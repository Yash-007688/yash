from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import requests
from datetime import datetime
import threading
import time
# Selenium imports removed for simplified version
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///youtube_automation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InstagramAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class YouTubeAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Reel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instagram_url = db.Column(db.String(500), nullable=False)
    youtube_url = db.Column(db.String(500))
    title = db.Column(db.String(200))
    thumbnail_path = db.Column(db.String(200))
    likes_count = db.Column(db.Integer, default=0)
    views_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    subscribers_gained = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProcessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(20), default='info')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Global variables for automation
automation_running = False
automation_thread = None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    instagram_accounts = InstagramAccount.query.filter_by(user_id=current_user.id).all()
    youtube_accounts = YouTubeAccount.query.filter_by(user_id=current_user.id).all()
    reels = Reel.query.filter_by(user_id=current_user.id).order_by(Reel.created_at.desc()).limit(10).all()
    logs = ProcessLog.query.filter_by(user_id=current_user.id).order_by(ProcessLog.created_at.desc()).limit(20).all()
    
    return render_template('dashboard.html', 
                         instagram_accounts=instagram_accounts,
                         youtube_accounts=youtube_accounts,
                         reels=reels,
                         logs=logs)

@app.route('/api/add_instagram_account', methods=['POST'])
@login_required
def add_instagram_account():
    data = request.get_json()
    account = InstagramAccount(
        username=data['username'],
        password=data['password'],
        user_id=current_user.id
    )
    db.session.add(account)
    db.session.commit()
    
    log = ProcessLog(
        message=f"Added Instagram account: {data['username']}",
        level='info',
        user_id=current_user.id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/add_youtube_account', methods=['POST'])
@login_required
def add_youtube_account():
    data = request.get_json()
    account = YouTubeAccount(
        email=data['email'],
        password=data['password'],
        user_id=current_user.id
    )
    db.session.add(account)
    db.session.commit()
    
    log = ProcessLog(
        message=f"Added YouTube account: {data['email']}",
        level='info',
        user_id=current_user.id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/start_automation', methods=['POST'])
@login_required
def start_automation():
    global automation_running, automation_thread
    
    if automation_running:
        return jsonify({'success': False, 'message': 'Automation already running'})
    
    automation_running = True
    automation_thread = threading.Thread(target=run_automation, args=(current_user.id,))
    automation_thread.start()
    
    log = ProcessLog(
        message="Started automation process",
        level='info',
        user_id=current_user.id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Automation started'})

@app.route('/api/stop_automation', methods=['POST'])
@login_required
def stop_automation():
    global automation_running
    
    automation_running = False
    
    log = ProcessLog(
        message="Stopped automation process",
        level='info',
        user_id=current_user.id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Automation stopped'})

@app.route('/api/get_logs')
@login_required
def get_logs():
    logs = ProcessLog.query.filter_by(user_id=current_user.id).order_by(ProcessLog.created_at.desc()).limit(50).all()
    return jsonify([{
        'id': log.id,
        'message': log.message,
        'level': log.level,
        'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for log in logs])

def run_automation(user_id):
    global automation_running
    
    log = ProcessLog(
        message="Starting Instagram reel processing...",
        level='info',
        user_id=user_id
    )
    db.session.add(log)
    db.session.commit()
    
    # Simulate Instagram reel processing
    while automation_running:
        try:
            # Check for new reels on Instagram accounts
            instagram_accounts = InstagramAccount.query.filter_by(user_id=user_id).all()
            
            for account in instagram_accounts:
                if not automation_running:
                    break
                
                # Simulate finding new reels
                log = ProcessLog(
                    message=f"Checking Instagram account: {account.username}",
                    level='info',
                    user_id=user_id
                )
                db.session.add(log)
                db.session.commit()
                
                # Simulate downloading and processing reels
                time.sleep(2)
                
                # Create a sample reel entry
                reel = Reel(
                    instagram_url="https://instagram.com/sample_reel",
                    title="Sample Hindi Reel Title",
                    thumbnail_path="/static/thumbnails/sample.jpg",
                    user_id=user_id,
                    status='processed'
                )
                db.session.add(reel)
                db.session.commit()
                
                log = ProcessLog(
                    message=f"Processed reel from {account.username}",
                    level='success',
                    user_id=user_id
                )
                db.session.add(log)
                db.session.commit()
            
            # Simulate YouTube upload
            youtube_accounts = YouTubeAccount.query.filter_by(user_id=user_id).all()
            for account in youtube_accounts:
                if not automation_running:
                    break
                
                log = ProcessLog(
                    message=f"Uploading to YouTube account: {account.email}",
                    level='info',
                    user_id=user_id
                )
                db.session.add(log)
                db.session.commit()
                
                time.sleep(3)
                
                log = ProcessLog(
                    message=f"Successfully uploaded to {account.email}",
                    level='success',
                    user_id=user_id
                )
                db.session.add(log)
                db.session.commit()
            
            # Wait before next cycle
            time.sleep(30)
            
        except Exception as e:
            log = ProcessLog(
                message=f"Automation error: {str(e)}",
                level='error',
                user_id=user_id
            )
            db.session.add(log)
            db.session.commit()
            time.sleep(60)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)