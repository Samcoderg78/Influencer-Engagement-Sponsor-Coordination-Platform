from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import AdRequest, Campaign, User, InfRequest, Message
from datetime import datetime


ad_requests_bp = Blueprint('ad_requests_bp', __name__)


@ad_requests_bp.route('/campaigns/<int:campaign_id>/influencers/available', methods=['GET'])
@jwt_required()
def get_available_influencers(campaign_id):
    current_user_id = get_jwt_identity()
    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.sponsor_id != current_user_id:
        return jsonify({"message": "Unauthorized"}), 403

    influencers = User.query.filter(User.role == 'influencer').all()

    result = []
    for influencer in influencers:
        ad_request = AdRequest.query.filter_by(campaign_id=campaign_id, influencer_id=influencer.id).first()
        status = ad_request.status if ad_request else "Not Sent"
        request_sent = True if ad_request else False  # Check if request was sent
        result.append({
            "id": influencer.id,
            "name": influencer.username,
            "status": status,
            "request_sent": request_sent
        })

    return jsonify(result), 200


@ad_requests_bp.after_request
def handle_options_request(response):
    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Headers", "Authorization, Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response



# Send AdRequest to influencer
@ad_requests_bp.route('/ad_requests', methods=['POST'])
@jwt_required()
def send_ad_request():
    data = request.get_json()
    campaign_id = data.get('campaign_id')
    influencer_id = data.get('influencer_id')

    current_user_id = get_jwt_identity()

    # Check if the campaign belongs to the sponsor
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.sponsor_id != current_user_id:
        return jsonify({"message": "Unauthorized"}), 403

    # Check if the request is already sent
    existing_request = AdRequest.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    if existing_request:
        return jsonify({"message": "Request already sent"}), 400

    # Create and send new ad request
    new_request = AdRequest(
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        status="Pending",
        requirements="Default requirements",  # Default, adjust if necessary
    )
    db.session.add(new_request)
    db.session.commit()

    return jsonify({"message": "Ad request sent successfully"}), 201

#Collaboration Requests
@ad_requests_bp.route('/ad_requests/influencer', methods=['GET'])
@jwt_required()
def get_collaboration_requests():
    current_user_id = get_jwt_identity()

    # Fetch ad requests for the current influencer
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user_id).all()

    # Prepare the response data
    requests_data = []
    for request in ad_requests:
        campaign = Campaign.query.get(request.campaign_id)
        sponsor = User.query.get(campaign.sponsor_id)

        budget = request.budget if request.budget is not None else campaign.budget

        requests_data.append({
            'id': request.id,
            'campaign_name': campaign.name,
            'campaign_description': campaign.description,
            'campaign_id': campaign.id, 
            'sponsor_name': sponsor.username,
            'budget': budget,
            'status': request.status
        })

    return jsonify(requests_data), 200


# Accept AdRequest by influencer
@ad_requests_bp.route('/ad_requests/<int:request_id>/accept', methods=['POST'])
@jwt_required()
def accept_ad_request(request_id):
    current_user_id = get_jwt_identity()

    # Find the ad request by ID
    ad_request = AdRequest.query.get_or_404(request_id)

    # Ensure the current user is the influencer for this request
    if ad_request.influencer_id != current_user_id:
        return jsonify({"message": "Unauthorized"}), 403

    # Update the status to 'Accepted'
    ad_request.status = "Accepted"
    db.session.commit()

    return jsonify({"message": "Ad request accepted successfully"}), 200


# Reject AdRequest
@ad_requests_bp.route('/ad_requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_ad_request(request_id):
    current_user_id = get_jwt_identity()

    # Find the ad request by ID
    ad_request = AdRequest.query.get_or_404(request_id)

    # Ensure the current user is the influencer for this request
    if ad_request.influencer_id != current_user_id:
        return jsonify({"message": "Unauthorized"}), 403

    # Update the status to 'Rejected'
    ad_request.status = "Rejected"
    db.session.commit()

    return jsonify({"message": "Ad request rejected successfully"}), 200


@ad_requests_bp.route('/influencer/ad-requests', methods=['GET'])
@jwt_required() 
def get_influencer_ad_requests():
    influencer_id = get_jwt_identity()
    
    if influencer_id is None:
        return jsonify({'error': 'Influencer ID required'}), 400
    
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer_id).all()
    return jsonify([request.to_dict() for request in ad_requests]), 200

@ad_requests_bp.route('/campaigns/<int:campaign_id>/influencer/status', methods=['GET'])
@jwt_required()
def get_influencer_request_status(campaign_id):
    influencer_id = get_jwt_identity()
    
    # Fetch the request status from the InfRequest table
    request = InfRequest.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()

    if request:
        return jsonify({'status': request.status}), 200
    else:
        return jsonify({'status': 'Not Requested'}), 200

