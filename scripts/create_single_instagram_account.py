#!/usr/bin/env python3
"""
Create a single Instagram account for the project (username: instabro by default).

Usage:
  source venv/bin/activate && python scripts/create_single_instagram_account.py | cat
"""

import os
import sys
import random
import string
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app, db, User, InstagramAccount, ProcessLog
from werkzeug.security import generate_password_hash


def generate_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(random.choices(characters, k=length))


def main():
    desired_username = os.environ.get('INSTAGRAM_USERNAME', 'instabro')
    default_email = os.environ.get('DEFAULT_USER_EMAIL', 'admin@example.com')
    default_username = os.environ.get('DEFAULT_USER_USERNAME', 'admin')
    default_password = os.environ.get('DEFAULT_USER_PASSWORD', 'admin123')

    with app.app_context():
        # Ensure at least one user exists
        user = User.query.filter_by(email=default_email).first()
        if not user:
            user = User(email=default_email, username=default_username, password_hash=generate_password_hash(default_password))
            db.session.add(user)
            db.session.commit()
            print(f"Created default user: {default_email} (username: {default_username}) / {default_password}")

        # Enforce single account: delete others if they exist and are not the desired one
        existing_accounts = InstagramAccount.query.filter_by(user_id=user.id).all()

        keep = None
        for acc in existing_accounts:
            if acc.username == desired_username and keep is None:
                keep = acc
            else:
                db.session.delete(acc)
        if existing_accounts:
            db.session.commit()

        if keep is None:
            # Create the single account with the desired username (fallback to suffixed if conflict)
            base_username = desired_username
            username = base_username
            suffix = 0
            while InstagramAccount.query.filter_by(username=username).first() is not None:
                suffix += 1
                username = f"{base_username}{suffix}"

            password_plain = generate_password()
            account = InstagramAccount(
                username=username,
                password=password_plain,
                is_active=True,
                login_status='new',
                user_id=user.id
            )
            db.session.add(account)
            db.session.commit()

            log = ProcessLog(
                message=f"Created single Instagram account: @{username}",
                level='success',
                user_id=user.id
            )
            db.session.add(log)
            db.session.commit()
            print(f"Created Instagram account => username: @{username}  password: {password_plain}")
        else:
            print(f"Keeping existing single Instagram account: @{keep.username}")

        # Final check: list the one account
        final = InstagramAccount.query.filter_by(user_id=user.id).all()
        print("\nCurrent Instagram accounts for user:")
        for acc in final:
            print(f" - @{acc.username} (status={acc.login_status}, active={acc.is_active})")


if __name__ == '__main__':
    main()

