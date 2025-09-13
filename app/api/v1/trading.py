"""
Trading API endpoints for fractional ownership platform
"""

from flask import Blueprint, request, session
from app.models import User, Asset, Fraction, Ownership, Transaction, ValueHistory, TradeRequest
from app import db
from app.api.errors import ValidationError, NotFoundError, AuthenticationError, success_response, error_response
from app.api.decorators import require_json, require_fields, handle_exceptions
from datetime import datetime
from sqlalchemy import func, desc

bp = Blueprint('trading', __name__, url_prefix='/trading')


@bp.route('/trade', methods=['POST'])
@require_json
@require_fields('from_owner_id', 'to_owner_id', 'fraction_ids')
@handle_exceptions
def trade_fractions():
    """
    Trade fractions between owners
    POST /api/v1/trading/trade
    Body: {
        "from_owner_id": 1,
        "to_owner_id": 2,
        "fraction_ids": [123, 456, 789]
    }
    """
    data = request.get_json()
    from_owner_id = data.get('from_owner_id')
    to_owner_id = data.get('to_owner_id')
    fraction_ids = data.get('fraction_ids', [])
    
    # Validate input
    if not isinstance(fraction_ids, list) or len(fraction_ids) == 0:
        raise ValidationError("fraction_ids must be a non-empty list")
    
    if from_owner_id == to_owner_id:
        raise ValidationError("from_owner_id and to_owner_id cannot be the same")
    
    # Verify both users exist
    from_user = User.query.get(from_owner_id)
    to_user = User.query.get(to_owner_id)
    
    if not from_user:
        raise NotFoundError(f"User {from_owner_id} not found")
    if not to_user:
        raise NotFoundError(f"User {to_owner_id} not found")
    
    results = []
    current_time = datetime.utcnow()
    
    # Process each fraction
    for fraction_id in fraction_ids:
        try:
            # Verify fraction exists
            fraction = Fraction.query.get(fraction_id)
            if not fraction:
                results.append({
                    'fraction_id': fraction_id,
                    'status': 'error',
                    'message': 'Fraction not found'
                })
                continue
            
            # Check current ownership
            current_ownership = Ownership.query.filter_by(
                fractions_fraction_id=fraction_id,
                users_user_id=from_owner_id
            ).first()
            
            if not current_ownership:
                results.append({
                    'fraction_id': fraction_id,
                    'status': 'error',
                    'message': f'User {from_owner_id} does not own this fraction'
                })
                continue
            
            # Remove old ownership
            db.session.delete(current_ownership)
            
            # Create new ownership
            new_ownership = Ownership(
                users_user_id=to_owner_id,
                fractions_fraction_id=fraction_id,
                fractions_assets_asset_id=fraction.assets_asset_id,
                acquired_at=current_time
            )
            db.session.add(new_ownership)
            
            # Create transaction record
            transaction = Transaction(
                transaction_id=None,  # Let auto-increment handle this
                quantity=1,
                unit_price=fraction.fraction_value,
                currency='USD',
                trade_time=current_time,
                from_users_user_id=from_owner_id,
                to_users_user_id=to_owner_id,
                fractions_fraction_id=fraction_id,
                fractions_assets_asset_id=fraction.assets_asset_id,
                notes=f'Fraction transfer from user {from_owner_id} to user {to_owner_id}'
            )
            db.session.add(transaction)
            
            results.append({
                'fraction_id': fraction_id,
                'status': 'success',
                'message': 'Transfer completed successfully'
            })
            
        except Exception as e:
            db.session.rollback()
            results.append({
                'fraction_id': fraction_id,
                'status': 'error',
                'message': str(e)
            })
    
    # Commit all changes
    try:
        db.session.commit()
        return success_response(
            data={'trades': results},
            message=f'Processed {len(fraction_ids)} fraction transfers'
        )
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f'Failed to complete trades: {str(e)}')


