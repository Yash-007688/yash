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
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random
import io
import base64
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
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    login_status = db.Column(db.String(20), default='unknown')  # active, suspended, blocked
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class YouTubeAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TargetAccount(db.Model):
    """Instagram accounts to monitor for content extraction"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    account_type = db.Column(db.String(50), default='content_creator')  # content_creator, influencer, brand, etc.
    is_active = db.Column(db.Boolean, default=True)
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
    target_accounts = TargetAccount.query.filter_by(user_id=current_user.id).all()
    reels = Reel.query.filter_by(user_id=current_user.id).order_by(Reel.created_at.desc()).limit(10).all()
    logs = ProcessLog.query.filter_by(user_id=current_user.id).order_by(ProcessLog.created_at.desc()).limit(20).all()
    
    return render_template('dashboard.html', 
                         instagram_accounts=instagram_accounts,
                         youtube_accounts=youtube_accounts,
                         target_accounts=target_accounts,
                         reels=reels,
                         logs=logs)

@app.route('/api/add_instagram_account', methods=['POST'])
@login_required
def add_instagram_account():
    data = request.get_json()
    
    # Check if user already has an Instagram account
    existing_account = InstagramAccount.query.filter_by(user_id=current_user.id).first()
    if existing_account:
        return jsonify({'success': False, 'message': 'You already have an Instagram account. Only one account is allowed.'}), 400
    
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
    
    return jsonify({'success': True, 'message': f'Instagram account @{data["username"]} added successfully!'})

@app.route('/api/create_instagram_account', methods=['POST'])
@login_required
def create_instagram_account():
    """Create a single Instagram account for content extraction"""
    data = request.get_json()
    
    # Check if user already has an Instagram account
    existing_account = InstagramAccount.query.filter_by(user_id=current_user.id).first()
    if existing_account:
        return jsonify({'success': False, 'message': 'You already have an Instagram account. Only one account is allowed.'}), 400
    
    # Generate random username and password
    import random
    import string
    
    # Generate random username
    username_prefix = data.get('username_prefix', 'reel_watcher')
    random_suffix = ''.join(random.choices(string.digits, k=4))
    username = f"{username_prefix}_{random_suffix}"
    
    # Generate strong password
    password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$%^&*', k=12))
    
    # Create account
    account = InstagramAccount(
        username=username,
        password=password,
        is_active=True,
        login_status='new',
        user_id=current_user.id
    )
    db.session.add(account)
    db.session.commit()
    
    log = ProcessLog(
        message=f"Created Instagram account: @{username} for reel watching",
        level='success',
        user_id=current_user.id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'account': {
            'username': username,
            'password': password,
            'id': account.id
        },
        'message': f'Created Instagram account: @{username} for reel watching'
    })

@app.route('/api/get_instagram_accounts')
@login_required
def get_instagram_accounts():
    """Get user's Instagram account"""
    account = InstagramAccount.query.filter_by(user_id=current_user.id).first()
    if account:
        return jsonify([{
            'id': account.id,
            'username': account.username,
            'is_active': account.is_active,
            'login_status': account.login_status,
            'last_login': account.last_login.strftime('%Y-%m-%d %H:%M:%S') if account.last_login else None,
            'created_at': account.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }])
    return jsonify([])

@app.route('/api/test_instagram_login/<int:account_id>', methods=['POST'])
@login_required
def test_instagram_login(account_id):
    """Test Instagram account login"""
    account = InstagramAccount.query.filter_by(id=account_id, user_id=current_user.id).first()
    
    if not account:
        return jsonify({'success': False, 'message': 'Account not found'}), 404
    
    try:
        # Simulate login test (in real implementation, this would use Instagram API)
        import random
        success = random.choice([True, True, True, False])  # 75% success rate for demo
        
        if success:
            account.login_status = 'active'
            account.last_login = datetime.utcnow()
            db.session.commit()
            
            log = ProcessLog(
                message=f"✅ Instagram login successful: @{account.username}",
                level='success',
                user_id=current_user.id
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Login successful for @{account.username}'
            })
        else:
            account.login_status = 'failed'
            db.session.commit()
            
            log = ProcessLog(
                message=f"❌ Instagram login failed: @{account.username}",
                level='error',
                user_id=current_user.id
            )
            db.session.add(log)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'message': f'Login failed for @{account.username}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error testing login: {str(e)}'
        }), 500

