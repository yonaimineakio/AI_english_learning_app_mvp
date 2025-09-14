import httpx
from typing import Optional, Dict, Any
from app.core.config import settings
import json


class Auth0Service:
    """Auth0 integration service"""
    
    def __init__(self):
        self.domain = settings.AUTH0_DOMAIN
        self.client_id = settings.AUTH0_CLIENT_ID
        self.client_secret = settings.AUTH0_CLIENT_SECRET
        self.audience = settings.AUTH0_AUDIENCE
        self.algorithm = settings.AUTH0_ALGORITHM
        self.jwks_url = f"https://{self.domain}/.well-known/jwks.json"
    
    async def get_jwks(self) -> Dict[str, Any]:
        """Get JSON Web Key Set from Auth0"""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url)
            response.raise_for_status()
            return response.json()
    
    async def verify_auth0_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Auth0 JWT token"""
        try:
            from jose import jwt
            from jose.backends import RSAKey
            import base64
            
            # Get JWKS
            jwks = await self.get_jwks()
            
            # Decode token header
            unverified_header = jwt.get_unverified_header(token)
            
            # Find the key
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
                    break
            
            if not rsa_key:
                return None
            
            # Create RSA key
            public_key = RSAKey(rsa_key, algorithm=unverified_header["alg"])
            
            # Verify token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=f"https://{self.domain}/"
            )
            
            return payload
            
        except Exception as e:
            print(f"Auth0 token verification failed: {e}")
            return None
    
    async def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Auth0"""
        try:
            userinfo_url = f"https://{self.domain}/userinfo"
            headers = {"Authorization": f"Bearer {token}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(userinfo_url, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            print(f"Failed to get user info from Auth0: {e}")
            return None


# Create global instance
auth0_service = Auth0Service()
