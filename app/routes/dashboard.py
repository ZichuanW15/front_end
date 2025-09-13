"""
Dashboard routes for the web interface
"""

from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from app.models import User, Asset, Fraction, Ownership, Transaction, ValueHistory, TradeRequest
from app import db
from datetime import datetime, timedelta
import requests
import json

bp = Blueprint('dashboard', __name__)


def require_login(f):
    """Decorator to require user login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login_page'))
        if not session.get('is_admin', False):
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard.user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/dashboard')
@require_login
def user_dashboard():
    """Regular user dashboard showing owned fractions"""
    user_id = session['user_id']
    
    # Get user's owned fractions with asset details
    user_holdings = db.session.query(
        Ownership.fractions_fraction_id,
        Ownership.acquired_at,
        Asset.asset_id,
        Asset.name.label('asset_name'),
        Asset.description.label('asset_description'),
        Fraction.fraction_value,
        Fraction.fraction_no
    ).join(
        Fraction, Ownership.fractions_fraction_id == Fraction.fraction_id
    ).join(
        Asset, Fraction.assets_asset_id == Asset.asset_id
    ).filter(
        Ownership.users_user_id == user_id
    ).all()
    
    # Group holdings by asset
    asset_holdings = {}
    for holding in user_holdings:
        asset_id = holding.asset_id
        if asset_id not in asset_holdings:
            asset_holdings[asset_id] = {
                'asset_name': holding.asset_name,
                'asset_description': holding.asset_description,
                'fractions': [],
                'total_fractions': 0,
                'total_value': 0.0
            }
        
        asset_holdings[asset_id]['fractions'].append({
            'fraction_id': holding.fractions_fraction_id,
            'fraction_no': holding.fraction_no,
            'fraction_value': float(holding.fraction_value) if holding.fraction_value else 0.0,
            'acquired_at': holding.acquired_at
        })
        asset_holdings[asset_id]['total_fractions'] += 1
        asset_holdings[asset_id]['total_value'] += float(holding.fraction_value) if holding.fraction_value else 0.0
    
    # Get latest asset values for each asset
    for asset_id in asset_holdings:
        latest_value = ValueHistory.query.filter_by(
            assets_asset_id=asset_id
        ).order_by(ValueHistory.update_time.desc()).first()
        
        asset_holdings[asset_id]['latest_asset_value'] = latest_value.asset_value if latest_value else 0
        asset_holdings[asset_id]['value_updated'] = latest_value.update_time if latest_value else None
    
    # Calculate portfolio summary
    total_assets = len(asset_holdings)
    total_fractions = sum(h['total_fractions'] for h in asset_holdings.values())
    total_value = sum(h['total_value'] for h in asset_holdings.values())
    
    return render_template('dashboard.html', 
                         asset_holdings=asset_holdings,
                         total_assets=total_assets,
                         total_fractions=total_fractions,
                         total_value=total_value,
                         username=session.get('username'))


@bp.route('/admin')
@require_admin
def admin_dashboard():
    """Admin dashboard with system overview and management tools"""
    # Get platform statistics
    stats = {
        'total_users': User.query.count(),
        'total_assets': Asset.query.count(),
        'total_fractions': Fraction.query.count(),
        'total_transactions': Transaction.query.count(),
        'total_ownership_records': Ownership.query.count()
    }
    
    # Get recent users
    recent_users = User.query.order_by(User.create_time.desc()).limit(10).all()
    
    # Get all assets with their latest values
    assets_with_values = db.session.query(
        Asset.asset_id,
        Asset.name,
        Asset.description,
        Asset.available_fractions,
        Asset.created_at,
        ValueHistory.asset_value.label('latest_value'),
        ValueHistory.update_time.label('value_updated')
    ).outerjoin(
        ValueHistory, Asset.asset_id == ValueHistory.assets_asset_id
    ).all()
    
    # Group by asset and get the latest value for each
    assets_data = {}
    for asset in assets_with_values:
        asset_id = asset.asset_id
        if asset_id not in assets_data or (asset.value_updated and 
            (assets_data[asset_id]['value_updated'] is None or 
             asset.value_updated > assets_data[asset_id]['value_updated'])):
            assets_data[asset_id] = {
                'asset_id': asset.asset_id,
                'name': asset.name,
                'description': asset.description,
                'available_fractions': asset.available_fractions,
                'created_at': asset.created_at,
                'latest_value': asset.latest_value,
                'value_updated': asset.value_updated,
                'fraction_value': asset.latest_value / asset.available_fractions if asset.available_fractions and asset.latest_value else 0
            }
    
    # Get recent transactions
    recent_transactions = db.session.query(
        Transaction.transaction_id,
        Transaction.trade_time,
        Transaction.unit_price,
        Transaction.currency,
        Asset.name.label('asset_name'),
        User.username.label('from_owner'),
        User.username.label('to_owner')
    ).join(
        Asset, Transaction.fractions_assets_asset_id == Asset.asset_id
    ).join(
        User, Transaction.from_users_user_id == User.user_id
    ).order_by(Transaction.trade_time.desc()).limit(10).all()
    
    return render_template('admin_dashboard.html',
                         stats=stats,
                         recent_users=recent_users,
                         assets_data=assets_data,
                         recent_transactions=recent_transactions,
                         username=session.get('username'))


@bp.route('/admin/create_asset', methods=['POST'])
@require_admin
def create_asset():
    """Create a new asset (admin only)"""
    try:
        asset_name = request.form.get('asset_name')
        description = request.form.get('description')
        initial_value = float(request.form.get('initial_value', 0))
        total_fractions = int(request.form.get('total_fractions', 0))
        
        if not asset_name or not description or initial_value <= 0 or total_fractions <= 0:
            flash('All fields are required and must be positive values', 'error')
            return redirect(url_for('dashboard.admin_dashboard'))
        
        if total_fractions > 100000:
            flash('Total fractions cannot exceed 100,000', 'error')
            return redirect(url_for('dashboard.admin_dashboard'))
        
        # Parse ownership assignment data
        ownership_data = request.form.get('ownership_data')
        ownership = {}
        if ownership_data:
            try:
                ownership = json.loads(ownership_data)
            except json.JSONDecodeError:
                flash('Invalid ownership data format', 'error')
                return redirect(url_for('dashboard.admin_dashboard'))
        
        # Create asset
        asset = Asset(
            name=asset_name,
            description=description,
            available_fractions=total_fractions,
            max_fractions=total_fractions,
            min_fractions=1,
            submitted_by_users_user_id=session['user_id'],
            created_at=datetime.utcnow(),
            status='approved',
            approved_at=datetime.utcnow(),
            approved_by_users_user_id=session['user_id']
        )
        db.session.add(asset)
        db.session.flush()  # Get asset_id
        
        # Create initial value history entry
        value_history = ValueHistory(
            value_id=f"init_{asset.asset_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            assets_asset_id=asset.asset_id,
            asset_value=initial_value,
            update_time=datetime.utcnow()
        )
        db.session.add(value_history)
        
        # Create fractions with ownership assignment
        fraction_value = initial_value / total_fractions
        current_time = datetime.utcnow()
        current_fraction = 1
        
        if ownership:
            # Assign fractions to specified users
            for user_id_str, fraction_count in ownership.items():
                try:
                    user_id = int(user_id_str.replace('user', '').replace('_id', ''))
                except ValueError:
                    continue
                
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
                    
                    # Create ownership record
                    ownership_record = Ownership(
                        users_user_id=user_id,
                        fractions_fraction_id=fraction.fraction_id,
                        fractions_assets_asset_id=asset.asset_id,
                        acquired_at=current_time
                    )
                    db.session.add(ownership_record)
                    
                    current_fraction += 1
        else:
            # Create fractions without initial ownership (admin owns them)
            admin_user_id = session['user_id']
            for i in range(1, total_fractions + 1):
                fraction = Fraction(
                    assets_asset_id=asset.asset_id,
                    fraction_no=i,
                    fraction_value=fraction_value
                )
                db.session.add(fraction)
                db.session.flush()  # Get fraction_id
                
                # Create ownership record for admin
                ownership_record = Ownership(
                    users_user_id=admin_user_id,
                    fractions_fraction_id=fraction.fraction_id,
                    fractions_assets_asset_id=asset.asset_id,
                    acquired_at=current_time
                )
                db.session.add(ownership_record)
        
        db.session.commit()
        
        flash(f'Asset "{asset_name}" created successfully with {total_fractions} fractions', 'success')
        return redirect(url_for('dashboard.admin_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to create asset: {str(e)}', 'error')
        return redirect(url_for('dashboard.admin_dashboard'))


@bp.route('/admin/update_asset_value/<int:asset_id>', methods=['POST'])
@require_admin
def update_asset_value(asset_id):
    """Update asset value (admin only)"""
    try:
        new_value = float(request.form.get('new_value', 0))
        
        if new_value <= 0:
            flash('New value must be positive', 'error')
            return redirect(url_for('dashboard.admin_dashboard'))
        
        # Get asset
        asset = Asset.query.get(asset_id)
        if not asset:
            flash('Asset not found', 'error')
            return redirect(url_for('dashboard.admin_dashboard'))
        
        # Create new value history entry
        value_history = ValueHistory(
            value_id=f"update_{asset_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            assets_asset_id=asset_id,
            asset_value=new_value,
            update_time=datetime.utcnow()
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
        
        flash(f'Asset value updated successfully to ${new_value:,.2f}', 'success')
        return redirect(url_for('dashboard.admin_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to update asset value: {str(e)}', 'error')
        return redirect(url_for('dashboard.admin_dashboard'))


@bp.route('/ledger')
@require_login
def view_ledger():
    """View transaction ledger"""
    user_id = session['user_id']
    
    # Get query parameters
    asset_id = request.args.get('asset_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query for user's transactions
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
    ).filter(
        (Transaction.from_users_user_id == user_id) |
        (Transaction.to_users_user_id == user_id)
    )
    
    # Apply filters
    if asset_id:
        query = query.filter(Transaction.fractions_assets_asset_id == asset_id)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Transaction.trade_time >= start_dt)
        except ValueError:
            flash('Invalid start date format', 'error')
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Transaction.trade_time <= end_dt)
        except ValueError:
            flash('Invalid end date format', 'error')
    
    # Execute query
    transactions = query.order_by(Transaction.trade_time.desc()).limit(100).all()
    
    # Format transaction data
    ledger_data = []
    for tx in transactions:
        from_user = User.query.get(tx.from_users_user_id)
        to_user = User.query.get(tx.to_users_user_id)
        
        ledger_data.append({
            'transaction_id': tx.transaction_id,
            'fraction_id': tx.fractions_fraction_id,
            'asset_name': tx.asset_name,
            'from_owner': from_user.username if from_user else f'User {tx.from_users_user_id}',
            'to_owner': to_user.username if to_user else f'User {tx.to_users_user_id}',
            'timestamp': tx.trade_time,
            'unit_price': float(tx.unit_price) if tx.unit_price else None,
            'currency': tx.currency,
            'notes': tx.notes,
            'is_outgoing': tx.from_users_user_id == user_id
        })
    
    # Get available assets for filter dropdown
    user_assets = db.session.query(Asset.asset_id, Asset.name).join(
        Fraction, Asset.asset_id == Fraction.assets_asset_id
    ).join(
        Ownership, Fraction.fraction_id == Ownership.fractions_fraction_id
    ).filter(Ownership.users_user_id == user_id).distinct().all()
    
    return render_template('ledger.html',
                         transactions=ledger_data,
                         user_assets=user_assets,
                         username=session.get('username'))


@bp.route('/snapshot')
@require_login
def view_snapshot():
    """View ownership snapshot at a specific date"""
    snapshot_date = request.args.get('at')
    
    if not snapshot_date:
        # Default to yesterday
        snapshot_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        # Parse date
        snapshot_dt = datetime.fromisoformat(snapshot_date)
        snapshot_dt = snapshot_dt.replace(hour=23, minute=59, second=59)
    except ValueError:
        flash('Invalid date format. Use YYYY-MM-DD', 'error')
        snapshot_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        snapshot_dt = datetime.fromisoformat(snapshot_date).replace(hour=23, minute=59, second=59)
    
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
                Ownership.acquired_at <= snapshot_dt
            ).order_by(Ownership.acquired_at.desc()).first()
            
            if ownership:
                owner = User.query.get(ownership.users_user_id)
                asset_data['fractions'].append({
                    'fraction_id': fraction.fraction_id,
                    'fraction_no': fraction.fraction_no,
                    'current_owner': {
                        'user_id': ownership.users_user_id,
                        'username': owner.username if owner else None
                    },
                    'last_transfer_timestamp': ownership.acquired_at
                })
        
        # Sort fractions by fraction_id
        asset_data['fractions'].sort(key=lambda x: x['fraction_id'])
        snapshot_data.append(asset_data)
    
    # Sort assets by asset_id
    snapshot_data.sort(key=lambda x: x['asset_id'])
    
    return render_template('snapshot.html',
                         snapshot_data=snapshot_data,
                         snapshot_date=snapshot_date,
                         username=session.get('username'))


@bp.route('/trade', methods=['GET', 'POST'])
@require_login
def trade_fractions():
    """Trade fractions interface"""
    if request.method == 'POST':
        try:
            from_owner_id = int(request.form.get('from_owner_id'))
            to_owner_id = int(request.form.get('to_owner_id'))
            fraction_ids_str = request.form.get('fraction_ids', '')
            
            # Parse fraction IDs
            fraction_ids = [int(fid.strip()) for fid in fraction_ids_str.split(',') if fid.strip()]
            
            if not fraction_ids:
                flash('Please specify fraction IDs to trade', 'error')
                return redirect(url_for('dashboard.trade_fractions'))
            
            if from_owner_id == to_owner_id:
                flash('Cannot trade fractions to yourself', 'error')
                return redirect(url_for('dashboard.trade_fractions'))
            
            # Verify current ownership
            for fraction_id in fraction_ids:
                current_ownership = Ownership.query.filter_by(
                    fractions_fraction_id=fraction_id,
                    users_user_id=from_owner_id
                ).first()
                
                if not current_ownership:
                    flash(f'You do not own fraction {fraction_id}', 'error')
                    return redirect(url_for('dashboard.trade_fractions'))
            
            # Process trades
            current_time = datetime.utcnow()
            successful_trades = 0
            
            for fraction_id in fraction_ids:
                try:
                    # Get fraction info
                    fraction = Fraction.query.get(fraction_id)
                    if not fraction:
                        continue
                    
                    # Remove old ownership
                    old_ownership = Ownership.query.filter_by(
                        fractions_fraction_id=fraction_id,
                        users_user_id=from_owner_id
                    ).first()
                    if old_ownership:
                        db.session.delete(old_ownership)
                    
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
                    
                    successful_trades += 1
                    
                except Exception as e:
                    continue
            
            db.session.commit()
            
            if successful_trades > 0:
                flash(f'Successfully traded {successful_trades} fractions', 'success')
            else:
                flash('No fractions were traded', 'error')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Trade failed: {str(e)}', 'error')
        
        return redirect(url_for('dashboard.trade_fractions'))
    
    # GET request - show trade form
    user_id = session['user_id']
    
    # Get user's owned fractions
    user_fractions = db.session.query(
        Ownership.fractions_fraction_id,
        Fraction.fraction_no,
        Fraction.fraction_value,
        Asset.name.label('asset_name'),
        Ownership.acquired_at
    ).join(
        Fraction, Ownership.fractions_fraction_id == Fraction.fraction_id
    ).join(
        Asset, Fraction.assets_asset_id == Asset.asset_id
    ).filter(
        Ownership.users_user_id == user_id
    ).order_by(Asset.name, Fraction.fraction_no).all()
    
    # Get all users for dropdown
    all_users = User.query.order_by(User.username).all()
    
    return render_template('trade.html',
                         user_fractions=user_fractions,
                         all_users=all_users,
                         username=session.get('username'))


@bp.route('/browse')
@require_login
def browse_fractions():
    """Browse available fractions for trading"""
    user_id = session['user_id']
    
    # Get query parameters
    asset_id = request.args.get('asset_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
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
        Ownership.users_user_id != user_id
    )
    
    # Apply asset filter if specified
    if asset_id:
        query = query.filter(Asset.asset_id == asset_id)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    fractions = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Get available assets for filter dropdown
    available_assets = db.session.query(
        Asset.asset_id, Asset.name
    ).join(
        Fraction, Asset.asset_id == Fraction.assets_asset_id
    ).join(
        Ownership, Fraction.fraction_id == Ownership.fractions_fraction_id
    ).filter(
        Ownership.users_user_id != user_id
    ).distinct().all()
    
    return render_template('browse.html',
                         fractions=fractions,
                         available_assets=available_assets,
                         total_count=total_count,
                         page=page,
                         per_page=per_page,
                         asset_id=asset_id,
                         username=session.get('username'))


@bp.route('/trade_requests')
@require_login
def trade_requests():
    """Manage trade requests (incoming and outgoing)"""
    user_id = session['user_id']
    request_type = request.args.get('type', 'all')
    
    # Build query for trade requests
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
        Fraction.fraction_no,
        Fraction.fraction_value
    ).join(
        Fraction, TradeRequest.fraction_id == Fraction.fraction_id
    ).join(
        Asset, Fraction.assets_asset_id == Asset.asset_id
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
    requests = query.order_by(TradeRequest.requested_at.desc()).all()
    
    # Format request data
    requests_data = []
    for req in requests:
        from_user = User.query.get(req.from_user_id)
        to_user = User.query.get(req.to_user_id)
        
        requests_data.append({
            'request_id': req.request_id,
            'fraction_id': req.fraction_id,
            'fraction_no': req.fraction_no,
            'fraction_value': float(req.fraction_value) if req.fraction_value else 0.0,
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
            'requested_at': req.requested_at,
            'responded_at': req.responded_at,
            'notes': req.notes,
            'is_incoming': req.to_user_id == user_id,
            'is_outgoing': req.from_user_id == user_id
        })
    
    return render_template('trade_requests.html',
                         requests=requests_data,
                         request_type=request_type,
                         username=session.get('username'))


@bp.route('/submit_trade_request', methods=['POST'])
@require_login
def submit_trade_request():
    """Submit a new trade request"""
    try:
        fraction_id = int(request.form.get('fraction_id'))
        notes = request.form.get('notes', '')
        
        # Create trade request via API
        api_url = f'http://localhost:5001/api/v1/trading/request_trade'
        
        # Get current user ID for the request
        current_user_id = session['user_id']
        
        # We need to determine who to send the request to (current owner)
        current_ownership = Ownership.query.filter_by(
            fractions_fraction_id=fraction_id
        ).order_by(Ownership.acquired_at.desc()).first()
        
        if not current_ownership:
            flash('No current owner found for this fraction', 'error')
            return redirect(url_for('dashboard.browse_fractions'))
        
        from_user_id = current_ownership.users_user_id
        
        # Prepare request data
        request_data = {
            'fraction_id': fraction_id,
            'to_user_id': from_user_id,  # The current owner
            'notes': notes
        }
        
        # Make API call
        response = requests.post(
            api_url,
            json=request_data,
            headers={'Content-Type': 'application/json'},
            cookies=request.cookies
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                flash('Trade request submitted successfully', 'success')
            else:
                flash(f'Error: {result.get("message", "Unknown error")}', 'error')
        else:
            flash('Failed to submit trade request', 'error')
            
    except Exception as e:
        flash(f'Error submitting trade request: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.browse_fractions'))


@bp.route('/respond_trade_request', methods=['POST'])
@require_login
def respond_trade_request():
    """Respond to a trade request (approve or deny)"""
    try:
        request_id = request.form.get('request_id')
        action = request.form.get('action')  # 'approve' or 'deny'
        
        if not request_id or not action:
            flash('Missing required parameters', 'error')
            return redirect(url_for('dashboard.trade_requests'))
        
        # Create response via API
        api_url = f'http://localhost:5001/api/v1/trading/respond_request'
        
        request_data = {
            'request_id': request_id,
            'action': action
        }
        
        # Make API call
        response = requests.post(
            api_url,
            json=request_data,
            headers={'Content-Type': 'application/json'},
            cookies=request.cookies
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                flash(f'Trade request {action}d successfully', 'success')
            else:
                flash(f'Error: {result.get("message", "Unknown error")}', 'error')
        else:
            flash('Failed to respond to trade request', 'error')
            
    except Exception as e:
        flash(f'Error responding to trade request: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.trade_requests'))