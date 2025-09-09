from flask import Blueprint, request, jsonify
from app.models import Transaction, User, Fraction, Asset, Ownership
from app.utils import calculate_fraction_value
from app import db
from datetime import datetime

bp = Blueprint('ledger', __name__)

@bp.route('/trade', methods=['POST'])
def create_trade():
    """
    Create a transaction record in the ledger for a fraction being traded
    POST /trade
    Body: {
        "from_user_id": 1,
        "to_user_id": 2,
        "fraction_id": 123,
        "quantity": 1,
        "unit_price": 150.50,
        "currency": "USD",
        "notes": "Optional trade notes"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['from_user_id', 'to_user_id', 'fraction_id', 'quantity', 'unit_price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        from_user_id = data['from_user_id']
        to_user_id = data['to_user_id']
        fraction_id = data['fraction_id']
        quantity = data['quantity']
        unit_price = data['unit_price']
        currency = data.get('currency', 'USD')
        notes = data.get('notes', '')
        
        # Validate users exist
        from_user = User.query.get(from_user_id)
        to_user = User.query.get(to_user_id)
        
        if not from_user:
            return jsonify({'error': f'From user {from_user_id} not found'}), 404
        if not to_user:
            return jsonify({'error': f'To user {to_user_id} not found'}), 404
        
        # Validate fraction exists
        fraction = Fraction.query.get(fraction_id)
        if not fraction:
            return jsonify({'error': f'Fraction {fraction_id} not found'}), 404
        
        # Validate that from_user owns the fraction
        ownership = Ownership.query.filter_by(
            Users_user_id=from_user_id,
            Fractions_fraction_id=fraction_id
        ).first()
        
        if not ownership:
            return jsonify({'error': f'User {from_user_id} does not own fraction {fraction_id}'}), 400
        
        # Validate quantity
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
        
        # Validate unit price
        if unit_price <= 0:
            return jsonify({'error': 'Unit price must be positive'}), 400
        
        # Create transaction record
        transaction = Transaction(
            quantity=quantity,
            unit_price=unit_price,
            currency=currency,
            trade_time=datetime.utcnow(),
            notes=notes,
            from_Users_user_id=from_user_id,
            to_Users_user_id=to_user_id,
            Fractions_fraction_id=fraction_id,
            Fractions_Assets_asset_id=fraction.Assets_asset_id
        )
        
        db.session.add(transaction)
        
        # Update ownership - transfer the fraction
        ownership.Users_user_id = to_user_id
        ownership.acquired_at = datetime.utcnow()
        
        db.session.commit()
        
        # Return transaction details
        return jsonify({
            'message': 'Trade completed successfully',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create trade: {str(e)}'}), 500

@bp.route('/transactions', methods=['GET'])
def get_transactions():
    """
    Get transaction history
    GET /transactions
    Query params: 
    - user_id (optional): filter by user
    - asset_id (optional): filter by asset
    - limit (optional, default 50): number of records to return
    """
    try:
        # Get query parameters
        user_id = request.args.get('user_id', type=int)
        asset_id = request.args.get('asset_id', type=int)
        limit = request.args.get('limit', 50, type=int)
        
        if limit > 1000:  # Prevent excessive data requests
            limit = 1000
        
        # Build query
        query = Transaction.query
        
        if user_id:
            query = query.filter(
                (Transaction.from_Users_user_id == user_id) |
                (Transaction.to_Users_user_id == user_id)
            )
        
        if asset_id:
            query = query.filter(Transaction.Fractions_Assets_asset_id == asset_id)
        
        # Order by trade time (most recent first)
        transactions = query.order_by(Transaction.trade_time.desc()).limit(limit).all()
        
        # Format response
        transactions_data = []
        for transaction in transactions:
            transaction_data = transaction.to_dict()
            
            # Add user and asset names for better readability
            from_user = User.query.get(transaction.from_Users_user_id)
            to_user = User.query.get(transaction.to_Users_user_id)
            asset = Asset.query.get(transaction.Fractions_Assets_asset_id)
            
            transaction_data['from_username'] = from_user.username if from_user else None
            transaction_data['to_username'] = to_user.username if to_user else None
            transaction_data['asset_name'] = asset.name if asset else None
            
            transactions_data.append(transaction_data)
        
        return jsonify({
            'transactions': transactions_data,
            'count': len(transactions_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch transactions: {str(e)}'}), 500

@bp.route('/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """
    Get specific transaction details
    GET /transactions/<transaction_id>
    """
    try:
        transaction = Transaction.query.get(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        transaction_data = transaction.to_dict()
        
        # Add additional details
        from_user = User.query.get(transaction.from_Users_user_id)
        to_user = User.query.get(transaction.to_Users_user_id)
        asset = Asset.query.get(transaction.Fractions_Assets_asset_id)
        fraction = Fraction.query.get(transaction.Fractions_fraction_id)
        
        transaction_data['from_username'] = from_user.username if from_user else None
        transaction_data['to_username'] = to_user.username if to_user else None
        transaction_data['asset_name'] = asset.name if asset else None
        transaction_data['fraction_no'] = fraction.fraction_no if fraction else None
        
        return jsonify(transaction_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch transaction: {str(e)}'}), 500