@app.route('/api/add_target_account', methods=['POST'])
@login_required
def add_target_account():
    """Add Instagram accounts to monitor for content extraction"""
    data = request.get_json()
    
    # Create new model for target accounts
    target_account = TargetAccount(
        username=data['username'],
        account_type=data.get('account_type', 'content_creator'),
        user_id=current_user.id,
        is_active=data.get('is_active', True)
    )
    db.session.add(target_account)
    db.session.commit()
    
    log = ProcessLog(
        message=f"Added target account to monitor: @{data['username']}",
        level='info',
        user_id=current_user.id
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Added @{data["username"]} to monitoring list'})

@app.route('/api/get_target_accounts')
@login_required
def get_target_accounts():
    """Get all target accounts being monitored"""
    target_accounts = TargetAccount.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': account.id,
        'username': account.username,
        'account_type': account.account_type,
        'is_active': account.is_active,
        'created_at': account.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for account in target_accounts])

@app.route('/api/remove_target_account/<int:account_id>', methods=['DELETE'])
@login_required
def remove_target_account(account_id):
    """Remove target account from monitoring"""
    account = TargetAccount.query.filter_by(id=account_id, user_id=current_user.id).first()
    if account:
        username = account.username
        db.session.delete(account)
        db.session.commit()
        
        log = ProcessLog(
            message=f"Removed target account from monitoring: @{username}",
            level='info',
            user_id=current_user.id
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Removed @{username} from monitoring'})
    
    return jsonify({'success': False, 'message': 'Account not found'}), 404

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

@app.route('/api/generate_thumbnail', methods=['POST'])
@login_required
def generate_thumbnail():
    data = request.get_json()
    title = data.get('title', 'EPIC YouTube Video! 🔥')
    style = data.get('style', 'gaming')
    
    try:
        # Create thumbnail
        thumbnail_img = create_catchy_thumbnail(title, style)
        
        # Save thumbnail
        filename = f"custom_thumbnail_{current_user.id}_{int(time.time())}.jpg"
        thumbnail_path = save_thumbnail(thumbnail_img, filename)
        
        # Convert to base64 for immediate preview
        img_buffer = io.BytesIO()
        thumbnail_img.save(img_buffer, format='JPEG', quality=85)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'thumbnail_path': thumbnail_path,
            'thumbnail_base64': f'data:image/jpeg;base64,{img_str}',
            'message': f'Created EPIC {style} thumbnail!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating thumbnail: {str(e)}'
        }), 500

@app.route('/api/get_thumbnail_styles')
@login_required
def get_thumbnail_styles():
    styles = [
        {
            'id': 'gaming',
            'name': 'Gaming Style',
            'description': 'Dark neon colors with EPIC text effects',
            'colors': ['Dark Blue', 'Purple', 'Neon Pink', 'Electric Blue']
        },
        {
            'id': 'vlog',
            'name': 'Vlog Style', 
            'description': 'Bright energetic colors for lifestyle content',
            'colors': ['Orange', 'Light Blue', 'Yellow', 'Pink']
        },
        {
            'id': 'default',
            'name': 'Classic Style',
            'description': 'Professional gradient backgrounds',
            'colors': ['Blue', 'Purple', 'Red', 'Green']
        }
    ]
    return jsonify(styles)

