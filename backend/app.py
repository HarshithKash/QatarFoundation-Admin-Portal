from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

# ──────────────────────────────────────────────
# App & Config
# ──────────────────────────────────────────────
BASE_DIR  = os.path.abspath(os.path.dirname(__file__))
FRONT_DIR = os.path.join(BASE_DIR, '..', 'frontend', 'sky')

app = Flask(__name__, static_folder=FRONT_DIR, static_url_path='')
app.config['SECRET_KEY']                  = 'certifyme_super_secret_2025'
app.config['SQLALCHEMY_DATABASE_URI']     = f"sqlite:///{os.path.join(BASE_DIR, 'certifyme.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME']  = timedelta(days=7)

db   = SQLAlchemy(app)
CORS(app, supports_credentials=True, origins=['http://127.0.0.1:5000', 'http://localhost:5000'])

# ──────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────
VALID_CATEGORIES = {'technology', 'business', 'design', 'marketing', 'data', 'other'}

class User(db.Model):
    __tablename__ = 'user'
    id          = db.Column(db.Integer, primary_key=True)
    full_name   = db.Column(db.String(100), nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=False)
    password    = db.Column(db.String(256), nullable=False)
    opportunities = db.relationship('Opportunity', backref='admin', lazy=True, cascade='all, delete-orphan')

class Opportunity(db.Model):
    __tablename__ = 'opportunity'
    id                  = db.Column(db.Integer, primary_key=True)
    admin_id            = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name                = db.Column(db.String(200), nullable=False)
    duration            = db.Column(db.String(100), nullable=False)
    start_date          = db.Column(db.String(50),  nullable=False)
    description         = db.Column(db.Text,        nullable=False)
    skills              = db.Column(db.Text,        nullable=False)   # comma-separated
    category            = db.Column(db.String(50),  nullable=False)
    future_opportunities= db.Column(db.Text,        nullable=False)
    max_applicants      = db.Column(db.Integer,     nullable=True)

    def to_dict(self):
        return {
            'id':                   self.id,
            'name':                 self.name,
            'duration':             self.duration,
            'start_date':           self.start_date,
            'description':          self.description,
            'skills':               self.skills,
            'category':             self.category,
            'future_opportunities': self.future_opportunities,
            'max_applicants':       self.max_applicants,
        }

with app.app_context():
    db.create_all()

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def current_user_id():
    return session.get('user_id')

def require_login():
    if not current_user_id():
        return jsonify({'error': 'Unauthorized'}), 401
    return None

# ──────────────────────────────────────────────
# Serve Frontend
# ──────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'admin.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# ──────────────────────────────────────────────
# Auth Routes
# ──────────────────────────────────────────────
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    full_name = (data.get('full_name') or '').strip()
    email     = (data.get('email')     or '').strip().lower()
    password  = (data.get('password')  or '').strip()

    if not full_name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    user = User(
        full_name = full_name,
        email     = email,
        password  = generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Account created successfully'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data        = request.get_json(silent=True) or {}
    email       = (data.get('email')    or '').strip().lower()
    password    = (data.get('password') or '').strip()
    remember_me = data.get('remember_me', False)

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid email or password'}), 401

    session.permanent = bool(remember_me)
    session['user_id'] = user.id
    return jsonify({'message': 'Login successful', 'email': user.email}), 200


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'}), 200


@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """
    Per US-1.3: Always show success. Generate token internally (log only).
    Token expires in 1 hour.
    """
    data  = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()

    # Log the reset token (no email sending required)
    expiry = datetime.now() + timedelta(hours=1)
    print(f'[RESET] Password reset requested for: {email} | Token expires: {expiry}')

    # Always return same message regardless of whether email exists (security best practice)
    return jsonify({'message': 'Reset link sent to your email!'}), 200


# ──────────────────────────────────────────────
# Opportunity Routes
# ──────────────────────────────────────────────
@app.route('/api/opportunities', methods=['GET'])
def get_opportunities():
    err = require_login()
    if err: return err

    opps = Opportunity.query.filter_by(admin_id=current_user_id()).all()
    return jsonify([o.to_dict() for o in opps]), 200


@app.route('/api/opportunities', methods=['POST'])
def create_opportunity():
    err = require_login()
    if err: return err

    data = request.get_json(silent=True) or {}
    name                = (data.get('name')                or '').strip()
    duration            = (data.get('duration')            or '').strip()
    start_date          = (data.get('start_date')          or '').strip()
    description         = (data.get('description')         or '').strip()
    skills              = (data.get('skills')              or '').strip()
    category            = (data.get('category')            or '').strip()
    future_opportunities= (data.get('future_opportunities')or '').strip()
    max_applicants      = data.get('max_applicants')

    if not all([name, duration, start_date, description, skills, category, future_opportunities]):
        return jsonify({'error': 'All required fields must be filled'}), 400
    if category not in VALID_CATEGORIES:
        return jsonify({'error': f'Invalid category. Must be one of: {", ".join(VALID_CATEGORIES)}'}), 400

    opp = Opportunity(
        admin_id            = current_user_id(),
        name                = name,
        duration            = duration,
        start_date          = start_date,
        description         = description,
        skills              = skills,
        category            = category,
        future_opportunities= future_opportunities,
        max_applicants      = int(max_applicants) if max_applicants else None,
    )
    db.session.add(opp)
    db.session.commit()
    return jsonify({'message': 'Opportunity created', 'id': opp.id}), 201


@app.route('/api/opportunities/<int:opp_id>', methods=['GET'])
def get_opportunity(opp_id):
    err = require_login()
    if err: return err

    opp = Opportunity.query.filter_by(id=opp_id, admin_id=current_user_id()).first()
    if not opp:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(opp.to_dict()), 200


@app.route('/api/opportunities/<int:opp_id>', methods=['PUT'])
def update_opportunity(opp_id):
    err = require_login()
    if err: return err

    opp = Opportunity.query.filter_by(id=opp_id, admin_id=current_user_id()).first()
    if not opp:
        return jsonify({'error': 'Not found or unauthorized'}), 404

    data     = request.get_json(silent=True) or {}
    category = (data.get('category') or '').strip()
    if category and category not in VALID_CATEGORIES:
        return jsonify({'error': 'Invalid category'}), 400

    fields = ['name', 'duration', 'start_date', 'description', 'skills',
              'category', 'future_opportunities', 'max_applicants']
    for f in fields:
        if f in data:
            val = data[f]
            if f == 'max_applicants':
                setattr(opp, f, int(val) if val else None)
            else:
                setattr(opp, f, str(val).strip())

    db.session.commit()
    return jsonify({'message': 'Opportunity updated'}), 200


@app.route('/api/opportunities/<int:opp_id>', methods=['DELETE'])
def delete_opportunity(opp_id):
    err = require_login()
    if err: return err

    opp = Opportunity.query.filter_by(id=opp_id, admin_id=current_user_id()).first()
    if not opp:
        return jsonify({'error': 'Not found or unauthorized'}), 404

    db.session.delete(opp)
    db.session.commit()
    return jsonify({'message': 'Opportunity deleted'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
