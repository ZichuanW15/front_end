from flask import Blueprint, request, jsonify
from app.models import Asset, ValueHistory, Fraction, Ownership
from app.utils import get_asset_current_value, get_ownership_snapshot, validate_date_format
from app import db
from datetime import datetime

bp = Blueprint('asset', __name__)

@bp.route('/assets/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    """
    Get current asset info and value
    GET /assets/<asset_id>
    """
    try:
        asset = Asset.query.get(asset_id)
        
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # Get current asset value
        current_value = get_asset_current_value(asset_id)
        
        # Get current fraction value
        from app.utils import calculate_fraction_value
        fraction_value = calculate_fraction_value(asset_id)
        
        asset_data = asset.to_dict()
        asset_data['current_value'] = current_value
        asset_data['fraction_value'] = float(fraction_value)
        
        return jsonify(asset_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch asset: {str(e)}'}), 500

@bp.route('/assets/<int:asset_id>/history', methods=['GET'])
def get_asset_history(asset_id):
    """
    Get historical asset value records
    GET /assets/<asset_id>/history
    Query params: limit (optional, default 100)
    """
    try:
        # Check if asset exists
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # Get limit from query params
        limit = request.args.get('limit', 100, type=int)
        if limit > 1000:  # Prevent excessive data requests
            limit = 1000
        
        # Get value history
        history = ValueHistory.query.filter_by(
            Assets_asset_id=asset_id
        ).order_by(ValueHistory.update_time.desc()).limit(limit).all()
        
        return jsonify({
            'asset_id': asset_id,
            'asset_name': asset.name,
            'history': [record.to_dict() for record in history]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch asset history: {str(e)}'}), 500

@bp.route('/assets/<int:asset_id>/snapshot', methods=['GET'])
def get_asset_snapshot(asset_id):
    """
    Get ownership snapshot at a specific time
    GET /assets/<asset_id>/snapshot?at=YYYY-MM-DD
    """
    try:
        # Check if asset exists
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # Get date parameter
        at_date = request.args.get('at')
        if not at_date:
            return jsonify({'error': 'Date parameter "at" is required (format: YYYY-MM-DD)'}), 400
        
        # Validate date format
        parsed_date = validate_date_format(at_date)
        if not parsed_date:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get ownership snapshot
        ownerships = get_ownership_snapshot(asset_id, parsed_date)
        
        # Get asset value at that time
        value_at_date = ValueHistory.query.filter(
            ValueHistory.Assets_asset_id == asset_id,
            ValueHistory.update_time <= parsed_date
        ).order_by(ValueHistory.update_time.desc()).first()
        
        # Format response
        snapshot_data = {
            'asset_id': asset_id,
            'asset_name': asset.name,
            'snapshot_date': at_date,
            'asset_value_at_date': value_at_date.asset_value if value_at_date else None,
            'ownership': []
        }
        
        # Group ownership by user
        user_ownership = {}
        for ownership in ownerships:
            user_id = ownership.Users_user_id
            if user_id not in user_ownership:
                user_ownership[user_id] = {
                    'user_id': user_id,
                    'fraction_count': 0,
                    'fraction_ids': []
                }
            user_ownership[user_id]['fraction_count'] += 1
            user_ownership[user_id]['fraction_ids'].append(ownership.Fractions_fraction_id)
        
        snapshot_data['ownership'] = list(user_ownership.values())
        
        return jsonify(snapshot_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch asset snapshot: {str(e)}'}), 500

@bp.route('/assets', methods=['GET'])
def get_all_assets():
    """
    Get all assets (for testing purposes)
    GET /assets
    """
    try:
        assets = Asset.query.all()
        return jsonify({
            'assets': [asset.to_dict() for asset in assets]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch assets: {str(e)}'}), 500