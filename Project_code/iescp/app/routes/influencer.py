from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import AdRequest
from app.forms import AdRequestResponseForm

influencer_bp = Blueprint('influencer_bp', __name__)

@influencer_bp.route('/influencer')
@login_required
def influencer_dashboard():
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()
    return render_template('influencer_dashboard.html', ad_requests=ad_requests)

@influencer_bp.route('/ad_request/<int:ad_request_id>/respond', methods=['GET', 'POST'])
@login_required
def respond_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if ad_request.influencer_id != current_user.id:
        abort(403)
    form = AdRequestResponseForm()
    if form.validate_on_submit():
        ad_request.status = form.status.data
        ad_request.messages = form.messages.data
        ad_request.payment_amount = form.payment_amount.data
        db.session.commit()
        flash('Your response has been submitted!', 'success')
        return redirect(url_for('influencer_bp.influencer_dashboard'))
    elif request.method == 'GET':
        form.status.data = ad_request.status
        form.messages.data = ad_request.messages
        form.payment_amount.data = ad_request.payment_amount
    return render_template('respond_ad_request.html', title='Respond Ad Request', form=form, legend='Respond Ad Request')
