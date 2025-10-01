"""
Unit tests for AssetValueService.
Tests are isolated and do not rely on external calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.services.asset_value_service import AssetValueService
from app.models import AssetValueHistory, Asset, User


class TestAssetValueService:
    """Test cases for AssetValueService."""
    
    def test_list_history_success(self):
        """Test successful history listing."""
        asset_id = 1
        dt_from = datetime(2023, 1, 1)
        dt_to = datetime(2023, 12, 31)
        mock_history = [Mock(spec=AssetValueHistory), Mock(spec=AssetValueHistory)]
        
        with patch('app.services.asset_value_service.AssetValueHistory') as mock_history_class:
            # Mock the recorded_at field to avoid datetime comparison issues
            mock_recorded_at = Mock()
            mock_recorded_at.__ge__ = Mock(return_value=True)
            mock_recorded_at.__le__ = Mock(return_value=True)
            mock_history_class.recorded_at = mock_recorded_at
            
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value.all.return_value = mock_history
            mock_history_class.query = mock_query
            
            result = AssetValueService.list_history(asset_id, dt_from, dt_to)
            
            assert result == mock_history
            # Verify query chain was called correctly
            assert mock_query.filter.call_count >= 1  # At least asset_id filter
            mock_query.order_by.assert_called_once()
            mock_query.order_by.return_value.all.assert_called_once()
    
    def test_list_history_no_date_filters(self):
        """Test history listing without date filters."""
        asset_id = 1
        mock_history = [Mock(spec=AssetValueHistory)]
        
        with patch('app.services.asset_value_service.AssetValueHistory') as mock_history_class:
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value.all.return_value = mock_history
            mock_history_class.query = mock_query
            
            result = AssetValueService.list_history(asset_id)
            
            assert result == mock_history
    
    def test_add_adjustment_success(self):
        """Test successful value adjustment by manager."""
        asset_id = 1
        value = 15000.50
        adjusted_by = 2
        reason = "Market adjustment"
        recorded_at = datetime(2023, 6, 15, 10, 30, 0)
        
        mock_user = Mock(spec=User)
        mock_user.is_manager = True
        
        mock_asset = Mock(spec=Asset)
        mock_asset.asset_id = asset_id
        
        mock_history = Mock(spec=AssetValueHistory)
        
        with patch('app.services.asset_value_service.db') as mock_db:
            with patch('app.services.asset_value_service.User') as mock_user_class:
                mock_user_class.query.get.return_value = mock_user
                
                with patch('app.services.asset_value_service.Asset') as mock_asset_class:
                    mock_asset_class.query.get.return_value = mock_asset
                    
                    with patch('app.services.asset_value_service.AssetValueHistory', return_value=mock_history):
                        result = AssetValueService.add_adjustment(
                            asset_id, value, adjusted_by, reason, recorded_at
                        )
                        
                        assert result == mock_history
                        mock_db.session.add.assert_called_once()
                        mock_db.session.commit.assert_called_once()
                        
                        # Verify asset value was updated
                        assert mock_asset.total_value == str(value)
    
    def test_add_adjustment_user_not_found(self):
        """Test value adjustment with non-existent user."""
        asset_id = 1
        value = 15000.50
        adjusted_by = 999  # Non-existent user
        reason = "Market adjustment"
        
        with patch('app.services.asset_value_service.User') as mock_user_class:
            mock_user_class.query.get.return_value = None
            
            with pytest.raises(PermissionError, match="Only manager can adjust asset values"):
                AssetValueService.add_adjustment(asset_id, value, adjusted_by, reason)
    
    def test_add_adjustment_non_manager_user(self):
        """Test value adjustment by non-manager user."""
        asset_id = 1
        value = 15000.50
        adjusted_by = 2
        reason = "Market adjustment"
        
        mock_user = Mock(spec=User)
        mock_user.is_manager = False  # Not a manager
        
        with patch('app.services.asset_value_service.User') as mock_user_class:
            mock_user_class.query.get.return_value = mock_user
            
            with pytest.raises(PermissionError, match="Only manager can adjust asset values"):
                AssetValueService.add_adjustment(asset_id, value, adjusted_by, reason)
    
    def test_add_adjustment_asset_not_found(self):
        """Test value adjustment for non-existent asset."""
        asset_id = 999
        value = 15000.50
        adjusted_by = 2
        reason = "Market adjustment"
        
        mock_user = Mock(spec=User)
        mock_user.is_manager = True
        
        with patch('app.services.asset_value_service.User') as mock_user_class:
            mock_user_class.query.get.return_value = mock_user
            
            with patch('app.services.asset_value_service.Asset') as mock_asset_class:
                mock_asset_class.query.get.return_value = None  # Asset not found
                
                with patch('app.services.asset_value_service.AssetValueHistory'):
                    with patch('app.services.asset_value_service.db') as mock_db:
                        # Should not raise exception, just not update asset
                        result = AssetValueService.add_adjustment(asset_id, value, adjusted_by, reason)
                        
                        # History should still be created
                        mock_db.session.add.assert_called_once()
                        mock_db.session.commit.assert_called_once()
    
    def test_add_adjustment_default_values(self):
        """Test value adjustment with default values."""
        asset_id = 1
        value = 15000.50
        adjusted_by = 2
        
        mock_user = Mock(spec=User)
        mock_user.is_manager = True
        
        mock_asset = Mock(spec=Asset)
        mock_asset.asset_id = asset_id
        
        with patch('app.services.asset_value_service.db') as mock_db:
            with patch('app.services.asset_value_service.User') as mock_user_class:
                mock_user_class.query.get.return_value = mock_user
                
                with patch('app.services.asset_value_service.Asset') as mock_asset_class:
                    mock_asset_class.query.get.return_value = mock_asset
                    
                    with patch('app.services.asset_value_service.AssetValueHistory') as mock_history_class:
                        mock_history = Mock(spec=AssetValueHistory)
                        mock_history_class.return_value = mock_history
                        
                        # Mock datetime.utcnow() to return a specific time
                        with patch('app.services.asset_value_service.datetime') as mock_datetime:
                            mock_now = datetime(2023, 6, 15, 10, 30, 0)
                            mock_datetime.utcnow.return_value = mock_now
                            
                            result = AssetValueService.add_adjustment(asset_id, value, adjusted_by)
                            
                            # Verify AssetValueHistory was created with correct parameters
                            mock_history_class.assert_called_once()
                            call_args = mock_history_class.call_args
                            assert call_args[1]['asset_id'] == asset_id
                            assert call_args[1]['value'] == value
                            assert call_args[1]['recorded_at'] == mock_now
                            assert call_args[1]['source'] == "manual_adjust"
                            assert call_args[1]['adjusted_by'] == adjusted_by
                            assert call_args[1]['adjustment_reason'] == ""
    
    def test_latest_value_success(self):
        """Test successful latest value retrieval."""
        asset_id = 1
        mock_history = Mock(spec=AssetValueHistory)
        
        with patch('app.services.asset_value_service.AssetValueHistory') as mock_history_class:
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.order_by.return_value.first.return_value = mock_history
            mock_history_class.query = mock_query
            
            result = AssetValueService.latest_value(asset_id)
            
            assert result == mock_history
            mock_query.filter_by.assert_called_once_with(asset_id=asset_id)
            mock_query.order_by.assert_called_once()
            mock_query.order_by.return_value.first.assert_called_once()
    
    def test_latest_value_not_found(self):
        """Test latest value retrieval when no history exists."""
        asset_id = 1
        
        with patch('app.services.asset_value_service.AssetValueHistory') as mock_history_class:
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.order_by.return_value.first.return_value = None
            mock_history_class.query = mock_query
            
            result = AssetValueService.latest_value(asset_id)
            
            assert result is None
            mock_query.filter_by.assert_called_once_with(asset_id=asset_id)
            mock_query.order_by.assert_called_once()
            mock_query.order_by.return_value.first.assert_called_once()