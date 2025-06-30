"""
Authentication utilities for the MentraOS Python SDK

Provides JWT token creation/validation and FastAPI middleware for
webview authentication, similar to the TypeScript SDK's auth module.
"""

import jwt
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
import httpx

from fastapi import HTTPException, Request, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .logger import get_logger

logger = get_logger(__name__)

# JWT token handling
class TokenManager:
    """Manages JWT token creation and validation"""

    @staticmethod
    def create_token(
        payload: Dict[str, Any],
        secret_key: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT token

        Args:
            payload: Token payload data
            secret_key: Secret key for signing
            expires_delta: Token expiration time (default: 5 minutes)

        Returns:
            Encoded JWT token string
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=5)

        to_encode = payload.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc)
        })

        return jwt.encode(to_encode, secret_key, algorithm="HS256")

    @staticmethod
    def validate_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate and decode a JWT token

        Args:
            token: JWT token string
            secret_key: Secret key for verification

        Returns:
            Decoded payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload
        except jwt.PyJWTError as e:
            logger.warning("Token validation failed", error=str(e))
            return None


def extract_temp_token(url: str) -> Optional[str]:
    """
    Extract temporary token from URL

    Args:
        url: URL that may contain aos_temp_token parameter

    Returns:
        Token if found, None otherwise
    """
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        tokens = query_params.get('aos_temp_token', [])
        return tokens[0] if tokens else None
    except Exception as e:
        logger.warning("Failed to extract temp token from URL", error=str(e))
        return None


async def exchange_token(
    cloud_api_url: str,
    temp_token: str,
    api_key: str,
    package_name: str
) -> Optional[str]:
    """
    Exchange temporary token for user ID

    Args:
        cloud_api_url: MentraOS Cloud API URL
        temp_token: Temporary token from URL
        api_key: App API key
        package_name: App package name

    Returns:
        User ID if successful, None if failed
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{cloud_api_url}/auth/exchange-token",
                json={
                    "temp_token": temp_token,
                    "api_key": api_key,
                    "package_name": package_name
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("user_id")
            else:
                logger.warning(
                    "Token exchange failed",
                    status_code=response.status_code,
                    response=response.text
                )
                return None

    except Exception as e:
        logger.error("Token exchange error", error=str(e))
        return None


def sign_session(user_id: str, secret: str) -> str:
    """
    Sign a session cookie with user ID

    Args:
        user_id: User identifier
        secret: Signing secret

    Returns:
        Signed session token
    """
    return TokenManager.create_token(
        {"user_id": user_id},
        secret,
        expires_delta=timedelta(days=7)  # Session cookies last longer
    )


def verify_session(
    token: str,
    secret: str,
    max_age_seconds: Optional[int] = None
) -> Optional[str]:
    """
    Verify a session token and extract user ID

    Args:
        token: Session token
        secret: Signing secret
        max_age_seconds: Maximum age in seconds (optional)

    Returns:
        User ID if valid, None if invalid
    """
    payload = TokenManager.validate_token(token, secret)
    if not payload:
        return None

    # Check max age if specified
    if max_age_seconds:
        iat = payload.get("iat")
        if iat:
            issued_at = datetime.fromtimestamp(iat, tz=timezone.utc)
            if datetime.now(timezone.utc) - issued_at > timedelta(seconds=max_age_seconds):
                return None

    return payload.get("user_id")


def validate_cloud_api_url_checksum(
    checksum: str,
    cloud_api_url: str,
    api_key: str
) -> bool:
    """
    Validate cloud API URL checksum for security

    Args:
        checksum: Provided checksum
        cloud_api_url: Cloud API URL
        api_key: App API key

    Returns:
        True if valid, False otherwise
    """
    expected = hmac.new(
        api_key.encode(),
        cloud_api_url.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(checksum, expected)


# FastAPI Dependencies and Middleware

class AuthConfig:
    """Configuration for authentication middleware"""

    def __init__(
        self,
        api_key: str,
        package_name: str,
        cookie_secret: Optional[str] = None,
        cookie_name: str = "aos_session",
        cookie_max_age: int = 7 * 24 * 3600,  # 7 days
        require_https: bool = True
    ):
        self.api_key = api_key
        self.package_name = package_name
        self.cookie_secret = cookie_secret or f"AOS_{package_name}_{api_key[:8]}"
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.require_https = require_https


def create_auth_dependency(config: AuthConfig):
    """
    Create a FastAPI dependency for authentication

    Args:
        config: Authentication configuration

    Returns:
        FastAPI dependency function
    """
    security = HTTPBearer(auto_error=False)

    async def authenticate(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[str]:
        """
        Authenticate request and return user ID

        Returns:
            User ID if authenticated, None otherwise
        """
        # Check for session cookie first
        session_cookie = request.cookies.get(config.cookie_name)
        if session_cookie:
            user_id = verify_session(session_cookie, config.cookie_secret)
            if user_id:
                return user_id

        # Check for temporary token in query parameters
        temp_token = request.query_params.get("aos_temp_token")
        if temp_token:
            # Extract cloud API URL and checksum for validation
            cloud_api_url = request.query_params.get("cloud_api_url")
            checksum = request.query_params.get("checksum")

            if cloud_api_url and checksum:
                if validate_cloud_api_url_checksum(checksum, cloud_api_url, config.api_key):
                    user_id = await exchange_token(
                        cloud_api_url,
                        temp_token,
                        config.api_key,
                        config.package_name
                    )
                    if user_id:
                        # Set session cookie for future requests
                        session_token = sign_session(user_id, config.cookie_secret)
                        # Note: FastAPI dependencies can't set cookies directly
                        # The route handler needs to set the cookie
                        request.state.set_session_cookie = (config.cookie_name, session_token)
                        return user_id

        # Check for Bearer token
        if credentials:
            # This could be used for API authentication
            # Validate the bearer token against your auth system
            pass

        return None

    return authenticate


def create_required_auth_dependency(config: AuthConfig):
    """
    Create a FastAPI dependency that requires authentication

    Args:
        config: Authentication configuration

    Returns:
        FastAPI dependency function that raises 401 if not authenticated
    """
    auth_dependency = create_auth_dependency(config)

    async def require_auth(user_id: Optional[str] = Depends(auth_dependency)) -> str:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        return user_id

    return require_auth


# Utility functions for webview URL generation

def generate_webview_url(base_url: str, token: str) -> str:
    """
    Generate a webview URL with embedded token

    Args:
        base_url: Base URL for the webview
        token: Authentication token

    Returns:
        Complete webview URL
    """
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}aos_temp_token={token}"


def extract_token_from_url(url: str) -> Optional[str]:
    """
    Extract token from a webview URL

    Args:
        url: URL that may contain a token

    Returns:
        Token if found, None otherwise
    """
    return extract_temp_token(url)