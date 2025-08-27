#!/usr/bin/env python3
"""
Maintenance script: Keep only ONE InstagramAccount per user (newest), remove others.

Usage:
  source venv/bin/activate && python scripts/keep_one_instagram_account.py
"""

from datetime import datetime
import os
import sys

# Ensure project root is on sys.path so we can import app
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app, db, InstagramAccount, User, ProcessLog


def prune_instagram_accounts():
    with app.app_context():
        users = User.query.all()
        total_removed = 0
        for user in users:
            accounts = (
                InstagramAccount.query.filter_by(user_id=user.id)
                .order_by(InstagramAccount.created_at.desc())
                .all()
            )
            if not accounts:
                continue

            keep = accounts[0]
            remove = accounts[1:]
            removed_usernames = []
            for acc in remove:
                removed_usernames.append(acc.username)
                db.session.delete(acc)
                total_removed += 1
            db.session.commit()

            # Log the action
            message = (
                f"🔒 Enforced single Instagram account for user {user.email or user.id}. "
                f"Kept @{keep.username}. Removed: {', '.join(removed_usernames) if removed_usernames else 'none'}"
            )
            log = ProcessLog(message=message, level='info', user_id=user.id)
            db.session.add(log)
            db.session.commit()

            print(message)

        print(f"Done. Removed {total_removed} extra Instagram accounts across all users.")


if __name__ == "__main__":
    prune_instagram_accounts()

