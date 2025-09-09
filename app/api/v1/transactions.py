"""
Transactions/Ledger API endpoints
"""

from flask import Blueprint, request
from app.models import Transaction, Fraction, User, Asset
from app.api.errors import NotFoundError, ValidationError, success_response
from app.api.decorators import require_json, require_fields, handle_exceptions, paginate
from app import db
from datetime import datetime

bp = Blueprint('transactions', __name__, url_prefix='/transactions')


@bp.route('/', methods=['GET'])
@handle_exceptions
@paginate(page=1, per_page=50)
def get_transactions(page=1, per_page=50):
    """
    Get all transactions with pagination
    GET /api/v1/transactions?page=1&per_page=50
    """
    transactions = Transaction.query.order_by(Transaction.trade_time.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    transactions_data = [transaction.to_dict() for transaction in transactions.items]
    
    return success_response(
        data={
            'transactions': transactions_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': transactions.total,
                'pages': transactions.pages,
                'has_next': transactions.has_next,
                'has_prev': transactions.has_prev
            }
        },
        message="Transactions retrieved successfully"
    )


@bp.route('/trade', methods=['POST'])
@require_json
@require_fields('fraction_id', 'buyer_id', 'seller_id', 'quantity', 'price')
@handle_exceptions
def create_trade():
    """
    Create a new trade transaction
    POST /api/v1/transactions/trade
    Body: {
        "fraction_id": 1,
        "buyer_id": 2,
        "seller_id": 3,
        "quantity": 10,
        "price": 100.50
    }
    """
    data = request.get_json()
    
    # Validate fraction exists
    fraction = Fraction.query.get(data['fraction_id'])
    if not fraction:
        raise NotFoundError("Fraction not found")
    
    # Validate users exist
    buyer = User.query.get(data['buyer_id'])
    if not buyer:
        raise NotFoundError("Buyer not found")
    
    seller = User.query.get(data['seller_id'])
    if not seller:
        raise NotFoundError("Seller not found")
    
    # Validate quantity and price
    quantity = data['quantity']
    price = data['price']
    
    if quantity <= 0:
        raise ValidationError("Quantity must be positive")
    
    if price <= 0:
        raise ValidationError("Price must be positive")
    
    # Check if seller has enough fractions
    from app.models import Ownership
    seller_ownership = Ownership.query.filter_by(
        users_user_id=data['seller_id'],
        fractions_fraction_id=data['fraction_id']
    ).first()
    
    if not seller_ownership or seller_ownership.quantity < quantity:
        raise ValidationError("Seller does not have enough fractions")
    
    try:
        # Create transaction record
        transaction = Transaction(
            fractions_fraction_id=data['fraction_id'],
            from_users_user_id=data['seller_id'],
            to_users_user_id=data['buyer_id'],
            quantity=quantity,
            unit_price=price,
            trade_time=datetime.utcnow()
        )
        
        db.session.add(transaction)
        
        # Update ownership records
        # Reduce seller's ownership
        seller_ownership.quantity -= quantity
        if seller_ownership.quantity == 0:
            db.session.delete(seller_ownership)
        
        # Add or update buyer's ownership
        buyer_ownership = Ownership.query.filter_by(
            users_user_id=data['buyer_id'],
            fractions_fraction_id=data['fraction_id']
        ).first()
        
        if buyer_ownership:
            buyer_ownership.quantity += quantity
        else:
            buyer_ownership = Ownership(
                users_user_id=data['buyer_id'],
                fractions_fraction_id=data['fraction_id'],
                quantity=quantity,
                acquired_at=datetime.utcnow()
            )
            db.session.add(buyer_ownership)
        
        db.session.commit()
        
        return success_response(
            data=transaction.to_dict(),
            message="Trade created successfully",
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        raise ValidationError(f"Failed to create trade: {str(e)}")


@bp.route('/<int:transaction_id>', methods=['GET'])
@handle_exceptions
def get_transaction(transaction_id):
    """
    Get specific transaction by ID
    GET /api/v1/transactions/<transaction_id>
    """
    transaction = Transaction.query.get(transaction_id)
    
    if not transaction:
        raise NotFoundError("Transaction not found")
    
    return success_response(
        data=transaction.to_dict(),
        message="Transaction retrieved successfully"
    )


@bp.route('/user/<int:user_id>', methods=['GET'])
@handle_exceptions
@paginate(page=1, per_page=50)
def get_user_transactions(user_id, page=1, per_page=50):
    """
    Get all transactions for a specific user
    GET /api/v1/transactions/user/<user_id>?page=1&per_page=50
    """
    # Verify user exists
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError("User not found")
    
    # Get transactions where user is buyer or seller
    transactions = Transaction.query.filter(
        (Transaction.from_users_user_id == user_id) | (Transaction.to_users_user_id == user_id)
    ).order_by(Transaction.trade_time.desc())\
    .paginate(page=page, per_page=per_page, error_out=False)
    
    transactions_data = [transaction.to_dict() for transaction in transactions.items]
    
    return success_response(
        data={
            'user_id': user_id,
            'transactions': transactions_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': transactions.total,
                'pages': transactions.pages,
                'has_next': transactions.has_next,
                'has_prev': transactions.has_prev
            }
        },
        message="User transactions retrieved successfully"
    )


@bp.route('/fraction/<int:fraction_id>', methods=['GET'])
@handle_exceptions
@paginate(page=1, per_page=50)
def get_fraction_transactions(fraction_id, page=1, per_page=50):
    """
    Get all transactions for a specific fraction
    GET /api/v1/transactions/fraction/<fraction_id>?page=1&per_page=50
    """
    # Verify fraction exists
    fraction = Fraction.query.get(fraction_id)
    if not fraction:
        raise NotFoundError("Fraction not found")
    
    # Get transactions for this fraction
    transactions = Transaction.query.filter_by(fractions_fraction_id=fraction_id)\
        .order_by(Transaction.trade_time.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    transactions_data = [transaction.to_dict() for transaction in transactions.items]
    
    return success_response(
        data={
            'fraction_id': fraction_id,
            'transactions': transactions_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': transactions.total,
                'pages': transactions.pages,
                'has_next': transactions.has_next,
                'has_prev': transactions.has_prev
            }
        },
        message="Fraction transactions retrieved successfully"
    )


@bp.route('/stats', methods=['GET'])
@handle_exceptions
def get_transaction_stats():
    """
    Get transaction statistics
    GET /api/v1/transactions/stats
    """
    from sqlalchemy import func
    
    # Get basic stats
    total_transactions = Transaction.query.count()
    total_volume = db.session.query(func.sum(Transaction.quantity * Transaction.unit_price)).scalar() or 0
    
    # Get recent activity (last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_transactions = Transaction.query.filter(
        Transaction.trade_time >= thirty_days_ago
    ).count()
    
    # Get top traded fractions
    top_fractions = db.session.query(
        Transaction.fractions_fraction_id,
        func.count(Transaction.transaction_id).label('trade_count'),
        func.sum(Transaction.quantity).label('total_quantity')
    ).group_by(Transaction.fractions_fraction_id)\
    .order_by(func.count(Transaction.transaction_id).desc())\
    .limit(10).all()
    
    stats = {
        'total_transactions': total_transactions,
        'total_volume': float(total_volume),
        'recent_transactions_30_days': recent_transactions,
        'top_traded_fractions': [
            {
                'fraction_id': fraction_id,
                'trade_count': trade_count,
                'total_quantity': total_quantity
            }
            for fraction_id, trade_count, total_quantity in top_fractions
        ]
    }
    
    return success_response(
        data=stats,
        message="Transaction statistics retrieved successfully"
    )