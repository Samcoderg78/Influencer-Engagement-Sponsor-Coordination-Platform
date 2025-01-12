from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, cache
from app.models import User, Campaign, AdRequest, InfRequest
from app.utils.decorators import admin_required
from functools import wraps
admin_bp = Blueprint('admin_bp', __name__)

# Admin Dashboard: Fetch all users, campaigns, and ad requests, plus statistics
# Ensure that the admin_required decorator is implemented correctly
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        # Fetch user identity from JWT
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Check if the user is an admin
        if user is None or user.role != 'admin':
            return jsonify({"message": "Access forbidden: Admins only."}), 403
        
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/admindashboard', methods=['GET'])
@jwt_required()
@admin_required
@cache.cached(timeout=360)
def admin_dashboard():
    # Fetch all relevant data
    users = User.query.filter(User.role != 'admin').all()
    campaigns = Campaign.query.all()
    ad_requests = AdRequest.query.all()
    inf_requests = InfRequest.query.all()

    # Statistics
    active_users = User.query.filter_by(active=True).filter(User.role != 'admin').count()  
    flagged_users = User.query.filter_by(flagged=True).filter(User.role != 'admin').count()
    active_campaigns = Campaign.query.filter_by(status='active').count()
    flagged_campaigns = Campaign.query.filter_by(flagged=True).count()
    public_campaigns = Campaign.query.filter_by(visibility='public').count()
    private_campaigns = Campaign.query.filter_by(visibility='private').count()

    response = {
        'users': [user.to_dict() for user in users],
        'campaigns': [
            {**campaign.to_dict(), 'sponsor_name': campaign.sponsor.username}
            for campaign in campaigns
        ],
        'ad_requests': [ad_request.to_dict() for ad_request in ad_requests],
        'inf_requests': [
            {
                **inf_request.to_dict(),
                'sponsor_name': inf_request.campaign.sponsor.username  
            }
            for inf_request in inf_requests
        ],
        'statistics': {
            'active_users': active_users,
            'flagged_users': flagged_users,
            'active_campaigns': active_campaigns,
            'flagged_campaigns': flagged_campaigns,
            'public_campaigns': public_campaigns,
            'private_campaigns': private_campaigns,
        }
    }

    return jsonify(response), 200

# Approve sponsor
@admin_bp.route('/admin/approve_user/<int:user_id>', methods=['POST'])
@jwt_required()
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'sponsor' or 'influencer' and not user.active:
        user.active = True
        db.session.commit()
        return jsonify({'message': f'Sponsor {user.username} approved successfully.'}), 200
    return jsonify({'error': 'User cannot be approved or is already approved.'}), 400

# Flag user
@admin_bp.route('/admin/flag_user/<int:user_id>', methods=['POST'])
@jwt_required()
@admin_required
def flag_user(user_id):
    user = User.query.get_or_404(user_id)
    if not user.flagged:
        user.flagged = True
        db.session.commit()
        return jsonify({'message': f'User {user.name} flagged successfully.'}), 200
    return jsonify({'error': 'User is already flagged.'}), 400

# Flag campaign
@admin_bp.route('/admin/flag_campaign/<int:campaign_id>', methods=['POST'])
@jwt_required()
@admin_required
def flag_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if not campaign.flagged:
        campaign.flagged = True
        db.session.commit()
        return jsonify({'message': f'Campaign {campaign.title} flagged successfully.'}), 200
    return jsonify({'error': 'Campaign is already flagged.'}), 400