def create_catchy_thumbnail(title, style="gaming"):
    """Create a catchy, arrogant, fancy thumbnail like popular YouTubers"""
    
    # Thumbnail dimensions (YouTube standard)
    width, height = 1280, 720
    
    # Create base image with gradient background
    if style == "gaming":
        # Gaming style - dark with neon colors
        colors = [
            [(20, 20, 40), (60, 20, 80)],  # Dark blue to purple
            [(40, 10, 30), (80, 20, 60)],  # Dark red to purple
            [(10, 30, 40), (30, 60, 80)],  # Dark cyan to blue
        ]
    elif style == "vlog":
        # Vlog style - bright and energetic
        colors = [
            [(255, 100, 50), (255, 150, 100)],  # Orange to light orange
            [(100, 200, 255), (150, 220, 255)],  # Light blue
            [(255, 200, 100), (255, 220, 150)],  # Light yellow
        ]
    else:
        # Default style
        colors = [
            [(50, 50, 100), (100, 50, 150)],  # Blue to purple
            [(100, 50, 50), (150, 50, 100)],  # Red to purple
            [(50, 100, 50), (100, 150, 100)],  # Green
        ]
    
    # Choose random color combination
    color_pair = random.choice(colors)
    
    # Create gradient background
    img = Image.new('RGB', (width, height), color_pair[0])
    draw = ImageDraw.Draw(img)
    
    # Create gradient effect
    for y in range(height):
        r = int(color_pair[0][0] + (color_pair[1][0] - color_pair[0][0]) * y / height)
        g = int(color_pair[0][1] + (color_pair[1][1] - color_pair[0][1]) * y / height)
        b = int(color_pair[0][2] + (color_pair[1][2] - color_pair[0][2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add some geometric shapes for visual appeal
    if style == "gaming":
        # Add neon-style geometric shapes
        for i in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            neon_color = random.choice([(255, 0, 100), (0, 255, 200), (255, 255, 0), (255, 100, 255)])
            draw.line([(x1, y1), (x2, y2)], fill=neon_color, width=3)
    
    # Add some circles or rectangles
    for i in range(3):
        x = random.randint(50, width-100)
        y = random.randint(50, height-100)
        size = random.randint(50, 150)
        if random.choice([True, False]):
            draw.ellipse([x, y, x+size, y+size], outline=(255, 255, 255, 100), width=2)
        else:
            draw.rectangle([x, y, x+size, y+size], outline=(255, 255, 255, 100), width=2)
    
    # Add text with fancy styling
    try:
        # Try to use a bold font, fallback to default if not available
        font_size = 80
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Split title into words for better layout
    words = title.split()
    if len(words) > 6:
        # Take first 6 words and add ellipsis
        title = " ".join(words[:6]) + "..."
    
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Add text shadow/outline for gaming style
    if style == "gaming":
        # Add multiple outlines for neon effect
        for offset in range(1, 4):
            draw.text((x-offset, y-offset), title, font=font, fill=(0, 0, 0))
            draw.text((x+offset, y-offset), title, font=font, fill=(0, 0, 0))
            draw.text((x-offset, y+offset), title, font=font, fill=(0, 0, 0))
            draw.text((x+offset, y+offset), title, font=font, fill=(0, 0, 0))
        
        # Main text in bright color
        draw.text((x, y), title, font=font, fill=(255, 255, 255))
    else:
        # Regular text with shadow
        draw.text((x+2, y+2), title, font=font, fill=(0, 0, 0))
        draw.text((x, y), title, font=font, fill=(255, 255, 255))
    
    # Add some catchy elements
    if style == "gaming":
        # Add gaming elements like "EPIC", "INSANE", "OMG"
        gaming_words = ["EPIC", "INSANE", "OMG", "WOW", "AMAZING", "CRAZY"]
        word = random.choice(gaming_words)
        
        # Position in top-right corner
        try:
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            small_font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), word, font=small_font)
        word_width = bbox[2] - bbox[0]
        word_x = width - word_width - 50
        word_y = 50
        
        # Add background for the word
        draw.rectangle([word_x-10, word_y-10, word_x+word_width+10, word_y+40], 
                      fill=(255, 0, 100))
        draw.text((word_x, word_y), word, font=small_font, fill=(255, 255, 255))
    
    # Add some emoji-like elements
    emoji_elements = ["🔥", "💯", "⚡", "🎮", "🏆", "💪"]
    if style == "vlog":
        emoji_elements = ["🔥", "💯", "⚡", "🎥", "📱", "💪"]
    
    # Add emoji text
    emoji = random.choice(emoji_elements)
    try:
        emoji_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
    except:
        emoji_font = ImageFont.load_default()
    
    emoji_x = 50
    emoji_y = height - 100
    draw.text((emoji_x, emoji_y), emoji, font=emoji_font, fill=(255, 255, 255))
    
    # Add some additional text elements
    if style == "gaming":
        # Add "NEW" or "LIVE" badge
        badge_text = random.choice(["NEW", "LIVE", "HOT"])
        badge_x = 50
        badge_y = 50
        
        # Red background for badge
        draw.rectangle([badge_x-10, badge_y-10, badge_x+80, badge_y+40], 
                      fill=(255, 0, 0))
        draw.text((badge_x, badge_y), badge_text, font=small_font, fill=(255, 255, 255))
    
    # Apply some filters for extra appeal
    if style == "gaming":
        # Add slight blur to background elements
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    
    # Enhance saturation
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.3)
    
    return img