@ad_requests_bp.route('/influencer/send-request', methods=['POST'])
@jwt_required()  
def send_ad_request_to_sponsor():
    data = request.get_json()
    influencer_id = get_jwt_identity()
    campaign_id = data.get('campaign_id')
    campaign_name = data.get('campaign_name')
    campaign_description = data.get('campaign_description')
    budget = data.get('budget')
    
    existing_request = InfRequest.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    if existing_request:
        return jsonify({'error': 'Request already sent for this campaign'}), 400

    influencer = User.query.get(influencer_id)
    influencer_name = influencer.username if influencer else 'Unknown'

    if not campaign_id:
        return jsonify({'error': 'Campaign ID is required'}), 400

    new_request = InfRequest(
        influencer_id=influencer_id,
        campaign_id=campaign_id,
        campaign_name=campaign_name,
        campaign_description=campaign_description,
        budget=budget,
        influencer_name=influencer_name,
        status='Pending'
    )

    db.session.add(new_request)
    db.session.commit()

    return jsonify({'message': 'Ad request sent successfully'}), 201


@ad_requests_bp.route('/sponsor/collab-requests', methods=['GET'])
@jwt_required()  # Ensure the user is authenticated
def get_collab_requests():
    sponsor_id = get_jwt_identity()  # Assuming the JWT contains the sponsor ID

    # Query to get all requests where the campaign is owned by the logged-in sponsor
    requests = InfRequest.query.join(Campaign).filter(
        Campaign.sponsor_id == sponsor_id
    ).all()

    # Format the response
    result = []
    for req in requests:
        if req.influencer:  # Ensure that the influencer exists
            influencer_name = req.influencer.username  # Use the username
        else:
            influencer_name = "Unknown"  # Fallback if influencer does not exist

        result.append({
            'id': req.id,
            'campaign_name': req.campaign.name,
            'influencer_name': influencer_name,
            'status': req.status,
            'description': req.campaign.description,
            'budget': req.campaign.budget,
        })

    return jsonify(result), 200

@ad_requests_bp.route('/sponsor/collab-requests/<int:request_id>/accept', methods=['PUT'])
@jwt_required()
def accept_collab_request(request_id):
    request = InfRequest.query.get(request_id)
    if request:
        request.status = 'Accepted'
        db.session.commit()
        return jsonify({'message': 'Request accepted successfully'}), 200
    return jsonify({'error': 'Request not found'}), 404

@ad_requests_bp.route('/sponsor/collab-requests/<int:request_id>/reject', methods=['PUT'])
@jwt_required()
def reject_collab_request(request_id):
    request = InfRequest.query.get(request_id)
    if request:
        request.status = 'Rejected'
        db.session.commit()
        return jsonify({'message': 'Request rejected successfully'}), 200
    return jsonify({'error': 'Request not found'}), 404

