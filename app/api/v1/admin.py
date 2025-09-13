"""
Admin API endpoints for fractional ownership platform
"""

from flask import Blueprint, request, session
from app.models import User, Asset, Fraction, ValueHistory, Transaction, Ownership
from app import db
from app.api.errors import ValidationError, NotFoundError, AuthenticationError, success_response, error_response
from app.api.decorators import require_json, require_fields, handle_exceptions
from datetime import datetime
from sqlalchemy import func
import secrets

bp = Blueprint('admin', __name__, url_prefix='/admin')


def require_admin():
    """Decorator to require admin/manager access"""
    user_id = session.get('user_id')
    if not user_id:
        raise AuthenticationError("Authentication required")
    
    user = User.query.get(user_id)
    if not user or not user.is_manager:
        raise AuthenticationError("Admin access required")


@bp.route('/assets', methods=['POST'])
@require_json
@require_fields('asset_name', 'description', 'initial_value', 'total_fractions')
@handle_exceptions
def create_asset():
    """
    Create a new asset (admin only)
    POST /api/v1/admin/assets
    Body: {
        "asset_name": "New Asset",
        "description": "Asset description",
        "initial_value": 1000000,
        "total_fractions": 10000,
        "ownership": {
            "user1_id": 30,
            "user2_id": 70
        }
    }
    """
    # Check admin access
    require_admin()
    
    data = request.get_json()
    asset_name = data.get('asset_name')
    description = data.get('description')
    initial_value = data.get('initial_value')
    total_fractions = data.get('total_fractions')
    ownership = data.get('ownership', {})
    
    # Validate input
    if not isinstance(initial_value, (int, float)) or initial_value <= 0:
        raise ValidationError("initial_value must be a positive number")
    
    if not isinstance(total_fractions, int) or total_fractions <= 0:
        raise ValidationError("total_fractions must be a positive integer")
    
    if total_fractions > 100000:
        raise ValidationError("total_fractions cannot exceed 100,000")
    
    # Validate ownership assignment if provided
    total_ownership_fractions = 0
    if ownership:
        for user_id_str, fraction_count in ownership.items():
            if not user_id_str.startswith('user') or not user_id_str.endswith('_id'):
                raise ValidationError(f"Invalid ownership key format: {user_id_str}")
            
            try:
                user_id = int(user_id_str.replace('user', '').replace('_id', ''))
            except ValueError:
                raise ValidationError(f"Invalid user ID in ownership key: {user_id_str}")
            
            if not isinstance(fraction_count, int) or fraction_count <= 0:
                raise ValidationError(f"Fraction count must be a positive integer for {user_id_str}")
            
            # Verify user exists
            user = User.query.get(user_id)
            if not user:
                raise ValidationError(f"User {user_id} not found")
            
            total_ownership_fractions += fraction_count
        
        if total_ownership_fractions > total_fractions:
            raise ValidationError(f"Total ownership fractions ({total_ownership_fractions}) cannot exceed total fractions ({total_fractions})")
    
    try:
        current_time = datetime.utcnow()
        user_id = session.get('user_id')
        
        # Create asset
        asset = Asset(
            name=asset_name,
            description=description,
            available_fractions=total_fractions,
            max_fractions=total_fractions,
            min_fractions=1,
            submitted_by_users_user_id=user_id,
            created_at=current_time,
            status='approved',
            approved_at=current_time,
            approved_by_users_user_id=user_id
        )
        db.session.add(asset)
        db.session.flush()  # Get asset_id
        
        # Create initial value history entry
        value_history = ValueHistory(
            value_id=f"init_{asset.asset_id}_{secrets.token_hex(8)}",
            assets_asset_id=asset.asset_id,
            asset_value=initial_value,
            update_time=current_time
        )
        db.session.add(value_history)
        
        # Create fractions
        fraction_value = initial_value / total_fractions
        fraction_ids = []
        ownership_assignments = []
        
        # Create fractions and assign ownership
        current_fraction = 1
        
        if ownership:
            # Assign fractions to specified users
            for user_id_str, fraction_count in ownership.items():
                user_id = int(user_id_str.replace('user', '').replace('_id', ''))
                
                for i in range(fraction_count):
                    if current_fraction > total_fractions:
                        break
                    
                    fraction = Fraction(
                        assets_asset_id=asset.asset_id,
                        fraction_no=current_fraction,
                        fraction_value=fraction_value
                    )
                    db.session.add(fraction)
                    db.session.flush()  # Get fraction_id
                    fraction_ids.append(fraction.fraction_id)
                    
                    # Create ownership record
                    ownership_record = Ownership(
                        users_user_id=user_id,
                        fractions_fraction_id=fraction.fraction_id,
                        fractions_assets_asset_id=asset.asset_id,
                        acquired_at=current_time
                    )
                    db.session.add(ownership_record)
                    ownership_assignments.append({
                        'user_id': user_id,
                        'fraction_id': fraction.fraction_id,
                        'username': User.query.get(user_id).username
                    })
                    
                    current_fraction += 1
        else:
            # Create fractions without initial ownership (admin owns them)
            admin_user_id = session.get('user_id')
            for i in range(1, total_fractions + 1):
                fraction = Fraction(
                    assets_asset_id=asset.asset_id,
                    fraction_no=i,
                    fraction_value=fraction_value
                )
                db.session.add(fraction)
                db.session.flush()  # Get fraction_id
                fraction_ids.append(fraction.fraction_id)
                
                # Create ownership record for admin
                ownership_record = Ownership(
                    users_user_id=admin_user_id,
                    fractions_fraction_id=fraction.fraction_id,
                    fractions_assets_asset_id=asset.asset_id,
                    acquired_at=current_time
                )
                db.session.add(ownership_record)
                ownership_assignments.append({
                    'user_id': admin_user_id,
                    'fraction_id': fraction.fraction_id,
                    'username': User.query.get(admin_user_id).username
                })
        
        db.session.commit()
        
        return success_response(
            data={
                'asset_id': asset.asset_id,
                'asset_name': asset.name,
                'description': asset.description,
                'initial_value': initial_value,
                'total_fractions': total_fractions,
                'fraction_value': fraction_value,
                'fraction_ids': fraction_ids,
                'ownership_assignments': ownership_assignments,
                'created_at': current_time.isoformat()
            },
            message=f'Asset "{asset_name}" created successfully with {total_fractions} fractions and ownership assignments'
        )
        
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f'Failed to create asset: {str(e)}')


