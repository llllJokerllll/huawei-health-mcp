"""
Tests for Huawei Health API client.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date

from src.huawei_client import HuaweiClient, HuaweiAPIError
from src.auth import OAuthManager, TokenData
from src.storage import Storage


class TestHuaweiClient:
    """Test Huawei API client."""
    
    @pytest.fixture
    def client(self, mock_storage):
        """Create Huawei client instance."""
        oauth = MagicMock(spec=OAuthManager)
        oauth.get_valid_token = AsyncMock(return_value=TokenData(
            access_token="test_token",
            refresh_token="test_refresh",
            expires_in=3600
        ))
        return HuaweiClient(oauth, mock_storage)
    
    @pytest.mark.asyncio
    async def test_get_steps(self, client: HuaweiClient):
        """Test getting steps data."""
        mock_response = {
            "polymerizeData": [{
                "dataTypeName": "com.huawei.continuous.steps.delta",
                "value": 10000,
                "distance": 8000.0,
                "calories": 400.0
            }]
        }
        
        with patch.object(client, '_polymerize_data', AsyncMock(return_value=mock_response)):
            result = await client.get_steps(date(2026, 3, 27))
            
            assert "polymerizeData" in result
            assert result["polymerizeData"][0]["value"] == 10000
    
    @pytest.mark.asyncio
    async def test_get_heart_rate(self, client: HuaweiClient):
        """Test getting heart rate data."""
        mock_response = {
            "dataPoints": [
                {"startTime": "2026-03-27T08:00:00Z", "value": 72}
            ]
        }
        
        with patch.object(client, '_read_data_records', AsyncMock(return_value=mock_response)):
            result = await client.get_heart_rate(date(2026, 3, 27), "instantaneous")
            
            assert "instantaneous" in result
            assert "dataPoints" in result["instantaneous"]
    
    @pytest.mark.asyncio
    async def test_get_sleep(self, client: HuaweiClient):
        """Test getting sleep data."""
        mock_response = {
            "sleepData": {
                "bedtime": "2026-03-26T23:00:00Z",
                "wakeup": "2026-03-27T07:00:00Z",
                "duration": 480,
                "score": 85
            }
        }
        
        with patch.object(client, '_read_data_records', AsyncMock(return_value=mock_response)):
            result = await client.get_sleep(date(2026, 3, 27))
            
            assert "sleepData" in result
    
    @pytest.mark.asyncio
    async def test_get_spo2(self, client: HuaweiClient):
        """Test getting SpO2 data."""
        mock_response = {
            "dataPoints": [
                {"startTime": "2026-03-27T08:00:00Z", "value": 98.5}
            ]
        }
        
        with patch.object(client, '_read_data_records', AsyncMock(return_value=mock_response)):
            result = await client.get_spo2(date(2026, 3, 27))
            
            assert "continuous" in result
            assert "instantaneous" in result
    
    @pytest.mark.asyncio
    async def test_get_stress(self, client: HuaweiClient):
        """Test getting stress data."""
        mock_response = {
            "dataPoints": [
                {"startTime": "2026-03-27T08:00:00Z", "value": 35}
            ]
        }
        
        with patch.object(client, '_read_data_records', AsyncMock(return_value=mock_response)):
            result = await client.get_stress(date(2026, 3, 27))
            
            assert "dataPoints" in result
    
    @pytest.mark.asyncio
    async def test_get_temperature(self, client: HuaweiClient):
        """Test getting temperature data."""
        mock_response = {
            "dataPoints": [
                {"startTime": "2026-03-27T08:00:00Z", "value": 36.5}
            ]
        }
        
        with patch.object(client, '_read_data_records', AsyncMock(return_value=mock_response)):
            result = await client.get_temperature(date(2026, 3, 27))
            
            assert "dataPoints" in result
    
    @pytest.mark.asyncio
    async def test_get_health_summary(self, client: HuaweiClient):
        """Test getting health summary aggregates all data."""
        with patch.object(client, 'get_steps', AsyncMock(return_value={"steps": 10000})), \
             patch.object(client, 'get_heart_rate', AsyncMock(return_value={"hr": 72})), \
             patch.object(client, 'get_sleep', AsyncMock(return_value={"sleep": "data"})), \
             patch.object(client, 'get_spo2', AsyncMock(return_value={"spo2": 98})), \
             patch.object(client, 'get_stress', AsyncMock(return_value={"stress": 35})), \
             patch.object(client, 'get_temperature', AsyncMock(return_value={"temp": 36.5})):
            
            result = await client.get_health_summary(date(2026, 3, 27))
            
            assert result["date"] == "2026-03-27"
            assert result["steps"] is not None
            assert result["heart_rate"] is not None
            assert result["sleep"] is not None
    
    @pytest.mark.asyncio
    async def test_caching(self, client: HuaweiClient, mock_storage):
        """Test that data is cached."""
        mock_response = {"data": "cached"}
        
        # First call should hit API
        with patch.object(client, '_polymerize_data', AsyncMock(return_value=mock_response)):
            result1 = await client.get_steps(date(2026, 3, 27))
            
            # Verify cache was set
            mock_storage.set_cached_data.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, client: HuaweiClient):
        """Test API error handling."""
        with patch.object(client, '_polymerize_data', AsyncMock(
            side_effect=HuaweiAPIError("API Error", status_code=500)
        )):
            with pytest.raises(HuaweiAPIError) as exc_info:
                await client.get_steps(date(2026, 3, 27))
            
            assert exc_info.value.status_code == 500
    
    @pytest.mark.asyncio
    async def test_unauthenticated_error(self, client: HuaweiClient):
        """Test error when not authenticated."""
        client.oauth.get_valid_token = AsyncMock(return_value=None)
        
        with pytest.raises(HuaweiAPIError) as exc_info:
            await client.get_steps(date(2026, 3, 27))
        
        assert exc_info.value.status_code == 401
        assert "Not authenticated" in str(exc_info.value)


class TestDataTypeNames:
    """Test Huawei data type name constants."""
    
    def test_data_type_names(self):
        """Verify all data type names are correct."""
        from src.huawei_client import HuaweiClient
        
        assert HuaweiClient.DATA_TYPES["steps"] == "com.huawei.continuous.steps.delta"
        assert HuaweiClient.DATA_TYPES["heart_rate_instant"] == "com.huawei.instantaneous.heart_rate"
        assert HuaweiClient.DATA_TYPES["heart_rate_continuous"] == "com.huawei.continuous.heart_rate.delta"
        assert HuaweiClient.DATA_TYPES["sleep"] == "com.huawei.sleep.detail"
        assert HuaweiClient.DATA_TYPES["spo2_continuous"] == "com.huawei.continuous.blood_oxygen"
        assert HuaweiClient.DATA_TYPES["spo2_instant"] == "com.huawei.instantaneous.blood_oxygen"
        assert HuaweiClient.DATA_TYPES["stress"] == "com.huawei.continuous.stress.delta"
        assert HuaweiClient.DATA_TYPES["temperature"] == "com.huawei.instantaneous.skin_temperature"
