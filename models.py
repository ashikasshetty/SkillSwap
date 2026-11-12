from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(150), default='St Agnes College, Mangaluru')
    avatar = db.Column(db.String(255), default='default_avatar.png')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    skills_offered = db.relationship('SkillOffered', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    skills_wanted = db.relationship('SkillWanted', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    sent_requests = db.relationship(
        'SwapRequest',
        foreign_keys='SwapRequest.sender_id',
        backref='sender',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    received_requests = db.relationship(
        'SwapRequest',
        foreign_keys='SwapRequest.receiver_id',
        backref='receiver',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    sent_messages = db.relationship(
        'Message',
        foreign_keys='Message.sender_id',
        backref='sender',
        lazy='dynamic'
    )
    received_messages = db.relationship(
        'Message',
        foreign_keys='Message.receiver_id',
        backref='receiver',
        lazy='dynamic'
    )
    
    reviews_given = db.relationship(
        'Review',
        foreign_keys='Review.reviewer_id',
        backref='reviewer',
        lazy='dynamic'
    )
    reviews_received = db.relationship(
        'Review',
        foreign_keys='Review.reviewee_id',
        backref='reviewee',
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def average_rating(self):
        reviews = self.reviews_received.all()
        if not reviews:
            return 5.0  # Default friendly starting rating for new students
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def total_reviews_count(self):
        return self.reviews_received.count()

    @property
    def completed_swaps_count(self):
        return SwapRequest.query.filter(
            ((SwapRequest.sender_id == self.id) | (SwapRequest.receiver_id == self.id)),
            SwapRequest.status == 'completed'
        ).count()

    def __repr__(self):
        return f'<User {self.email}>'


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='fa-book')  # FontAwesome icon name
    description = db.Column(db.String(255), nullable=True)
    
    skills_offered = db.relationship('SkillOffered', backref='category', lazy='dynamic')
    skills_wanted = db.relationship('SkillWanted', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class SkillOffered(db.Model):
    __tablename__ = 'skills_offered'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False, index=True)
    proficiency = db.Column(db.String(30), default='Intermediate')  # Beginner, Intermediate, Advanced, Expert
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<SkillOffered {self.skill_name} by User {self.user_id}>'


class SkillWanted(db.Model):
    __tablename__ = 'skills_wanted'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False, index=True)
    target_level = db.Column(db.String(30), default='Beginner')  # Beginner, Intermediate, Advanced
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<SkillWanted {self.skill_name} by User {self.user_id}>'


class SwapRequest(db.Model):
    __tablename__ = 'swap_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    offered_skill_id = db.Column(db.Integer, db.ForeignKey('skills_offered.id'), nullable=True)
    requested_skill_id = db.Column(db.Integer, db.ForeignKey('skills_offered.id'), nullable=True)
    
    # Status options: 'pending', 'accepted', 'rejected', 'completed', 'cancelled'
    status = db.Column(db.String(20), default='pending', index=True)
    message = db.Column(db.Text, nullable=True)
    schedule_note = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    offered_skill = db.relationship('SkillOffered', foreign_keys=[offered_skill_id])
    requested_skill = db.relationship('SkillOffered', foreign_keys=[requested_skill_id])

    messages = db.relationship('Message', backref='swap_request', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='swap_request', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<SwapRequest {self.id}: {self.sender_id} -> {self.receiver_id} ({self.status})>'


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    swap_id = db.Column(db.Integer, db.ForeignKey('swap_requests.id', ondelete='CASCADE'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id}>'


class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    swap_id = db.Column(db.Integer, db.ForeignKey('swap_requests.id', ondelete='CASCADE'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Review {self.id}: {self.rating} stars from {self.reviewer_id} to {self.reviewee_id}>'
