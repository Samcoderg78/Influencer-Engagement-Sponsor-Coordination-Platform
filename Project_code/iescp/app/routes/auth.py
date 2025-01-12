from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from app import db
from app.models import User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    niche = data.get('niche')  # Get niche from request data, if present

    if not username or not email or not password or not role:
        return jsonify({"message": "Missing fields"}), 400

    # If role is 'influencer', ensure niche is provided
    if role == 'influencer' and not niche:
        return jsonify({"message": "Niche is required for influencers"}), 400

    # Check if user already exists
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"message": "User already exists"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    # Create the new user
    new_user = User(username=username, email=email, password=hashed_password, role=role, active=False, niche=niche)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    if request.content_type != 'application/json':
        return jsonify({"message": "Unsupported Media Type"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Missing fields"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        if not user.active:
            return jsonify({"message": "Your account is not approved yet. Please contact the admin."}), 403

        if check_password_hash(user.password, password):
            if not user.active:
                return jsonify({"message": "Your account is not approved yet. Please contact the admin."}), 403
            if user.flagged:
                return jsonify({"message": "Your account has been flagged. You cannot log in."}), 403
            else:
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)
                return jsonify({
                    'message': "Login successful",
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'username': user.username,
                        'email': user.email,
                        'role': user.role
                    }
                }), 200
    return jsonify({"message": "Login Unsuccessful. Please check email and password"}), 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt_identity()['jti'] 
    return jsonify(msg="Successfully logged out"), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()  
def refresh():
    access_token = create_access_token(identity=get_jwt_identity())
    return jsonify(access_token=access_token), 200