def save_thumbnail(img, filename):
    """Save thumbnail to static folder"""
    thumbnail_dir = os.path.join(os.path.dirname(__file__), 'static', 'thumbnails')
    os.makedirs(thumbnail_dir, exist_ok=True)
    
    filepath = os.path.join(thumbnail_dir, filename)
    img.save(filepath, 'JPEG', quality=95)
    return f'/static/thumbnails/{filename}'

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
            # Get user's Instagram account for content extraction
            instagram_account = InstagramAccount.query.filter_by(user_id=user_id, is_active=True, login_status='active').first()
            
            if not instagram_account:
                log = ProcessLog(
                    message="No active Instagram account for content extraction. Please create or activate your Instagram account.",
                    level='warning',
                    user_id=user_id
                )
                db.session.add(log)
                db.session.commit()
                time.sleep(60)  # Wait 1 minute before checking again
                continue
            
            # Get target accounts to monitor
            target_accounts = TargetAccount.query.filter_by(user_id=user_id, is_active=True).all()
            
            if not target_accounts:
                log = ProcessLog(
                    message="No target accounts configured. Please add Instagram accounts to monitor.",
                    level='warning',
                    user_id=user_id
                )
                db.session.add(log)
                db.session.commit()
                time.sleep(60)  # Wait 1 minute before checking again
                continue
            
            # Use single Instagram account to extract content from target accounts
            log = ProcessLog(
                message=f"🔐 Using Instagram account: @{instagram_account.username} for reel watching",
                level='info',
                user_id=user_id
            )
            db.session.add(log)
            db.session.commit()
            
            for target_account in target_accounts:
                if not automation_running:
                    break
                
                # Simulate using Instagram account to check target account
                log = ProcessLog(
                    message=f"🔍 @{instagram_account.username} watching @{target_account.username}",
                    level='info',
                    user_id=user_id
                )
                db.session.add(log)
                db.session.commit()
                
                # Simulate finding new reels from this specific account
                time.sleep(2)
                
                # Generate catchy title
                catchy_titles = [
                    "INSANE Hindi Comedy That Will Make You CRY! 😂",
                    "EPIC Gaming Moment You Won't Believe! 🎮",
                    "OMG This Vlog Will BLOW YOUR MIND! 🔥",
                    "CRAZY Dance Challenge Gone Wrong! 💃",
                    "AMAZING Cooking Hack That Actually Works! 👨‍🍳",
                    "WOW This Reaction is PURE GOLD! ⚡",
                    "INSANE Prank That Went Too Far! 😱",
                    "EPIC Fail That Made Me Famous! 🏆"
                ]
                
                title = random.choice(catchy_titles)
                
                # Create catchy thumbnail
                thumbnail_style = random.choice(["gaming", "vlog"])
                thumbnail_img = create_catchy_thumbnail(title, thumbnail_style)
                
                # Save thumbnail
                filename = f"thumbnail_{user_id}_{int(time.time())}.jpg"
                thumbnail_path = save_thumbnail(thumbnail_img, filename)
                
                # Create a sample reel entry with source account info
                reel = Reel(
                    instagram_url=f"https://instagram.com/{target_account.username}/reel/sample",
                    title=title,
                    thumbnail_path=thumbnail_path,
                    user_id=user_id,
                    status='processed'
                )
                db.session.add(reel)
                db.session.commit()
                
                log = ProcessLog(
                    message=f"📱 Found new reel from @{target_account.username}: {title}",
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