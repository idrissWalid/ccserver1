from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re
import os

app = Flask(__name__)

# --- CONFIGURATION BASE DE DONNÉES ---
# On récupère l'URL de Render, sinon on utilise ton URL Supabase
# Note: SQLAlchemy requiert 'postgresql://' au lieu de 'postgres://'
uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'postgresql://postgres:[YOUR-PASSWORD]@db.gtqwsydwrlwruoruqlvx.supabase.co:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'une_cle_tres_secrete_123')

CORS(app)
db = SQLAlchemy(app)

# --- MODÈLE UTILISATEUR ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    orange_money = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_subscribed = db.Column(db.Boolean, default=False)
    subscribe_date = db.Column(db.DateTime, nullable=True)

    def check_validity(self):
        if self.is_subscribed and self.subscribe_date:
            if datetime.now() > self.subscribe_date + timedelta(days=30):
                self.is_subscribed = False
                db.session.commit()
        return self.is_subscribed

    def to_dict(self):
        return {
            "username": self.username,
            "phone": self.phone,
            "orange_money": self.orange_money,
            "is_subscribed": self.check_validity(),
            "date": self.subscribe_date.strftime("%d/%m/%Y") if self.subscribe_date else None
        }

# Création des tables dans Supabase
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def home():
    return jsonify({"status": "Server is running", "database": "Connected to Supabase"}), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Nom d'utilisateur déjà pris"}), 400
    
    new_user = User(
        username=data['username'],
        phone=data['phone'],
        orange_money=data['orange_money'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(new_user)
    db.session.commit()
    
    # Code USSD simulé (Exemple Orange BF)
    ussd_code = f"*144*10*55713380*500#" 
    return jsonify({"ussd_code": ussd_code}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password_hash, data['password']):
        return jsonify({"status": "success", "user": user.to_dict()}), 200
    return jsonify({"error": "Identifiants incorrects"}), 401

@app.route('/api/check-status/<username>', methods=['GET'])
def check_status(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"is_subscribed": user.check_validity()}), 200
    return jsonify({"error": "Not found"}), 404

@app.route('/payment', methods=['POST'])
def handle_payment():
    raw_data = request.get_data().decode('utf-8', errors='ignore')
    match = re.search(r'du\s(\d{8})', raw_data)
    
    if match:
        phone_payer = match.group(1)
        user = User.query.filter_by(orange_money=phone_payer).first()
        if user:
            user.is_subscribed = True
            user.subscribe_date = datetime.now()
            db.session.commit()
            return jsonify({"status": "success", "message": f"Compte {phone_payer} active"}), 200
            
    return jsonify({"error": "Format de message non reconnu"}), 400

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    if request.headers.get('X-API-KEY') != "Lifeisabitch13":
        return jsonify({"error": "Unauthorized"}), 401
    
    users = User.query.all()
    return jsonify({
        "total": len(users),
        "actifs": len([u for u in users if u.check_validity()]),
        "users": [u.to_dict() for u in users]
    })

if __name__ == '__main__':
    # Configuration pour le déploiement
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)