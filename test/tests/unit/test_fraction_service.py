"""
Unit tests for FractionService.
Tests are isolated and do not rely on external calls.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.fraction_service import FractionService
from app.models import Fraction, Asset, User


class TestFractionService:
    """Test cases for FractionService."""
    
    def test_create_fraction_success(self):
        """Test successful fraction creation."""
        fraction_data = {
            'asset_id': 1,
            'owner_id': 2,
            'units': 50,
            'is_active': True,
            'value_perunit': 1000
        }
        
        mock_asset = Mock(spec=Asset)
        mock_asset.unit_min = 1
        mock_asset.unit_max = 100
        
        with patch('app.services.fraction_service.db') as mock_db:
            with patch('app.services.fraction_service.Asset') as mock_asset_class:
                mock_asset_class.query.get.return_value = mock_asset
                
                mock_fraction = Mock(spec=Fraction)
                with patch('app.services.fraction_service.Fraction', return_value=mock_fraction):
                    result = FractionService.create_fraction(fraction_data)
                    
                    assert result == mock_fraction
                    mock_db.session.add.assert_called_once()
                    mock_db.session.commit.assert_called_once()
    
    def test_create_fraction_missing_required_field(self):
        """Test fraction creation with missing required field."""
        fraction_data = {
            'asset_id': 1,
            'units': 50
            # Missing 'asset_id' or 'units' would be caught by the test
        }
        
        # Test missing asset_id
        fraction_data_no_asset = {'units': 50}
        with pytest.raises(ValueError, match="Missing required field: asset_id"):
            FractionService.create_fraction(fraction_data_no_asset)
        
        # Test missing units
        fraction_data_no_units = {'asset_id': 1}
        with pytest.raises(ValueError, match="Missing required field: units"):
            FractionService.create_fraction(fraction_data_no_units)
    
    def test_create_fraction_asset_not_found(self):
        """Test fraction creation with non-existent asset."""
        fraction_data = {
            'asset_id': 999,
            'units': 50
        }
        
        with patch('app.services.fraction_service.Asset') as mock_asset_class:
            mock_asset_class.query.get.return_value = None
            
            with pytest.raises(ValueError, match="Asset not found"):
                FractionService.create_fraction(fraction_data)
    
    def test_create_fraction_units_below_minimum(self):
        """Test fraction creation with units below asset minimum."""
        fraction_data = {
            'asset_id': 1,
            'units': 0  # Below minimum
        }
        
        mock_asset = Mock(spec=Asset)
        mock_asset.unit_min = 1
        mock_asset.unit_max = 100
        
        with patch('app.services.fraction_service.Asset') as mock_asset_class:
            mock_asset_class.query.get.return_value = mock_asset
            
            with pytest.raises(ValueError, match="Units must be between 1 and 100"):
                FractionService.create_fraction(fraction_data)
    
    def test_create_fraction_units_above_maximum(self):
        """Test fraction creation with units above asset maximum."""
        fraction_data = {
            'asset_id': 1,
            'units': 150  # Above maximum
        }
        
        mock_asset = Mock(spec=Asset)
        mock_asset.unit_min = 1
        mock_asset.unit_max = 100
        
        with patch('app.services.fraction_service.Asset') as mock_asset_class:
            mock_asset_class.query.get.return_value = mock_asset
            
            with pytest.raises(ValueError, match="Units must be between 1 and 100"):
                FractionService.create_fraction(fraction_data)
    
    def test_get_fraction_by_id_success(self):
        """Test successful fraction retrieval by ID."""
        fraction_id = 1
        mock_fraction = Mock(spec=Fraction)
        
        with patch('app.services.fraction_service.Fraction') as mock_fraction_class:
            mock_fraction_class.query.get.return_value = mock_fraction
            
            result = FractionService.get_fraction_by_id(fraction_id)
            
            assert result == mock_fraction
            mock_fraction_class.query.get.assert_called_once_with(fraction_id)
    
    def test_get_fraction_by_id_not_found(self):
        """Test fraction retrieval with non-existent ID."""
        fraction_id = 999
        
        with patch('app.services.fraction_service.Fraction') as mock_fraction_class:
            mock_fraction_class.query.get.return_value = None
            
            result = FractionService.get_fraction_by_id(fraction_id)
            
            assert result is None
            mock_fraction_class.query.get.assert_called_once_with(fraction_id)
    
    def test_get_fractions_by_owner(self):
        """Test retrieval of fractions by owner."""
        owner_id = 1
        mock_fractions = [Mock(spec=Fraction), Mock(spec=Fraction)]
        
        with patch('app.services.fraction_service.Fraction') as mock_fraction_class:
            mock_fraction_class.query.filter_by.return_value.all.return_value = mock_fractions
            
            result = FractionService.get_fractions_by_owner(owner_id)
            
            assert result == mock_fractions
            mock_fraction_class.query.filter_by.assert_called_once_with(owner_id=owner_id)
    
    def test_get_fractions_by_asset(self):
        """Test retrieval of fractions by asset."""
        asset_id = 1
        mock_fractions = [Mock(spec=Fraction), Mock(spec=Fraction)]
        
        with patch('app.services.fraction_service.Fraction') as mock_fraction_class:
            mock_fraction_class.query.filter_by.return_value.all.return_value = mock_fractions
            
            result = FractionService.get_fractions_by_asset(asset_id)
            
            assert result == mock_fractions
            mock_fraction_class.query.filter_by.assert_called_once_with(asset_id=asset_id)
    
    def test_update_fraction_success(self):
        """Test successful fraction update."""
        fraction_id = 1
        fraction_data = {'units': 75, 'is_active': False}
        mock_fraction = Mock(spec=Fraction)
        
        with patch('app.services.fraction_service.Fraction') as mock_fraction_class:
            mock_fraction_class.query.get.return_value = mock_fraction
            
            with patch('app.services.fraction_service.db') as mock_db:
                result = FractionService.update_fraction(fraction_id, fraction_data)
                
                assert result == mock_fraction
                assert mock_fraction.units == 75
                assert mock_fraction.is_active is False
                mock_db.session.commit.assert_called_once()
    
    def test_update_fraction_not_found(self):
        """Test fraction update with non-existent ID."""
        fraction_id = 999
        fraction_data = {'units': 75}
        
        with patch('app.services.fraction_service.Fraction') as mock_fraction_class:
            mock_fraction_class.query.get.return_value = None
            
            result = FractionService.update_fraction(fraction_id, fraction_data)
            
            assert result is None
    
    def test_delete_fraction_success(self):
        """Test successful fraction deletion."""
        fraction_id = 1
        mock_fraction = Mock(spec=Fraction)
        
        with patch('app.services.fraction_service.Fraction') as mock_fraction_class:
            mock_fraction_class.query.get.return_value = mock_fraction
            
            with patch('app.services.fraction_service.db') as mock_db:
                result = FractionService.delete_fraction(fraction_id)
                
                assert result is True
                mock_db.session.delete.assert_called_once_with(mock_fraction)
                mock_db.session.commit.assert_called_once()
    
    def test_delete_fraction_not_found(self):
        """Test fraction deletion with non-existent ID."""
        fraction_id = 999
        
        with patch('app.services.fraction_service.Fraction') as mock_fraction_class:
            mock_fraction_class.query.get.return_value = None
            
            result = FractionService.delete_fraction(fraction_id)
            
            assert result is False
    
    def test_get_active_fractions(self):
        """Test retrieval of active fractions."""
        mock_fractions = [Mock(spec=Fraction), Mock(spec=Fraction)]
        
        with patch('app.services.fraction_service.Fraction') as mock_fraction_class:
            mock_fraction_class.query.filter_by.return_value.all.return_value = mock_fractions
            
            result = FractionService.get_active_fractions()
            
            assert result == mock_fractions
            mock_fraction_class.query.filter_by.assert_called_once_with(is_active=True)