@bp.route('/assets/<int:asset_id>/value', methods=['POST'])
@require_json
@require_fields('new_value')
@handle_exceptions
def update_asset_value(asset_id):
    """
    Update asset value (admin only)
    POST /api/v1/admin/assets/<asset_id>/value
    Body: {"new_value": 1500000}
    """
    # Check admin access
    require_admin()
    
    data = request.get_json()
    new_value = data.get('new_value')
    
    # Validate input
    if not isinstance(new_value, (int, float)) or new_value <= 0:
        raise ValidationError("new_value must be a positive number")
    
    # Get asset
    asset = Asset.query.get(asset_id)
    if not asset:
        raise NotFoundError(f"Asset {asset_id} not found")
    
    try:
        current_time = datetime.utcnow()
        
        # Create new value history entry
        value_history = ValueHistory(
            value_id=f"update_{asset_id}_{secrets.token_hex(8)}",
            assets_asset_id=asset_id,
            asset_value=new_value,
            update_time=current_time
        )
        db.session.add(value_history)
        
        # Update fraction values
        if asset.available_fractions and asset.available_fractions > 0:
            new_fraction_value = new_value / asset.available_fractions
            
            # Update all fractions for this asset
            Fraction.query.filter_by(assets_asset_id=asset_id).update({
                'fraction_value': new_fraction_value
            })
        
        db.session.commit()
        
        return success_response(
            data={
                'asset_id': asset_id,
                'asset_name': asset.name,
                'old_value': asset.value_history[-2].asset_value if len(asset.value_history) > 1 else None,
                'new_value': new_value,
                'new_fraction_value': new_fraction_value if asset.available_fractions else None,
                'updated_at': current_time.isoformat()
            },
            message=f'Asset value updated successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f'Failed to update asset value: {str(e)}')


@bp.route('/users', methods=['GET'])
@handle_exceptions
def list_users():
    """
    List all users (admin only)
    GET /api/v1/admin/users
    """
    # Check admin access
    require_admin()
    
    users = User.query.all()
    users_data = [user.to_dict() for user in users]
    
    return success_response(
        data={'users': users_data},
        message=f'Retrieved {len(users_data)} users'
    )


@bp.route('/stats', methods=['GET'])
@handle_exceptions
def get_admin_stats():
    """
    Get platform statistics (admin only)
    GET /api/v1/admin/stats
    """
    # Check admin access
    require_admin()
    
    # Get counts
    total_assets = Asset.query.count()
    total_users = User.query.count()
    total_fractions = Fraction.query.count()
    total_transactions = db.session.query(Transaction).count()
    total_ownership_records = db.session.query(Ownership).count()
    
    # Get recent activity
    recent_transactions = db.session.query(Transaction).order_by(
        db.desc(Transaction.trade_time)
    ).limit(5).all()
    
    recent_transactions_data = [tx.to_dict() for tx in recent_transactions]
    
    # Get asset value distribution
    asset_values = db.session.query(
        Asset.asset_id,
        Asset.name,
        func.max(ValueHistory.asset_value).label('latest_value')
    ).join(ValueHistory).group_by(Asset.asset_id, Asset.name).all()
    
    stats_data = {
        'totals': {
            'assets': total_assets,
            'users': total_users,
            'fractions': total_fractions,
            'transactions': total_transactions,
            'ownership_records': total_ownership_records
        },
        'recent_transactions': recent_transactions_data,
        'asset_values': [
            {
                'asset_id': av.asset_id,
                'asset_name': av.name,
                'latest_value': av.latest_value
            }
            for av in asset_values
        ]
    }
    
    return success_response(
        data=stats_data,
        message='Platform statistics retrieved successfully'
    )