@bp.route('/ledger', methods=['GET'])
@handle_exceptions
def get_ledger():
    """
    Get transaction history with optional filters
    GET /api/v1/trading/ledger
    Query params: asset_id, owner_id, start_date, end_date
    """
    # Get query parameters
    asset_id = request.args.get('asset_id', type=int)
    owner_id = request.args.get('owner_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build base query
    query = db.session.query(
        Transaction.transaction_id,
        Transaction.fractions_fraction_id,
        Transaction.from_users_user_id,
        Transaction.to_users_user_id,
        Transaction.trade_time,
        Transaction.unit_price,
        Transaction.currency,
        Transaction.notes,
        Transaction.fractions_assets_asset_id,
        Asset.name.label('asset_name')
    ).join(
        Asset, Transaction.fractions_assets_asset_id == Asset.asset_id
    )
    
    # Apply filters
    if asset_id:
        query = query.filter(Transaction.fractions_assets_asset_id == asset_id)
    
    if owner_id:
        query = query.filter(
            (Transaction.from_users_user_id == owner_id) |
            (Transaction.to_users_user_id == owner_id)
        )
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(Transaction.trade_time >= start_dt)
        except ValueError:
            raise ValidationError("Invalid start_date format. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(Transaction.trade_time <= end_dt)
        except ValueError:
            raise ValidationError("Invalid end_date format. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
    
    # Execute query and format results
    transactions = query.order_by(desc(Transaction.trade_time)).all()
    
    ledger_data = []
    for tx in transactions:
        # Get usernames separately to avoid join conflicts
        from_user = User.query.get(tx.from_users_user_id)
        to_user = User.query.get(tx.to_users_user_id)
        
        ledger_data.append({
            'transaction_id': tx.transaction_id,
            'fraction_id': tx.fractions_fraction_id,
            'asset_name': tx.asset_name,
            'from_owner': from_user.username if from_user else f'User {tx.from_users_user_id}',
            'to_owner': to_user.username if to_user else f'User {tx.to_users_user_id}',
            'timestamp': tx.trade_time.isoformat() if tx.trade_time else None,
            'unit_price': float(tx.unit_price) if tx.unit_price else None,
            'currency': tx.currency,
            'notes': tx.notes
        })
    
    return success_response(
        data={'ledger': ledger_data},
        message=f'Retrieved {len(ledger_data)} transactions'
    )


@bp.route('/fractions/<int:fraction_id>', methods=['GET'])
@handle_exceptions
def get_fraction_details(fraction_id):
    """
    Get detailed information about a specific fraction
    GET /api/v1/trading/fractions/<fraction_id>
    """
    # Get fraction
    fraction = Fraction.query.get(fraction_id)
    if not fraction:
        raise NotFoundError(f"Fraction {fraction_id} not found")
    
    # Get asset information
    asset = Asset.query.get(fraction.assets_asset_id)
    if not asset:
        raise NotFoundError(f"Asset {fraction.assets_asset_id} not found")
    
    # Get current owner (latest ownership record)
    current_ownership = Ownership.query.filter_by(
        fractions_fraction_id=fraction_id
    ).order_by(desc(Ownership.acquired_at)).first()
    
    if not current_ownership:
        raise NotFoundError(f"No ownership record found for fraction {fraction_id}")
    
    # Get current owner details
    current_owner = User.query.get(current_ownership.users_user_id)
    
    # Get latest asset value
    latest_value = ValueHistory.query.filter_by(
        assets_asset_id=fraction.assets_asset_id
    ).order_by(desc(ValueHistory.update_time)).first()
    
    # Calculate current value
    current_value = None
    if latest_value and asset.available_fractions and asset.available_fractions > 0:
        current_value = float(latest_value.asset_value) / asset.available_fractions
    
    fraction_data = {
        'fraction_id': fraction_id,
        'fraction_no': fraction.fraction_no,
        'asset': {
            'asset_id': asset.asset_id,
            'name': asset.name,
            'description': asset.description
        },
        'current_owner': {
            'user_id': current_ownership.users_user_id,
            'username': current_owner.username if current_owner else None
        },
        'purchase_time': current_ownership.acquired_at.isoformat() if current_ownership.acquired_at else None,
        'current_value': current_value,
        'latest_asset_value': latest_value.asset_value if latest_value else None,
        'total_fractions': asset.available_fractions
    }
    
    return success_response(
        data=fraction_data,
        message='Fraction details retrieved successfully'
    )


@bp.route('/snapshot', methods=['GET'])
@handle_exceptions
def get_ownership_snapshot():
    """
    Get ownership snapshot at a specific date
    GET /api/v1/trading/snapshot?at=YYYY-MM-DD
    """
    at_date = request.args.get('at')
    if not at_date:
        raise ValidationError("at parameter is required (YYYY-MM-DD format)")
    
    try:
        # Parse date
        snapshot_date = datetime.fromisoformat(at_date)
        # Set to end of day to include all transactions on that date
        snapshot_date = snapshot_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        raise ValidationError("Invalid date format. Use YYYY-MM-DD")
    
    # Get all assets
    assets = Asset.query.all()
    snapshot_data = []
    
    for asset in assets:
        asset_data = {
            'asset_id': asset.asset_id,
            'asset_name': asset.name,
            'fractions': []
        }
        
        # Get all fractions for this asset
        fractions = Fraction.query.filter_by(assets_asset_id=asset.asset_id).all()
        
        for fraction in fractions:
            # Get ownership at or before snapshot date
            ownership = Ownership.query.filter(
                Ownership.fractions_fraction_id == fraction.fraction_id,
                Ownership.acquired_at <= snapshot_date
            ).order_by(desc(Ownership.acquired_at)).first()
            
            if ownership:
                owner = User.query.get(ownership.users_user_id)
                asset_data['fractions'].append({
                    'fraction_id': fraction.fraction_id,
                    'fraction_no': fraction.fraction_no,
                    'current_owner': {
                        'user_id': ownership.users_user_id,
                        'username': owner.username if owner else None
                    },
                    'last_transfer_timestamp': ownership.acquired_at.isoformat() if ownership.acquired_at else None
                })
        
        # Sort fractions by fraction_id
        asset_data['fractions'].sort(key=lambda x: x['fraction_id'])
        snapshot_data.append(asset_data)
    
    # Sort assets by asset_id
    snapshot_data.sort(key=lambda x: x['asset_id'])
    
    return success_response(
        data={
            'snapshot_date': at_date,
            'assets': snapshot_data
        },
        message=f'Ownership snapshot for {at_date} retrieved successfully'
    )


@bp.route('/request_trade', methods=['POST'])
@require_json
@require_fields('fraction_id', 'to_user_id')
@handle_exceptions
def request_trade():
    """
    Create a new trade request
    POST /api/v1/trading/request_trade
    Body: {
        "fraction_id": 123,
        "to_user_id": 2,
        "notes": "Optional message"
    }
    """
    data = request.get_json()
    fraction_id = data.get('fraction_id')
    to_user_id = data.get('to_user_id')
    notes = data.get('notes', '')
    
    # Get current user from session
    current_user_id = session.get('user_id')
    if not current_user_id:
        raise AuthenticationError("Authentication required")
    
    # Validate input
    if not isinstance(fraction_id, int):
        raise ValidationError("fraction_id must be an integer")
    
    if not isinstance(to_user_id, int):
        raise ValidationError("to_user_id must be an integer")
    
    if current_user_id == to_user_id:
        raise ValidationError("Cannot request trade with yourself")
    
    # Verify fraction exists and get current owner
    fraction = Fraction.query.get(fraction_id)
    if not fraction:
        raise NotFoundError(f"Fraction {fraction_id} not found")
    
    # Get current owner of the fraction
    current_ownership = Ownership.query.filter_by(
        fractions_fraction_id=fraction_id
    ).order_by(desc(Ownership.acquired_at)).first()
    
    if not current_ownership:
        raise NotFoundError(f"No current owner found for fraction {fraction_id}")
    
    from_user_id = current_ownership.users_user_id
    
    # Check if user is trying to request their own fraction
    if current_user_id == from_user_id:
        raise ValidationError("Cannot request trade for your own fraction")
    
    # Verify target user exists
    to_user = User.query.get(to_user_id)
    if not to_user:
        raise NotFoundError(f"User {to_user_id} not found")
    
    # Check for existing pending request for this fraction
    existing_request = TradeRequest.query.filter_by(
        fraction_id=fraction_id,
        from_user_id=from_user_id,
        to_user_id=current_user_id,
        status='pending'
    ).first()
    
    if existing_request:
        raise ValidationError("A pending trade request already exists for this fraction")
    
    try:
        # Create trade request
        trade_request = TradeRequest(
            fraction_id=fraction_id,
            from_user_id=from_user_id,
            to_user_id=current_user_id,
            notes=notes,
            requested_at=datetime.utcnow()
        )
        
        db.session.add(trade_request)
        db.session.commit()
        
        # Get asset info for response
        asset = Asset.query.get(fraction.assets_asset_id)
        
        return success_response(
            data={
                'request_id': trade_request.request_id,
                'fraction_id': fraction_id,
                'asset_name': asset.name if asset else 'Unknown Asset',
                'from_user': User.query.get(from_user_id).username,
                'to_user': to_user.username,
                'status': 'pending',
                'requested_at': trade_request.requested_at.isoformat()
            },
            message='Trade request created successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f'Failed to create trade request: {str(e)}')


@bp.route('/requests', methods=['GET'])
@handle_exceptions
def get_trade_requests():
    """
    Get trade requests for a user
    GET /api/v1/trading/requests?user_id=...&type=incoming|outgoing
    """
    # Get current user from session
    current_user_id = session.get('user_id')
    if not current_user_id:
        raise AuthenticationError("Authentication required")
    
    # Get query parameters
    user_id = request.args.get('user_id', type=int)
    request_type = request.args.get('type', 'all')  # incoming, outgoing, or all
    
    # If no user_id specified, use current user
    if not user_id:
        user_id = current_user_id
    
    # Build query with aliases for users table
    from sqlalchemy.orm import aliased
    from_user_alias = aliased(User)
    to_user_alias = aliased(User)
    
    query = db.session.query(
        TradeRequest.request_id,
        TradeRequest.fraction_id,
        TradeRequest.from_user_id,
        TradeRequest.to_user_id,
        TradeRequest.status,
        TradeRequest.requested_at,
        TradeRequest.responded_at,
        TradeRequest.notes,
        Asset.name.label('asset_name'),
        from_user_alias.username.label('from_username'),
        to_user_alias.username.label('to_username')
    ).join(
        Fraction, TradeRequest.fraction_id == Fraction.fraction_id
    ).join(
        Asset, Fraction.assets_asset_id == Asset.asset_id
    ).join(
        from_user_alias, TradeRequest.from_user_id == from_user_alias.user_id
    ).join(
        to_user_alias, TradeRequest.to_user_id == to_user_alias.user_id
    )
    
    # Filter by request type
    if request_type == 'incoming':
        query = query.filter(TradeRequest.to_user_id == user_id)
    elif request_type == 'outgoing':
        query = query.filter(TradeRequest.from_user_id == user_id)
    else:
        # Show all requests involving this user
        query = query.filter(
            (TradeRequest.from_user_id == user_id) |
            (TradeRequest.to_user_id == user_id)
        )
    
    # Execute query
    requests = query.order_by(desc(TradeRequest.requested_at)).all()
    
    # Format response
    requests_data = []
    for req in requests:
        # Get usernames separately to avoid join conflicts
        from_user = User.query.get(req.from_user_id)
        to_user = User.query.get(req.to_user_id)
        
        requests_data.append({
            'request_id': req.request_id,
            'fraction_id': req.fraction_id,
            'asset_name': req.asset_name,
            'from_user': {
                'user_id': req.from_user_id,
                'username': from_user.username if from_user else None
            },
            'to_user': {
                'user_id': req.to_user_id,
                'username': to_user.username if to_user else None
            },
            'status': req.status,
            'requested_at': req.requested_at.isoformat() if req.requested_at else None,
            'responded_at': req.responded_at.isoformat() if req.responded_at else None,
            'notes': req.notes,
            'is_incoming': req.to_user_id == current_user_id,
            'is_outgoing': req.from_user_id == current_user_id
        })
    
    return success_response(
        data={'requests': requests_data},
        message=f'Retrieved {len(requests_data)} trade requests'
    )


@bp.route('/respond_request', methods=['POST'])
@require_json
@require_fields('request_id', 'action')
@handle_exceptions
def respond_to_trade_request():
    """
    Respond to a trade request (approve or deny)
    POST /api/v1/trading/respond_request
    Body: {
        "request_id": "uuid-string",
        "action": "approve" | "deny"
    }
    """
    data = request.get_json()
    request_id = data.get('request_id')
    action = data.get('action')
    
    # Get current user from session
    current_user_id = session.get('user_id')
    if not current_user_id:
        raise AuthenticationError("Authentication required")
    
    # Validate action
    if action not in ['approve', 'deny']:
        raise ValidationError("action must be 'approve' or 'deny'")
    
    # Get trade request
    trade_request = TradeRequest.query.get(request_id)
    if not trade_request:
        raise NotFoundError(f"Trade request {request_id} not found")
    
    # Verify current user is the owner (can respond to this request)
    if trade_request.to_user_id != current_user_id:
        raise ValidationError("You can only respond to requests for your own fractions")
    
    # Check if request is still pending
    if trade_request.status != 'pending':
        raise ValidationError(f"Trade request is already {trade_request.status}")
    
    try:
        current_time = datetime.utcnow()
        trade_request.status = 'approved' if action == 'approve' else 'denied'
        trade_request.responded_at = current_time
        
        if action == 'approve':
            # Transfer ownership
            fraction_id = trade_request.fraction_id
            
            # Get fraction info
            fraction = Fraction.query.get(fraction_id)
            if not fraction:
                raise NotFoundError(f"Fraction {fraction_id} not found")
            
            # Remove old ownership
            old_ownership = Ownership.query.filter_by(
                fractions_fraction_id=fraction_id,
                users_user_id=trade_request.from_user_id
            ).first()
            
            if not old_ownership:
                raise NotFoundError(f"Current ownership not found for fraction {fraction_id}")
            
            db.session.delete(old_ownership)
            
            # Create new ownership
            new_ownership = Ownership(
                users_user_id=trade_request.to_user_id,
                fractions_fraction_id=fraction_id,
                fractions_assets_asset_id=fraction.assets_asset_id,
                acquired_at=current_time
            )
            db.session.add(new_ownership)
            
            # Create transaction record
            transaction = Transaction(
                transaction_id=None,  # Let auto-increment handle this
                quantity=1,
                unit_price=fraction.fraction_value,
                currency='USD',
                trade_time=current_time,
                from_users_user_id=trade_request.from_user_id,
                to_users_user_id=trade_request.to_user_id,
                fractions_fraction_id=fraction_id,
                fractions_assets_asset_id=fraction.assets_asset_id,
                notes=f'Fraction transfer via approved trade request {request_id}'
            )
            db.session.add(transaction)
        
        db.session.commit()
        
        return success_response(
            data={
                'request_id': request_id,
                'status': trade_request.status,
                'responded_at': trade_request.responded_at.isoformat()
            },
            message=f'Trade request {action}d successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f'Failed to respond to trade request: {str(e)}')


@bp.route('/browse_fractions', methods=['GET'])
@handle_exceptions
def browse_fractions():
    """
    Browse available fractions (not owned by current user)
    GET /api/v1/trading/browse_fractions?asset_id=...&page=...&per_page=...
    """
    # Get current user from session
    current_user_id = session.get('user_id')
    if not current_user_id:
        raise AuthenticationError("Authentication required")
    
    # Get query parameters
    asset_id = request.args.get('asset_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Build query for fractions not owned by current user
    query = db.session.query(
        Fraction.fraction_id,
        Fraction.fraction_no,
        Fraction.fraction_value,
        Asset.asset_id,
        Asset.name.label('asset_name'),
        Asset.description.label('asset_description'),
        User.username.label('current_owner'),
        Ownership.acquired_at.label('acquired_date')
    ).join(
        Asset, Fraction.assets_asset_id == Asset.asset_id
    ).join(
        Ownership, Fraction.fraction_id == Ownership.fractions_fraction_id
    ).join(
        User, Ownership.users_user_id == User.user_id
    ).filter(
        Ownership.users_user_id != current_user_id
    )
    
    # Apply asset filter if specified
    if asset_id:
        query = query.filter(Asset.asset_id == asset_id)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    fractions = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Format response
    fractions_data = []
    for fraction in fractions:
        fractions_data.append({
            'fraction_id': fraction.fraction_id,
            'fraction_no': fraction.fraction_no,
            'fraction_value': float(fraction.fraction_value) if fraction.fraction_value else 0.0,
            'asset': {
                'asset_id': fraction.asset_id,
                'name': fraction.asset_name,
                'description': fraction.asset_description
            },
            'current_owner': {
                'username': fraction.current_owner,
                'acquired_date': fraction.acquired_date.isoformat() if fraction.acquired_date else None
            }
        })
    
    return success_response(
        data={
            'fractions': fractions_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        },
        message=f'Retrieved {len(fractions_data)} available fractions'
    )