from flask import Blueprint, request, jsonify, make_response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, cache
from app.models import Campaign, AdRequest, InfRequest, User, Message
from datetime import datetime
import csv
import io

campaigns_bp = Blueprint('campaigns_bp', __name__)

@campaigns_bp.route('/campaigns', methods=['POST'])
@jwt_required()
def create_campaign():
    current_user_id = get_jwt_identity()
    token = request.headers.get('Authorization')
    
    if request.content_type != 'application/json':
        return make_response(jsonify({"message": "Unsupported Media Type"}), 415)

    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    
    

    name = data.get('name')
    description = data.get('description')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    budget = data.get('budget')
    visibility = data.get('visibility')
    goals = data.get('goals')
    niches = data.get('niches')

    if not all([name, description, start_date, end_date, budget, visibility, goals]):
        return jsonify({"message": "Missing fields"}), 400

    try:
        start_date = datetime.strptime(start_date, '%d/%m/%Y')
        end_date = datetime.strptime(end_date, '%d/%m/%Y')
    except ValueError:
        return jsonify({"message": "Invalid date format, expected YYYY-MM-DD"}), 400

    try:
        campaign = Campaign(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            visibility=visibility,
            goals=goals,
            niches=niches, 
            sponsor_id=current_user_id
        )
        db.session.add(campaign)
        db.session.commit()
        return jsonify(campaign.to_dict()), 201
    except Exception as e:
        print(f"Database error: {str(e)}")  # Log the error for debugging
        return jsonify({"message": "Failed to create campaign"}), 500


@campaigns_bp.route('/campaigns', methods=['GET'])
@jwt_required()
def get_campaigns():
    try:
        user_identity = get_jwt_identity()
        campaigns = Campaign.query.filter_by(sponsor_id=user_identity).all()
        return jsonify([campaign.to_dict() for campaign in campaigns]), 200

    except Exception as e:
        # Catch any exceptions and return a 422 response with the error message
        return jsonify({"msg": str(e)}), 422

@campaigns_bp.route('/campaigns/public', methods=['GET'])
def get_public_campaigns():
    campaigns = Campaign.query.filter_by(visibility='public').all()
    return jsonify([campaign.to_dict() for campaign in campaigns]), 200


@campaigns_bp.route('/campaigns/<int:campaign_id>', methods=['GET'])
@jwt_required()
def get_campaign(campaign_id):
    try:
        user_identity = get_jwt_identity()
        campaign = Campaign.query.filter_by(id=campaign_id, sponsor_id=user_identity).first()
        
        if campaign is None:
            return jsonify({"msg": "Campaign not found"}), 404
 
        return jsonify(campaign.to_dict()), 200  
    
    except Exception as e:
        return jsonify({"msg": str(e)}), 422

@campaigns_bp.route('/campaigns/<int:campaign_id>', methods=['PUT'])
@jwt_required()
def update_campaign(campaign_id):
    data = request.json
    campaign = Campaign.query.get(campaign_id)

    if not campaign:
        return jsonify({"message": "Campaign not found"}), 404

    campaign.name = data.get("name", campaign.name)
    campaign.description = data.get("description", campaign.description)
    campaign.budget = data.get("budget", campaign.budget)
    campaign.visibility = data.get("visibility", campaign.visibility)
    campaign.description = data.get("description", campaign.description)

    try:
        db.session.commit()
        cache.delete('/public-campaigns') 
        return jsonify({"message": "Campaign updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating campaign"}), 500
    
    
