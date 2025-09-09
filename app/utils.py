from datetime import datetime
from decimal import Decimal
from app.models import Asset, ValueHistory, Fraction, Ownership
from app import db

def calculate_fraction_value(asset_id):
    """
    Calculate the current value of a fraction for a given asset.
    Formula: latest_asset_value / total_fractions
    """
    try:
        # Get the latest asset value
        latest_value_record = ValueHistory.query.filter_by(
            assets_asset_id=asset_id
        ).order_by(ValueHistory.update_time.desc()).first()
        
        if not latest_value_record:
            return Decimal('0.00')
        
        # Get the asset to find total fractions
        asset = Asset.query.get(asset_id)
        if not asset or not asset.available_fractions:
            return Decimal('0.00')
        
        # Calculate fraction value
        fraction_value = Decimal(latest_value_record.asset_value) / Decimal(asset.available_fractions)
        return fraction_value.quantize(Decimal('0.01'))
        
    except Exception as e:
        print(f"Error calculating fraction value: {e}")
        return Decimal('0.00')

def get_asset_current_value(asset_id):
    """
    Get the current value of an asset from the latest ValueHistory record.
    """
    latest_value = ValueHistory.query.filter_by(
        assets_asset_id=asset_id
    ).order_by(ValueHistory.update_time.desc()).first()
    
    return latest_value.asset_value if latest_value else 0

def get_ownership_snapshot(asset_id, at_date=None):
    """
    Get ownership snapshot for an asset at a specific date.
    If no date provided, returns current ownership.
    """
    query = Ownership.query.filter_by(fractions_assets_asset_id=asset_id)
    
    if at_date:
        # Convert string date to datetime if needed
        if isinstance(at_date, str):
            at_date = datetime.fromisoformat(at_date.replace('Z', '+00:00'))
        query = query.filter(Ownership.acquired_at <= at_date)
    
    return query.all()

def get_user_fractions_at_date(user_id, at_date=None):
    """
    Get all fractions owned by a user at a specific date.
    If no date provided, returns current ownership.
    """
    query = Ownership.query.filter_by(Users_user_id=user_id)
    
    if at_date:
        # Convert string date to datetime if needed
        if isinstance(at_date, str):
            at_date = datetime.fromisoformat(at_date.replace('Z', '+00:00'))
        query = query.filter(Ownership.acquired_at <= at_date)
    
    return query.all()

def validate_date_format(date_string):
    """
    Validate and parse date string in YYYY-MM-DD format.
    Returns datetime object if valid, None otherwise.
    """
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        return None

def format_currency(amount, currency='USD'):
    """
    Format amount as currency string.
    """
    if currency == 'USD':
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"