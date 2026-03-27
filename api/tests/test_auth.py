"""
Tests for authentication routes.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

from src.auth import OAuthError, TokenData


class TestAuthRoutes:
    """Test authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_authorize_url(self, client: AsyncClient):
        """Test getting authorization URL."""
        response = await client.get("/api/v1/auth/authorize")
        
        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "oauth-login.cloud.huawei.com" in data["authorization_url"]
    
    @pytest.mark.asyncio
    async def test_get_authorize_url_with_state(self, client: AsyncClient):
        """Test getting authorization URL with state parameter."""
        response = await client.get("/api/v1/auth/authorize?state=random_state_123")
        
        assert response.status_code == 200
        data = response.json()
        assert "state=random_state_123" in data["authorization_url"]
    
    @pytest.mark.asyncio
    async def test_oauth_callback_error(self, client: AsyncClient):
        """Test OAuth callback with error."""
        response = await client.get(
            "/api/v1/auth/callback?error=access_denied&error_description=User%20denied%20access"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_oauth_callback_success(self, client: AsyncClient, mock_oauth_manager):
        """Test successful OAuth callback."""
        mock_token = MagicMock()
        mock_token.token_type = "Bearer"
        mock_token.expires_in = 3600
        
        with patch("src.main.oauth_manager", mock_oauth_manager):
            mock_oauth_manager.exchange_code_for_token = AsyncMock(return_value=mock_token)
            
            response = await client.get("/api/v1/auth/callback?code=test_auth_code")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_oauth_callback_post(self, client: AsyncClient, mock_oauth_manager):
        """Test OAuth callback via POST."""
        mock_token = MagicMock()
        mock_token.token_type = "Bearer"
        mock_token.expires_in = 3600
        
        with patch("src.main.oauth_manager", mock_oauth_manager):
            mock_oauth_manager.exchange_code_for_token = AsyncMock(return_value=mock_token)
            
            response = await client.post(
                "/api/v1/auth/callback",
                json={"code": "test_auth_code"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, mock_oauth_manager):
        """Test token refresh."""
        mock_token = MagicMock()
        mock_token.token_type = "Bearer"
        mock_token.expires_in = 3600
        
        with patch("src.main.oauth_manager", mock_oauth_manager):
            mock_oauth_manager.refresh_access_token = AsyncMock(return_value=mock_token)
            
            response = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "test_refresh_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_auth_status_unauthenticated(self, client: AsyncClient, mock_oauth_manager):
        """Test auth status when not authenticated."""
        with patch("src.main.oauth_manager", mock_oauth_manager):
            mock_oauth_manager.is_authenticated = AsyncMock(return_value=False)
            
            response = await client.get("/api/v1/auth/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["authenticated"] is False
    
    @pytest.mark.asyncio
    async def test_logout(self, client: AsyncClient, mock_oauth_manager):
        """Test logout endpoint."""
        with patch("src.main.oauth_manager", mock_oauth_manager):
            mock_oauth_manager.logout = AsyncMock()
            
            response = await client.post("/api/v1/auth/logout")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
