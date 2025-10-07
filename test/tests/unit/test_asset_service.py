"""
Unit tests for AssetService.
Tests are isolated and do not rely on external calls.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.services.asset_service import AssetService
from app.models import Asset, User


class TestAssetService:
    """Test cases for AssetService."""
    
    def test_create_asset_success(self):
        """Test successful asset creation."""
        asset_data = {
            'asset_name': 'Test Asset',
            'asset_description': 'Test Description',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 100,
            'total_value': '10000.00'
        }
        
        with patch('app.services.asset_service.db') as mock_db:
            mock_asset = Mock(spec=Asset)
            mock_db.session.add.return_value = None
            mock_db.session.commit.return_value = None
            
            # Mock the Asset constructor to return our mock
            with patch('app.services.asset_service.Asset', return_value=mock_asset):
                result = AssetService.create_asset(asset_data)
                
                assert result == mock_asset
                mock_db.session.add.assert_called_once()
                mock_db.session.commit.assert_called_once()
    
    def test_create_asset_missing_required_field(self):
        """Test asset creation with missing required field."""
        asset_data = {
            'asset_name': 'Test Asset',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 100
            # Missing 'total_value'
        }
        
        with pytest.raises(ValueError, match="Missing required field: total_value"):
            AssetService.create_asset(asset_data)
    
    def test_create_asset_none_value(self):
        """Test asset creation with None value for required field."""
        asset_data = {
            'asset_name': 'Test Asset',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 100,
            'total_value': None
        }
        
        with pytest.raises(ValueError, match="Missing required field: total_value"):
            AssetService.create_asset(asset_data)
    
    def test_create_asset_unit_min_less_than_one(self):
        """Test asset creation with unit_min < 1."""
        asset_data = {
            'asset_name': 'Test Asset',
            'total_unit': 1000,
            'unit_min': 0,  # Invalid: less than 1
            'unit_max': 100,
            'total_value': '10000.00'
        }
        
        with pytest.raises(ValueError, match="unit_min must be at least 1"):
            AssetService.create_asset(asset_data)
    
    def test_create_asset_unit_min_greater_than_max(self):
        """Test asset creation with unit_min > unit_max."""
        asset_data = {
            'asset_name': 'Test Asset',
            'total_unit': 1000,
            'unit_min': 100,
            'unit_max': 50,  # max < min
            'total_value': '10000.00'
        }
        
        with pytest.raises(ValueError, match="unit_max cannot be less than unit_min"):
            AssetService.create_asset(asset_data)
    
    def test_create_asset_total_unit_less_than_min(self):
        """Test asset creation with total_unit < unit_min."""
        asset_data = {
            'asset_name': 'Test Asset',
            'total_unit': 50,
            'unit_min': 100,
            'unit_max': 200,
            'total_value': '10000.00'
        }
        
        with pytest.raises(ValueError, match="unit_min cannot be greater than total_unit"):
            AssetService.create_asset(asset_data)
    
    def test_create_asset_unit_max_greater_than_total(self):
        """Test asset creation with unit_max > total_unit - this should be ALLOWED."""
        asset_data = {
            'asset_name': 'Test Asset',
            'total_unit': 100,
            'unit_min': 1,
            'unit_max': 200,  # max > total is allowed
            'total_value': '10000.00'
        }
        
        # This should succeed - unit_max can be greater than total_unit
        with patch('app.services.asset_service.db') as mock_db:
            mock_asset = Mock(spec=Asset)
            mock_db.session.add.return_value = None
            mock_db.session.commit.return_value = None
            
            with patch('app.services.asset_service.Asset', return_value=mock_asset):
                result = AssetService.create_asset(asset_data)
                
                assert result == mock_asset
                mock_db.session.add.assert_called_once()
                mock_db.session.commit.assert_called_once()
    
    def test_create_asset_with_initial_fraction_success(self):
        """Test successful asset creation with initial fraction."""
        asset_data = {
            'asset_name': 'Test Asset',
            'asset_description': 'Test Description',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 100,
            'total_value': '10000.00'
        }
        owner_id = 1
        admin_user_id = 2
        
        with patch('app.services.asset_service.db') as mock_db:
            # Mock User query
            mock_owner = Mock(spec=User)
            mock_owner.user_id = owner_id
            
            mock_admin = Mock(spec=User)
            mock_admin.user_id = admin_user_id
            mock_admin.is_manager = True
            
            with patch('app.services.asset_service.User') as mock_user_class:
                mock_user_class.query.get.side_effect = lambda uid: mock_owner if uid == owner_id else mock_admin
                
                # Mock Asset creation
                mock_asset = Mock(spec=Asset)
                mock_asset.asset_id = 1
                mock_asset.total_unit = 1000
                
                with patch('app.services.asset_service.AssetService.create_asset', return_value=mock_asset):
                    with patch('app.services.asset_service.Fraction') as mock_fraction_class:
                        with patch('app.services.asset_service.AssetValueHistory') as mock_history_class:
                            mock_fraction = Mock()
                            mock_history = Mock()
                            
                            mock_fraction_class.return_value = mock_fraction
                            mock_history_class.return_value = mock_history
                            
                            result = AssetService.create_asset_with_initial_fraction(
                                asset_data, owner_id, admin_user_id
                            )
                            
                            assert 'asset' in result
                            assert 'fraction' in result
                            assert 'value_history' in result
                            assert result['asset'] == mock_asset
                            assert result['fraction'] == mock_fraction
                            assert result['value_history'] == mock_history
                            
                            # Verify database operations
                            assert mock_db.session.add.call_count == 2  # fraction + history
                            mock_db.session.commit.assert_called_once()
    
    def test_create_asset_with_initial_fraction_owner_not_found(self):
        """Test asset creation with non-existent owner."""
        asset_data = {
            'asset_name': 'Test Asset',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 100,
            'total_value': '10000.00'
        }
        owner_id = 999  # Non-existent
        admin_user_id = 2
        
        with patch('app.services.asset_service.User') as mock_user_class:
            mock_user_class.query.get.return_value = None
            
            with pytest.raises(ValueError, match="Owner user not found"):
                AssetService.create_asset_with_initial_fraction(asset_data, owner_id, admin_user_id)
    
    def test_create_asset_with_initial_fraction_admin_not_found(self):
        """Test asset creation with non-existent admin."""
        asset_data = {
            'asset_name': 'Test Asset',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 100,
            'total_value': '10000.00'
        }
        owner_id = 1
        admin_user_id = 999  # Non-existent
        
        with patch('app.services.asset_service.User') as mock_user_class:
            mock_owner = Mock(spec=User)
            mock_user_class.query.get.side_effect = lambda uid: mock_owner if uid == owner_id else None
            
            with pytest.raises(ValueError, match="Admin user not found"):
                AssetService.create_asset_with_initial_fraction(asset_data, owner_id, admin_user_id)
    
    def test_create_asset_with_initial_fraction_non_manager_admin(self):
        """Test asset creation with non-manager admin."""
        asset_data = {
            'asset_name': 'Test Asset',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 100,
            'total_value': '10000.00'
        }
        owner_id = 1
        admin_user_id = 2
        
        with patch('app.services.asset_service.User') as mock_user_class:
            mock_owner = Mock(spec=User)
            mock_admin = Mock(spec=User)
            mock_admin.is_manager = False  # Not a manager
            
            mock_user_class.query.get.side_effect = lambda uid: mock_owner if uid == owner_id else mock_admin
            
            with pytest.raises(PermissionError, match="Only managers can create assets"):
                AssetService.create_asset_with_initial_fraction(asset_data, owner_id, admin_user_id)
    
    def test_create_asset_with_initial_fraction_rollback_on_failure(self):
        """Test that asset creation is rolled back if fraction/history creation fails."""
        asset_data = {
            'asset_name': 'Test Asset',
            'total_unit': 1000,
            'unit_min': 1,
            'unit_max': 100,
            'total_value': '10000.00'
        }
        owner_id = 1
        admin_user_id = 2
        
        with patch('app.services.asset_service.db') as mock_db:
            # Mock User query
            mock_owner = Mock(spec=User)
            mock_admin = Mock(spec=User)
            mock_admin.is_manager = True
            
            with patch('app.services.asset_service.User') as mock_user_class:
                mock_user_class.query.get.side_effect = lambda uid: mock_owner if uid == owner_id else mock_admin
                
                # Mock Asset creation
                mock_asset = Mock(spec=Asset)
                mock_asset.asset_id = 1
                mock_asset.total_unit = 1000
                
                with patch('app.services.asset_service.AssetService.create_asset', return_value=mock_asset):
                    # Simulate failure during fraction/history creation
                    mock_db.session.add.side_effect = Exception("Database error")
                    
                    with pytest.raises(ValueError, match="Failed to create initial fraction or value history"):
                        AssetService.create_asset_with_initial_fraction(asset_data, owner_id, admin_user_id)
                    
                    # Verify rollback was called
                    mock_db.session.rollback.assert_called_once()
    
    def test_get_asset_by_id_success(self):
        """Test successful asset retrieval by ID."""
        asset_id = 1
        mock_asset = Mock(spec=Asset)
        
        with patch('app.services.asset_service.Asset') as mock_asset_class:
            mock_asset_class.query.get.return_value = mock_asset
            
            result = AssetService.get_asset_by_id(asset_id)
            
            assert result == mock_asset
            mock_asset_class.query.get.assert_called_once_with(asset_id)
    
    def test_get_asset_by_id_not_found(self):
        """Test asset retrieval with non-existent ID."""
        asset_id = 999
        
        with patch('app.services.asset_service.Asset') as mock_asset_class:
            mock_asset_class.query.get.return_value = None
            
            result = AssetService.get_asset_by_id(asset_id)
            
            assert result is None
            mock_asset_class.query.get.assert_called_once_with(asset_id)
    
    def test_get_all_assets_with_pagination(self):
        """Test asset retrieval with pagination."""
        page = 2
        per_page = 10
        mock_assets = [Mock(spec=Asset), Mock(spec=Asset)]
        
        with patch('app.services.asset_service.Asset') as mock_asset_class:
            mock_paginate = Mock()
            mock_paginate.items = mock_assets
            mock_asset_class.query.paginate.return_value = mock_paginate
            
            result = AssetService.get_all_assets(page, per_page)
            
            assert result == mock_assets
            mock_asset_class.query.paginate.assert_called_once_with(
                page=page, per_page=per_page, error_out=False
            )
    
    def test_update_asset_success(self):
        """Test successful asset update."""
        asset_id = 1
        asset_data = {'asset_name': 'Updated Asset'}
        mock_asset = Mock(spec=Asset)
        
        with patch('app.services.asset_service.Asset') as mock_asset_class:
            mock_asset_class.query.get.return_value = mock_asset
            
            with patch('app.services.asset_service.db') as mock_db:
                result = AssetService.update_asset(asset_id, asset_data)
                
                assert result == mock_asset
                assert mock_asset.asset_name == 'Updated Asset'
                mock_db.session.commit.assert_called_once()
    
    def test_update_asset_not_found(self):
        """Test asset update with non-existent ID."""
        asset_id = 999
        asset_data = {'asset_name': 'Updated Asset'}
        
        with patch('app.services.asset_service.Asset') as mock_asset_class:
            mock_asset_class.query.get.return_value = None
            
            result = AssetService.update_asset(asset_id, asset_data)
            
            assert result is None
    
    def test_delete_asset_success(self):
        """Test successful asset deletion."""
        asset_id = 1
        mock_asset = Mock(spec=Asset)
        
        with patch('app.services.asset_service.Asset') as mock_asset_class:
            mock_asset_class.query.get.return_value = mock_asset
            
            with patch('app.services.asset_service.db') as mock_db:
                result = AssetService.delete_asset(asset_id)
                
                assert result is True
                mock_db.session.delete.assert_called_once_with(mock_asset)
                mock_db.session.commit.assert_called_once()
    
    def test_delete_asset_not_found(self):
        """Test asset deletion with non-existent ID."""
        asset_id = 999
        
        with patch('app.services.asset_service.Asset') as mock_asset_class:
            mock_asset_class.query.get.return_value = None
            
            result = AssetService.delete_asset(asset_id)
            
            assert result is False
    
    def test_get_asset_fractions_success(self):
        """Test successful retrieval of asset fractions."""
        asset_id = 1
        mock_fractions = [Mock(), Mock()]
        mock_asset = Mock(spec=Asset)
        mock_asset.fractions = mock_fractions
        
        with patch('app.services.asset_service.Asset') as mock_asset_class:
            mock_asset_class.query.get.return_value = mock_asset
            
            result = AssetService.get_asset_fractions(asset_id)
            
            assert result == mock_fractions
    
    def test_get_asset_fractions_asset_not_found(self):
        """Test fraction retrieval for non-existent asset."""
        asset_id = 999
        
        with patch('app.services.asset_service.Asset') as mock_asset_class:
            mock_asset_class.query.get.return_value = None
            
            result = AssetService.get_asset_fractions(asset_id)
            
            assert result == []