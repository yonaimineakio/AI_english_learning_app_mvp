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


@router.post("/webhooks/revenuecat", dependencies=[Depends(verify_revenuecat_webhook)])
async def process_revenuecat_webhook(request: Request, db: Session = Depends(get_db)):
    logger.info("RevenueCat webhook started")
    payload = await request.json()
    event = payload.get("event", {})
    app_user_id = event.get("app_user_id")
    # RevenueCatでは "type" フィールドを使用
    event_type = (event.get("type") or "").upper()

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
    elif event_type in {"CANCELLED", "EXPIRED", "EXPIRATION"}:
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
