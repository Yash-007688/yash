#!/usr/bin/env python3
"""
Reset the SQLite database schema (DROPS ALL TABLES) and recreates them.

Usage:
  source venv/bin/activate && python scripts/reset_db.py | cat
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app, db


def main():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset complete: dropped and recreated all tables.")


if __name__ == '__main__':
    main()

