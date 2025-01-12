from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Campaign
from app.forms import CampaignForm

sponsor_bp = Blueprint('sponsor_bp', __name__)

@sponsor_bp.route('/sponsordashboard')
@jwt_required()
def sponsor_dashboard():
    current_user_id = get_jwt_identity()
    campaigns = Campaign.query.filter_by(sponsor_id=current_user_id).all()
    return render_template('sponsor_dashboard.html', campaigns=campaigns)

@sponsor_bp.route('/campaign/new', methods=['GET', 'POST'])
@jwt_required()
def new_campaign():
    form = CampaignForm()
    if form.validate_on_submit():
        current_user_id = get_jwt_identity()
        campaign = Campaign(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            visibility=form.visibility.data,
            goals=form.goals.data,
            sponsor_id=current_user_id
        )
        db.session.add(campaign)
        db.session.commit()
        flash('Your campaign has been created!', 'success')
        return redirect(url_for('sponsor_bp.sponsor_dashboard'))
    return render_template('create_campaign.html', title='New Campaign', form=form, legend='New Campaign')

@sponsor_bp.route('/campaign/<int:campaign_id>/update', methods=['GET', 'POST'])
@jwt_required()
def update_campaign(campaign_id):
    current_user_id = get_jwt_identity()
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id != current_user_id:
        abort(403)
    form = CampaignForm()
    if form.validate_on_submit():
        campaign.name = form.name.data
        campaign.description = form.description.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        campaign.budget = form.budget.data
        campaign.visibility = form.visibility.data
        campaign.goals = form.goals.data
        db.session.commit()
        flash('Your campaign has been updated!', 'success')
        return redirect(url_for('sponsor_bp.sponsor_dashboard'))
    elif request.method == 'GET':
        form.name.data = campaign.name
        form.description.data = campaign.description
        form.start_date.data = campaign.start_date
        form.end_date.data = campaign.end_date
        form.budget.data = campaign.budget
        form.visibility.data = campaign.visibility
        form.goals.data = campaign.goals
    return render_template('create_campaign.html', title='Update Campaign', form=form, legend='Update Campaign')
