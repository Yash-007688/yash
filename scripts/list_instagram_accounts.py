#!/usr/bin/env python3
"""
List Instagram accounts per user to verify which account remains.

Usage:
  source venv/bin/activate && python scripts/list_instagram_accounts.py | cat
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app, db, InstagramAccount, User


def list_accounts():
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found.")
            return
        for user in users:
            accounts = InstagramAccount.query.filter_by(user_id=user.id).order_by(InstagramAccount.created_at.desc()).all()
            print(f"User: {user.email if hasattr(user, 'email') and user.email else user.id}")
            if not accounts:
                print("  No Instagram accounts.")
            else:
                for i, acc in enumerate(accounts, 1):
                    print(f"  {i}. @{acc.username} (status={acc.login_status}, active={acc.is_active})")


if __name__ == "__main__":
    list_accounts()

