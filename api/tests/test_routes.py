"""
Tests for health data routes.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from datetime import datetime


class TestHealthRoutes:
    """Test health data endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient, mock_oauth_manager):
        """Test health check endpoint."""
        with patch("src.main.oauth_manager", mock_oauth_manager):
            mock_oauth_manager.is_authenticated = AsyncMock(return_value=False)
            
            response = await client.get("/api/v1/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert "version" in data
    
    @pytest.mark.asyncio
    async def test_get_steps(self, client: AsyncClient, mock_huawei_api_response):
        """Test getting steps data."""
        mock_client = AsyncMock()
        mock_client.get_steps = AsyncMock(return_value=mock_huawei_api_response)
        
        with patch("src.main.huawei_client", mock_client):
            response = await client.get("/api/v1/steps?date=2026-03-27")
            
            assert response.status_code == 200
            data = response.json()
            assert data["date"] == "2026-03-27"
            assert "steps" in data
            assert "distance_meters" in data
            assert "calories" in data
    
    @pytest.mark.asyncio
    async def test_get_steps_default_date(self, client: AsyncClient, mock_huawei_api_response):
        """Test getting steps data without date (defaults to today)."""
        mock_client = AsyncMock()
        mock_client.get_steps = AsyncMock(return_value=mock_huawei_api_response)
        
        with patch("src.main.huawei_client", mock_client):
            response = await client.get("/api/v1/steps")
            
            assert response.status_code == 200
            data = response.json()
            assert "date" in data
    
    @pytest.mark.asyncio
    async def test_get_heart_rate(self, client: AsyncClient, mock_huawei_heart_rate_response):
        """Test getting heart rate data."""
        mock_response = {
            "instantaneous": mock_huawei_heart_rate_response,
            "continuous": None
        }
        
        mock_client = AsyncMock()
        mock_client.get_heart_rate = AsyncMock(return_value=mock_response)
        
        with patch("src.main.huawei_client", mock_client):
            response = await client.get("/api/v1/heart-rate?date=2026-03-27&type=all")
            
            assert response.status_code == 200
            data = response.json()
            assert data["date"] == "2026-03-27"
            assert "data" in data
    
    @pytest.mark.asyncio
    async def test_get_sleep(self, client: AsyncClient, mock_huawei_sleep_response):
        """Test getting sleep data."""
        mock_client = AsyncMock()
        mock_client.get_sleep = AsyncMock(return_value=mock_huawei_sleep_response)
        
        with patch("src.main.huawei_client", mock_client):
            response = await client.get("/api/v1/sleep?date=2026-03-27")
            
            assert response.status_code == 200
            data = response.json()
            assert data["date"] == "2026-03-27"
            assert "phases" in data
            assert "score" in data
    
    @pytest.mark.asyncio
    async def test_get_spo2(self, client: AsyncClient):
        """Test getting SpO2 data."""
        mock_response = {
            "continuous": {"dataPoints": [{"startTime": "2026-03-27T08:00:00Z", "value": 98.5}]},
            "instantaneous": {"dataPoints": [{"startTime": "2026-03-27T09:00:00Z", "value": 97.0}]}
        }
        
        mock_client = AsyncMock()
        mock_client.get_spo2 = AsyncMock(return_value=mock_response)
        
        with patch("src.main.huawei_client", mock_client):
            response = await client.get("/api/v1/spo2?date=2026-03-27")
            
            assert response.status_code == 200
            data = response.json()
            assert data["date"] == "2026-03-27"
            assert "data" in data
    
    @pytest.mark.asyncio
    async def test_get_stress(self, client: AsyncClient):
        """Test getting stress data."""
        mock_response = {
            "dataPoints": [
                {"startTime": "2026-03-27T08:00:00Z", "value": 25},
                {"startTime": "2026-03-27T12:00:00Z", "value": 45}
            ]
        }
        
        mock_client = AsyncMock()
        mock_client.get_stress = AsyncMock(return_value=mock_response)
        
        with patch("src.main.huawei_client", mock_client):
            response = await client.get("/api/v1/stress?date=2026-03-27")
            
            assert response.status_code == 200
            data = response.json()
            assert data["date"] == "2026-03-27"
            assert "data" in data
            # Check stress descriptions are added
            for point in data["data"]:
                assert "description" in point
                assert point["description"] in ["relaxed", "normal", "moderate", "high", "very_high"]
    
    @pytest.mark.asyncio
    async def test_get_temperature(self, client: AsyncClient):
        """Test getting temperature data."""
        mock_response = {
            "dataPoints": [
                {"startTime": "2026-03-27T08:00:00Z", "value": 36.5},
                {"startTime": "2026-03-27T12:00:00Z", "value": 36.8}
            ]
        }
        
        mock_client = AsyncMock()
        mock_client.get_temperature = AsyncMock(return_value=mock_response)
        
        with patch("src.main.huawei_client", mock_client):
            response = await client.get("/api/v1/temperature?date=2026-03-27")
            
            assert response.status_code == 200
            data = response.json()
            assert data["date"] == "2026-03-27"
            assert "data" in data
    
    @pytest.mark.asyncio
    async def test_get_ecg(self, client: AsyncClient):
        """Test getting ECG data."""
        mock_response = {
            "dataPoints": [
                {"startTime": "2026-03-27T08:00:00Z", "result": 1, "heartRate": 72}
            ]
        }
        
        mock_client = AsyncMock()
        mock_client.get_ecg = AsyncMock(return_value=mock_response)
        
        with patch("src.main.huawei_client", mock_client):
            response = await client.get("/api/v1/ecg?date=2026-03-27")
            
            assert response.status_code == 200
            data = response.json()
            assert data["date"] == "2026-03-27"
            assert "data" in data
    
    @pytest.mark.asyncio
    async def test_get_workouts(self, client: AsyncClient):
        """Test getting workout history."""
        mock_response = {
            "workouts": [
                {
                    "id": "workout-123",
                    "type": "running",
                    "startTime": "2026-03-27T08:00:00Z",
                    "endTime": "2026-03-27T09:00:00Z",
                    "duration": 60,
                    "calories": 500,
                    "heartRateAvg": 140,
                    "heartRateMax": 165,
                    "distance": 8000
                }
            ]
        }
        
        mock_client = AsyncMock()
        mock_client.get_workouts = AsyncMock(return_value=mock_response)
        
        with patch("src.main.huawei_client", mock_client):
            response = await client.get("/api/v1/workouts?date=2026-03-27&limit=10")
            
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "count" in data
    
    @pytest.mark.asyncio
    async def test_get_health_summary(self, client: AsyncClient, mock_huawei_api_response, mock_huawei_heart_rate_response):
        """Test getting health summary."""
        mock_summary = {
            "steps": mock_huawei_api_response,
            "heart_rate": {"instantaneous": mock_huawei_heart_rate_response, "continuous": None},
            "sleep": None,
            "spo2": None,
            "stress": None,
            "temperature": None
        }
        
        mock_client = AsyncMock()
        mock_client.get_health_summary = AsyncMock(return_value=mock_summary)
        
        with patch("src.main.huawei_client", mock_client):
            response = await client.get("/api/v1/summary?date=2026-03-27")
            
            assert response.status_code == 200
            data = response.json()
            assert data["date"] == "2026-03-27"
            assert "heart_rate_avg" in data
            assert "steps" in data
