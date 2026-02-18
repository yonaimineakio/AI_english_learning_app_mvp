from __future__ import annotations
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.services.subscription.subscription_service import SubscriptionService
from app.core.deps import verify_revenuecat_webhook
from app.core.logging_config import get_logger
from fastapi.responses import JSONResponse

router = APIRouter()
logger = get_logger(__name__)


def _get_str(obj: dict, *keys: str) -> str | None:
    """Get first present string value from dict by snake_case or camelCase keys."""
    for k in keys:
        v = obj.get(k)
        if v is not None and isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _app_user_id_from_payload(payload: dict) -> str | None:
    """Extract app_user_id from RevenueCat webhook payload.
    RevenueCat sends event under "event" key; field may be app_user_id or appUserId.
    See: https://www.revenuecat.com/docs/integrations/webhooks/event-types-and-fields
    """
    event = payload.get("event") or {}
    if not isinstance(event, dict):
        event = {}
    # event may wrap data in a "data" key in some API versions
    event_data = event.get("data") or event.get("event") or event

    for source in (event_data, event, payload):
        if not isinstance(source, dict):
            continue
        app_user_id = _get_str(source, "app_user_id", "appUserId")
        if app_user_id:
            return app_user_id
        original = _get_str(source, "original_app_user_id", "originalAppUserId")
        if original:
            return original

    aliases = (
        event_data.get("aliases")
        or event_data.get("Aliases")
        or event.get("aliases")
        or event.get("Aliases")
        or payload.get("aliases")
        or []
    )
    if isinstance(aliases, list) and aliases:
        first = aliases[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict):
            return _get_str(first, "app_user_id", "appUserId")
    return None


@router.post("/webhooks/revenuecat", dependencies=[Depends(verify_revenuecat_webhook)])
async def process_revenuecat_webhook(request: Request, db: Session = Depends(get_db)):
    logger.info("RevenueCat webhook started")
    payload = await request.json()
    event = payload.get("event") or payload
    if not isinstance(event, dict):
        event = {}
    event_data = event.get("data") or event.get("event") or event
    if not isinstance(event_data, dict):
        event_data = event
    app_user_id = _app_user_id_from_payload(payload)
    event_type = (
        event_data.get("type")
        or event.get("type")
        or payload.get("type")
        or ""
    ).upper()

    if not app_user_id:
        event = payload.get("event") or {}
        logger.warning(
            "RevenueCat webhook missing app_user_id; payload keys=%s, event keys=%s",
            list(payload.keys()),
            list(event.keys()) if isinstance(event, dict) else type(event).__name__,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Missing app_user_id in webhook payload"},
        )

    subscription_service = SubscriptionService(db)
    user = subscription_service.get_user_by_app_user_id(app_user_id)
    if not user:
        logger.warning(f"User with app_user_id {app_user_id} not found")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": "User not found"}
        )

    if event_type in {"INITIAL_PURCHASE", "RENEWAL", "UNCANCELLATION"}:
        subscription_service.update_user_subscription(user.id, is_pro=True)
        logger.info(f"User {user.id} subscribed to Pro")
    elif event_type in {"CANCELLATION", "CANCELLED", "EXPIRATION", "EXPIRED"}:
        subscription_service.update_user_subscription(user.id, is_pro=False)
        logger.info(f"User {user.id} unsubscribed from Pro")
    else:
        logger.warning(f"Unknown event type: {event_type}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Unknown event type"},
        )

    logger.info(f"RevenueCat webhook completed: {request}")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Webhook processed successfully"},
    )