@campaigns_bp.route('/campaigns/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    try:
        user_identity = get_jwt_identity()
        campaign = Campaign.query.filter_by(id=campaign_id, sponsor_id=user_identity).first()

        if campaign is None:
            return jsonify({"msg": "Campaign not found"}), 404

        # Manually delete related ad requests and inf requests
        db.session.query(AdRequest).filter(AdRequest.campaign_id == campaign_id).delete()
        db.session.query(InfRequest).filter(InfRequest.campaign_id == campaign_id).delete()

        # Now delete the campaign
        db.session.delete(campaign)
        db.session.commit()

        return jsonify({"msg": "Campaign deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()  # Rollback on failure
        return jsonify({"msg": str(e)}), 422
    

@campaigns_bp.route('/api/export_campaigns', methods=['GET'])
@jwt_required()
def export_campaigns():
    try:
        sponsor_id = get_jwt_identity()
        campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()

        if not campaigns:
            return jsonify({'message': 'No campaigns found for this sponsor'}), 404

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Campaign ID', 'Name', 'Description', 'Start Date', 'End Date', 'Budget', 'Visibility'])
        for campaign in campaigns:
            writer.writerow([
                campaign.id,
                campaign.name,
                campaign.description,
                campaign.start_date.isoformat() if campaign.start_date else "",
                campaign.end_date.isoformat() if campaign.end_date else "",
                campaign.budget,
                campaign.visibility,
            ])

        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='campaigns_export.csv'
        )
    except Exception as e:
        print(f"Error exporting campaigns: {e}")
        return jsonify({'message': 'Error generating export file'}), 500


@campaigns_bp.route('/influencers/search', methods=['GET'])
@jwt_required()
def search_influencers():
    query = request.args.get('query', '').strip().lower()

    if not query:
        print("No query provided.")
        return jsonify([]), 200  # Return empty array if no query

    # Log the query for debugging
    print(f"Search Query: '{query}'")

    # Fetch influencers with role="Influencer" filtered by query
    influencers = (
        db.session.query(User)
        .filter(
            User.role.ilike("influencer"),  # Only influencers
            (
                User.username.ilike(f"%{query}%") |  # Search by username
                User.email.ilike(f"%{query}%")      # Search by email
            )
        )
        .all()
    )

    # Log the number of influencers found
    if influencers:
        print(f"Found {len(influencers)} influencers.")
    else:
        print("No influencers found matching the query.")

    # Serialize influencers
    influencers_data = [
        {
            "id": influencer.id,
            "name": influencer.username,
            "email": influencer.email
        }
        for influencer in influencers
    ]

    # Log the serialized data
    print(f"Serialized Influencers: {influencers_data}")

    return jsonify(influencers_data), 200


# Fetch messages for a specific campaign
@campaigns_bp.route("/campaigns/<int:campaign_id>/messages", methods=["GET"])
def get_messages_for_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404
    
    # Retrieve all messages sent to this campaign
    messages = Message.query.filter_by(campaign_id=campaign_id).all()
    response = []
    
    for message in messages:
        response.append({
            "id": message.id,
            "sender_id": message.sender_id,
            "sender_name": message.sender.username,  # Assuming the 'sender' is an influencer
            "message": message.content,
            "timestamp": message.timestamp,
        })
    
    return jsonify(response)

@campaigns_bp.route('/campaigns/<int:campaign_id>/messages/reply', methods=['POST', 'OPTIONS'])
@jwt_required()
def reply_message(campaign_id):
    # Handle OPTIONS preflight request for CORS
    if request.method == 'OPTIONS':
        return jsonify({'message': 'Preflight request successful'}), 200

    # Handle POST request to send a reply
    if request.method == 'POST':
        try:
            # Extract the message content, influencer ID, and optionally request_id
            influencer_id = request.json.get('influencer_id')
            message = request.json.get('message')
            request_id = request.json.get('request_id')  # Optional field, may be None

            # Debugging: print received data
            print(f"Received Data: influencer_id={influencer_id}, message={message}, request_id={request_id}")

            # Validate inputs
            if not influencer_id or not message:
                return jsonify({'error': 'Missing required fields'}), 400

            # Fetch the campaign, ensure the campaign exists
            campaign = Campaign.query.get_or_404(campaign_id)

            # Ensure the logged-in user is valid (the sender of the message)
            sender_id = get_jwt_identity()  # Get the ID of the logged-in user

            # Ensure the sender is either a Sponsor or Admin
            sender = User.query.get_or_404(sender_id)

            # Create a new message
            new_message = Message(
                request_id=request_id,  # This can be None if no request_id is passed
                campaign_id=campaign.id,
                influencer_id=influencer_id,
                content=message,
                sender_id=sender.id,  # Use the sender's ID here
            )

            # Add the message to the database
            db.session.add(new_message)
            db.session.commit()

            return jsonify({'message': 'Reply sent successfully!'}), 200

        except Exception as e:
            print(f"Error while sending reply: {str(e)}") 
            return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Invalid method'}), 405



@campaigns_bp.route('/campaigns/<int:campaign_id>/influencers', methods=['GET'])
@jwt_required()
def get_influencers_by_campaign(campaign_id):
    """
    Fetch the list of influencers associated with a specific campaign
    """
    # Fetch the campaign from the database
    campaign = Campaign.query.get_or_404(campaign_id)

    # Query the influencers associated with the campaign
    influencers = User.query.filter_by(role='influencer').all()

    # If no influencers are found, return an empty list
    if not influencers:
        return jsonify([])

    # Serialize the influencers (example assuming a name and id)
    influencers_data = [{
        'id': influencer.id,
        'name': influencer.username
    } for influencer in influencers]

    return jsonify(influencers_data), 200