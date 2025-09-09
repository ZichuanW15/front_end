from flask import Blueprint, request, jsonify
from app.models import User, Ownership, Fraction, Asset
from app.utils import get_user_fractions_at_date, validate_date_format, calculate_fraction_value
from app import db
from datetime import datetime

bp = Blueprint('user', __name__)

@bp.route('/owners/<int:user_id>/fractions', methods=['GET'])
def get_user_fractions(user_id):
    """
    Get all current fractions owned by a user
    GET /owners/<user_id>/fractions
    Query params: at (optional, format: YYYY-MM-DD) - get fractions at specific date
    """
    try:
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get date parameter if provided
        at_date = request.args.get('at')
        parsed_date = None
        
        if at_date:
            parsed_date = validate_date_format(at_date)
            if not parsed_date:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get user's fractions
        ownerships = get_user_fractions_at_date(user_id, parsed_date)
        
        # Format response with fraction details
        fractions_data = []
        for ownership in ownerships:
            fraction = Fraction.query.get(ownership.Fractions_fraction_id)
            asset = Asset.query.get(ownership.Fractions_Assets_asset_id)
            
            if fraction and asset:
                # Calculate current fraction value
                current_fraction_value = calculate_fraction_value(asset.asset_id)
                
                fraction_info = {
                    'fraction_id': fraction.fraction_id,
                    'fraction_no': fraction.fraction_no,
                    'asset_id': asset.asset_id,
                    'asset_name': asset.name,
                    'asset_status': asset.status,
                    'fraction_value': float(fraction.fraction_value) if fraction.fraction_value else 0.0,
                    'current_fraction_value': float(current_fraction_value),
                    'acquired_at': ownership.acquired_at.isoformat() if ownership.acquired_at else None
                }
                fractions_data.append(fraction_info)
        
        # Group by asset for better organization
        assets_summary = {}
        total_value = 0.0
        
        for fraction_info in fractions_data:
            asset_id = fraction_info['asset_id']
            if asset_id not in assets_summary:
                assets_summary[asset_id] = {
                    'asset_id': asset_id,
                    'asset_name': fraction_info['asset_name'],
                    'asset_status': fraction_info['asset_status'],
                    'fraction_count': 0,
                    'total_value': 0.0,
                    'fractions': []
                }
            
            assets_summary[asset_id]['fraction_count'] += 1
            assets_summary[asset_id]['total_value'] += fraction_info['current_fraction_value']
            assets_summary[asset_id]['fractions'].append(fraction_info)
            total_value += fraction_info['current_fraction_value']
        
        response_data = {
            'user_id': user_id,
            'username': user.username,
            'snapshot_date': at_date if at_date else 'current',
            'total_fractions': len(fractions_data),
            'total_portfolio_value': total_value,
            'assets': list(assets_summary.values())
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch user fractions: {str(e)}'}), 500

@bp.route('/owners/<int:user_id>/portfolio', methods=['GET'])
def get_user_portfolio(user_id):
    """
    Get user portfolio summary
    GET /owners/<user_id>/portfolio
    """
    try:
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get current ownership
        ownerships = get_user_fractions_at_date(user_id)
        
        # Calculate portfolio metrics
        portfolio_data = {
            'user_id': user_id,
            'username': user.username,
            'total_assets': 0,
            'total_fractions': len(ownerships),
            'total_value': 0.0,
            'asset_breakdown': {}
        }
        
        # Group by asset
        for ownership in ownerships:
            asset = Asset.query.get(ownership.Fractions_Assets_asset_id)
            if asset:
                asset_id = asset.asset_id
                
                if asset_id not in portfolio_data['asset_breakdown']:
                    portfolio_data['asset_breakdown'][asset_id] = {
                        'asset_id': asset_id,
                        'asset_name': asset.name,
                        'asset_status': asset.status,
                        'fraction_count': 0,
                        'total_value': 0.0
                    }
                
                portfolio_data['asset_breakdown'][asset_id]['fraction_count'] += 1
                
                # Calculate value for this fraction
                fraction_value = calculate_fraction_value(asset_id)
                portfolio_data['asset_breakdown'][asset_id]['total_value'] += float(fraction_value)
                portfolio_data['total_value'] += float(fraction_value)
        
        portfolio_data['total_assets'] = len(portfolio_data['asset_breakdown'])
        portfolio_data['asset_breakdown'] = list(portfolio_data['asset_breakdown'].values())
        
        return jsonify(portfolio_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch user portfolio: {str(e)}'}), 500