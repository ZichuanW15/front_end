"""
Users/Owners API endpoints
"""

from flask import Blueprint, request
from app.models import User, Ownership, Fraction, Asset
from app.utils import get_ownership_snapshot, validate_date_format
from app.api.errors import NotFoundError, ValidationError, success_response
from app.api.decorators import handle_exceptions, paginate
from app import db
from datetime import datetime

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/', methods=['GET'])
@handle_exceptions
@paginate(page=1, per_page=20)
def get_users(page=1, per_page=20):
    """
    Get all users with pagination
    GET /api/v1/users?page=1&per_page=20
    """
    users = User.query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    users_data = [user.to_dict() for user in users.items]
    
    return success_response(
        data={
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        },
        message="Users retrieved successfully"
    )


@bp.route('/<int:user_id>', methods=['GET'])
@handle_exceptions
def get_user(user_id):
    """
    Get specific user by ID
    GET /api/v1/users/<user_id>
    """
    user = User.query.get(user_id)
    
    if not user:
        raise NotFoundError("User not found")
    
    return success_response(
        data=user.to_dict(),
        message="User retrieved successfully"
    )


@bp.route('/<int:user_id>/fractions', methods=['GET'])
@handle_exceptions
def get_user_fractions(user_id):
    """
    Get all current fractions owned by a user
    GET /api/v1/users/<user_id>/fractions
    """
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("User not found")
    
    # Get current ownership records
    ownerships = Ownership.query.filter_by(users_user_id=user_id).all()
    
    fractions_data = []
    for ownership in ownerships:
        fraction = Fraction.query.get(ownership.fractions_fraction_id)
        if fraction:
            asset = Asset.query.get(fraction.assets_asset_id)
            fraction_data = {
                'fraction_id': fraction.fraction_id,
                'asset_id': fraction.assets_asset_id,
                'asset_name': asset.name if asset else 'Unknown Asset',
                'fraction_number': fraction.fraction_no,
                'quantity_owned': 1,
                'purchase_date': ownership.acquired_at.isoformat() if ownership.acquired_at else None,
                'purchase_price': float(fraction.fraction_value) if fraction.fraction_value else None
            }
            fractions_data.append(fraction_data)
    
    return success_response(
        data={
            'user_id': user_id,
            'fractions': fractions_data
        },
        message="User fractions retrieved successfully"
    )


@bp.route('/<int:user_id>/fractions/history', methods=['GET'])
@handle_exceptions
def get_user_fractions_history(user_id):
    """
    Get fractions owned at a specific time by a user
    GET /api/v1/users/<user_id>/fractions/history?at=YYYY-MM-DD
    """
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("User not found")
    
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
    
    # Get ownership records up to the specified date
    ownerships = Ownership.query.filter(
        Ownership.user_id == user_id,
        Ownership.purchase_date <= snapshot_date
    ).all()
    
    fractions_data = []
    for ownership in ownerships:
        fraction = Fraction.query.get(ownership.fractions_fraction_id)
        if fraction:
            asset = Asset.query.get(fraction.assets_asset_id)
            fraction_data = {
                'fraction_id': fraction.fraction_id,
                'asset_id': fraction.assets_asset_id,
                'asset_name': asset.name if asset else 'Unknown Asset',
                'fraction_number': fraction.fraction_no,
                'quantity_owned': 1,
                'purchase_date': ownership.acquired_at.isoformat() if ownership.acquired_at else None,
                'purchase_price': float(fraction.fraction_value) if fraction.fraction_value else None
            }
            fractions_data.append(fraction_data)
    
    return success_response(
        data={
            'user_id': user_id,
            'date': date_str,
            'fractions': fractions_data
        },
        message="User fractions history retrieved successfully"
    )


@bp.route('/<int:user_id>/portfolio', methods=['GET'])
@handle_exceptions
def get_user_portfolio(user_id):
    """
    Get user's complete portfolio summary
    GET /api/v1/users/<user_id>/portfolio
    """
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("User not found")
    
    # Get current ownership records
    ownerships = Ownership.query.filter_by(users_user_id=user_id).all()
    
    portfolio_summary = {
        'user_id': user_id,
        'total_assets': 0,
        'total_fractions': 0,
        'total_investment': 0.0,
        'assets': []
    }
    
    asset_summary = {}
    
    for ownership in ownerships:
        fraction = Fraction.query.get(ownership.fractions_fraction_id)
        if fraction:
            asset = Asset.query.get(fraction.assets_asset_id)
            if asset:
                asset_id = asset.id
                
                if asset_id not in asset_summary:
                    asset_summary[asset_id] = {
                        'asset_id': asset_id,
                        'asset_name': asset.name,
                        'total_fractions': 0,
                        'total_investment': 0.0,
                        'fractions': []
                    }
                
                asset_summary[asset_id]['total_fractions'] += 1
                asset_summary[asset_id]['total_investment'] += float(fraction.fraction_value or 0)
                asset_summary[asset_id]['fractions'].append({
                    'fraction_id': fraction.fraction_id,
                    'fraction_number': fraction.fraction_no,
                    'quantity': 1,
                    'purchase_price': float(fraction.fraction_value or 0)
                })
    
    portfolio_summary['total_assets'] = len(asset_summary)
    portfolio_summary['assets'] = list(asset_summary.values())
    portfolio_summary['total_fractions'] = sum(asset['total_fractions'] for asset in asset_summary.values())
    portfolio_summary['total_investment'] = sum(asset['total_investment'] for asset in asset_summary.values())
    
    return success_response(
        data=portfolio_summary,
        message="User portfolio retrieved successfully"
    )