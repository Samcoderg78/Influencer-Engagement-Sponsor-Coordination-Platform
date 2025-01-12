from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    flagged = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=False) 
    niche = db.Column(db.String(255))
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'flagged': self.flagged,
            'niche': self.niche,
        }
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}', '{self.active}' )"

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)
    goals = db.Column(db.Text, nullable=False)
    flagged = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='active')
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sponsor = db.relationship('User', backref='campaigns')
    niches = db.Column(db.String(255))  # New column for niches

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'budget': self.budget,
            'visibility': self.visibility,
            'goals': self.goals,
            'flagged': self.flagged,
            'status': self.status,
            'sponsor_id': self.sponsor_id,
            'sponsor_name': self.sponsor.username,
            'niches': self.niches,
        }

    def __repr__(self):
        return f"Campaign('{self.name}', '{self.start_date}', '{self.end_date}')"

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    campaign_description = db.Column(db.String(255))
    budget = db.Column(db.Float)
    campaign = db.relationship('Campaign', backref='ad_requests')
    influencer = db.relationship('User', backref='ad_requests')
    messages = db.relationship('Message', backref='ad_request_ref', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign.name,
            'influencer_id': self.influencer_id,
            'status': self.status,
            'campaign_description': self.campaign_description,
            'budget': self.budget,
            'influencer_name': self.influencer.username if self.influencer else None,
            'sponsor_name': self.campaign.sponsor.username if self.campaign.sponsor else None
        }

    def __repr__(self):
        return (f"AdRequest(campaign_id={self.campaign_id}, influencer_id={self.influencer_id}, "
                f"status={self.status})")

class InfRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    campaign_name = db.Column(db.String(100), nullable=False)
    campaign_description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    influencer_name = db.Column(db.String(100), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Pending')

    campaign = db.relationship('Campaign', foreign_keys=[campaign_id])
    influencer = db.relationship('User', foreign_keys=[influencer_id])

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'campaign_name': self.campaign_name,
            'campaign_description': self.campaign_description,
            'budget': self.budget,
            'influencer_id': self.influencer_id,
            'influencer_name': self.influencer_name,
            'sent_at': self.sent_at.isoformat(),
            'status': self.status
        }

    def __repr__(self):
        return (f"InfRequest(campaign_id={self.campaign_id}, influencer_id={self.influencer_id}, "
                f"influencer_name={self.influencer_name}, budget={self.budget}, sent_at={self.sent_at}, status={self.status})")

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('ad_request.id'), nullable=True)
    campaign_id = db.Column(db.Integer)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_request = db.relationship('AdRequest', backref='messages_list', lazy=True)
    influencer = db.relationship('User', foreign_keys=[influencer_id], backref='received_messages', lazy=True)
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages', lazy=True)

    def to_dict(self):
        is_influencer = self.sender_id == self.influencer_id
        return {
            'id': self.id,
            'request_id': self.request_id,
            'campaign_id': self.campaign_id,
            'influencer_id': self.influencer_id,
            'is_influencer': is_influencer,
            'sender_id': self.sender_id,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
        }

    def __repr__(self):
        return (f"Message(influencer_id={self.influencer_id}, "
                f"campaign={self.campaign_id}, sender_id={self.sender_id}, "
                f"sender_name={self.sender.username if self.sender else 'Unknown'}, "
                f"content={self.content})")
