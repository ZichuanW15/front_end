"""
Assets API endpoints
"""

from flask import Blueprint, request
from app.models import Asset, ValueHistory, Fraction, Ownership
from app.utils import get_asset_current_value, get_ownership_snapshot, validate_date_format
from app.api.errors import NotFoundError, ValidationError, success_response
from app.api.decorators import handle_exceptions, paginate
from app import db
from datetime import datetime

bp = Blueprint('assets', __name__, url_prefix='/assets')


@bp.route('/', methods=['GET'])
@handle_exceptions
@paginate(page=1, per_page=20)
def get_assets(page=1, per_page=20):
    """
    Get all assets with pagination
    GET /api/v1/assets?page=1&per_page=20
    """
    assets = Asset.query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    assets_data = []
    for asset in assets.items:
        asset_dict = asset.to_dict()
        asset_dict['current_value'] = get_asset_current_value(asset.asset_id)
        assets_data.append(asset_dict)
    
    return success_response(
        data={
            'assets': assets_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': assets.total,
                'pages': assets.pages,
                'has_next': assets.has_next,
                'has_prev': assets.has_prev
            }
        },
        message="Assets retrieved successfully"
    )


@bp.route('/<int:asset_id>', methods=['GET'])
@handle_exceptions
def get_asset(asset_id):
    """
    Get current asset info and value
    GET /api/v1/assets/<asset_id>
    """
    asset = Asset.query.get(asset_id)
    
    if not asset:
        raise NotFoundError("Asset not found")
    
    # Get current asset value
    current_value = get_asset_current_value(asset_id)
    
    # Get current fraction value
    from app.utils import calculate_fraction_value
    fraction_value = calculate_fraction_value(asset_id)
    
    asset_data = asset.to_dict()
    asset_data['current_value'] = current_value
    asset_data['fraction_value'] = float(fraction_value)
    
    return success_response(
        data=asset_data,
        message="Asset retrieved successfully"
    )


@bp.route('/<int:asset_id>/history', methods=['GET'])
@handle_exceptions
@paginate(page=1, per_page=50)
def get_asset_history(asset_id, page=1, per_page=50):
    """
    Get historical asset value records
    GET /api/v1/assets/<asset_id>/history?page=1&per_page=50
    """
    # Verify asset exists
    asset = Asset.query.get(asset_id)
    if not asset:
        raise NotFoundError("Asset not found")
    
    # Get value history with pagination
    history = ValueHistory.query.filter_by(assets_asset_id=asset_id)\
        .order_by(ValueHistory.update_time.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    history_data = [record.to_dict() for record in history.items]
    
    return success_response(
        data={
            'asset_id': asset_id,
            'history': history_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': history.total,
                'pages': history.pages,
                'has_next': history.has_next,
                'has_prev': history.has_prev
            }
        },
        message="Asset history retrieved successfully"
    )


@bp.route('/<int:asset_id>/snapshot', methods=['GET'])
@handle_exceptions
def get_asset_snapshot(asset_id):
    """
    Get ownership snapshot at a specific time
    GET /api/v1/assets/<asset_id>/snapshot?at=YYYY-MM-DD
    """
    # Verify asset exists
    asset = Asset.query.get(asset_id)
    if not asset:
        raise NotFoundError("Asset not found")
    
    # Get date parameter
    date_str = request.args.get('at')
    if not date_str:
        raise ValidationError("Date parameter 'at' is required (format: YYYY-MM-DD)")
    
    # Validate date format
    if not validate_date_format(date_str):
        raise ValidationError("Invalid date format. Use YYYY-MM-DD")
    
    try:
        snapshot_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError("Invalid date format. Use YYYY-MM-DD")
    
    # Get ownership snapshot
    snapshot = get_ownership_snapshot(asset_id, snapshot_date)
    
    return success_response(
        data={
            'asset_id': asset_id,
            'date': date_str,
            'snapshot': snapshot
        },
        message="Ownership snapshot retrieved successfully"
    )


@bp.route('/<int:asset_id>/fractions', methods=['GET'])
@handle_exceptions
def get_asset_fractions(asset_id):
    """
    Get all fractions for an asset
    GET /api/v1/assets/<asset_id>/fractions
    """
    # Verify asset exists
    asset = Asset.query.get(asset_id)
    if not asset:
        raise NotFoundError("Asset not found")
    
    # Get fractions for this asset
    fractions = Fraction.query.filter_by(assets_asset_id=asset_id).all()
    fractions_data = [fraction.to_dict() for fraction in fractions]
    
    return success_response(
        data={
            'asset_id': asset_id,
            'fractions': fractions_data
        },
        message="Asset fractions retrieved successfully"
    )