#influencer 
@ad_requests_bp.route('/ad_requests/<int:request_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(request_id):
    current_user = get_jwt_identity()

    # Fetch the messages for the ad request
    messages = Message.query.filter(
        Message.request_id == request_id,
        (Message.sender_id == current_user) | (Message.influencer_id == current_user)
    ).all()

    # Serialize messages
    serialized_messages = []
    for message in messages:
        if isinstance(message, Message):
            sender_name = message.sender.username if message.sender else 'Unknown'
            serialized_messages.append({
                "id": message.id,
                "sender_name": sender_name,
                "content": message.content,
                "timestamp": message.timestamp.isoformat() if message.timestamp else None,
                "is_influencer": message.sender_id == current_user  # Determine if the sender is the current user
            })
        else:
            print(f"Unexpected message type: {type(message)}")

    return jsonify(serialized_messages), 200




@ad_requests_bp.route('/ad_requests/<int:request_id>/messages', methods=['POST'])
@jwt_required()
def send_message(request_id):
    data = request.get_json()
    campaign_id = data.get('campaign_id') 
    content = data.get('content')  # Corrected this line
    influencer_id = data.get('influencer_id')
    sender_id = get_jwt_identity()  

    # Validate inputs
    if not content:
        return jsonify({'error': 'Message content is required'}), 400
    if not influencer_id:
        return jsonify({'error': 'Influencer ID is required'}), 400

    new_message = Message(
        request_id=request_id,
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        sender_id=sender_id,
        content=content,
        timestamp=datetime.now()  
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict()), 201


@ad_requests_bp.route('/user/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,  
    }

    return jsonify(user_data), 200


#sponsor
@ad_requests_bp.route('/ad_requests/<int:campaign_id>/<int:influencer_id>/messages', methods=['GET'])
@jwt_required()
def get_conversation_messages(campaign_id, influencer_id):
    sponsor_id = get_jwt_identity()
    messages = Message.query.filter(
        Message.campaign_id == campaign_id,
        Message.influencer_id == influencer_id,
        (Message.sender_id == sponsor_id) | (Message.sender_id == influencer_id)
    ).all()

    # Serialize messages
    serialized_messages = []
    for message in messages:
        if isinstance(message, Message):
            sender_name = message.sender.username if message.sender else 'Unknown'
            serialized_messages.append({
                "id": message.id,
                "sender_name": message.sender.username if message.sender else 'Unknown',
                "sender_name": sender_name,
                "content": message.content,
                "timestamp": message.timestamp.isoformat() if message.timestamp else None,
                "is_influencer": message.sender_id == influencer_id
            })
        else:
            print(f"Unexpected message type: {type(message)}")

    return jsonify(serialized_messages), 200



    
    
# Backend route for handling replies
@ad_requests_bp.route('/ad_requests/<int:campaign_id>/<int:influencer_id>/reply', methods=['POST'])
@jwt_required()
def send_reply(campaign_id, influencer_id):
    data = request.get_json()
    sender_id = get_jwt_identity()  # Get the ID of the currently authenticated user
    content = data.get('message')
    
    if not content:
        return jsonify({'error': 'Message content is required'}), 400

    # Check if the ad request exists
    ad_request = AdRequest.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    if not ad_request:
        return jsonify({'error': 'Ad request not found for this campaign and influencer'}), 404

    # Fetch the sender user
    sender = User.query.get(sender_id)
    if not sender:
        return jsonify({'error': 'Sender not found'}), 404

    # Create a new message with the sender_id included
    new_message = Message(
        request_id=ad_request.id,  # Assuming request_id is linked to the ad request
        campaign_id=campaign_id,
        influencer_id=influencer_id,
        sender_id=sender_id,  # Include the sender ID
        content=content,
        timestamp=datetime.utcnow()  # Use UTC for the timestamp
    )

    # Add the message to the session and commit to the database
    db.session.add(new_message)
    db.session.commit()

    return jsonify({'message': 'Reply sent successfully', 'data': new_message.to_dict()}), 201



@ad_requests_bp.route('/ad_requests/<int:request_id>/modify', methods=['PUT'])
@jwt_required()
def modify_ad_request(request_id):
    influencer_id = get_jwt_identity() 
    data = request.get_json() 
    try:
        ad_request = AdRequest.query.filter_by(id=request_id, influencer_id=influencer_id).first()
        if not ad_request:
            return jsonify({'error': 'Ad request not found or unauthorized'}), 404

        ad_request.campaign_description = data.get('description', ad_request.campaign_description)
        db.session.commit()  
        return jsonify({'message': 'Ad request modified successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ad_requests_bp.route('/campaigns/<int:campaign_id>/influencers/<int:influencer_id>/request', methods=['DELETE'])
@jwt_required()
def delete_ad_request(campaign_id, influencer_id):
    """
    Deletes an ad request for a given campaign and influencer.
    """
    current_user_id = get_jwt_identity()

    # Ensure the campaign belongs to the current sponsor
    campaign = Campaign.query.filter_by(id=campaign_id, sponsor_id=current_user_id).first()
    if not campaign:
        return jsonify({"error": "Campaign not found or not authorized"}), 404

    # Find the ad request for the given campaign and influencer
    ad_request = AdRequest.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    if not ad_request:
        return jsonify({"error": "Ad request not found"}), 404

    try:
        # Delete the ad request
        db.session.delete(ad_request)
        db.session.commit()
        return jsonify({"message": "Ad request successfully deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the ad request", "details": str(e)}), 500


@ad_requests_bp.route('/ad_requests/<int:campaign_id>/<int:influencer_id>', methods=['PUT'])
def update_ad_request_budget(campaign_id, influencer_id):
    data = request.json
    new_budget = data.get("budget")
    
    # Validate input
    if new_budget is None or not isinstance(new_budget, (int, float)):
        return jsonify({"error": "Invalid budget value"}), 400
    
    # Find the AdRequest
    ad_request = AdRequest.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    if not ad_request:
        return jsonify({"error": "AdRequest not found"}), 404
    
    # Update the budget
    ad_request.budget = new_budget
    db.session.commit()

    return jsonify({"message": "AdRequest budget updated successfully", "ad_request": ad_request.to_dict()})

