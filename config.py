import os
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent
class Config:
 SECRET_KEY=os.environ.get('SECRET_KEY','local-dev-only-change-this')
 SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL',f"sqlite:///{BASE_DIR/'nexus.db'}").replace('postgres://','postgresql://',1)
 SQLALCHEMY_TRACK_MODIFICATIONS=False
 SESSION_COOKIE_HTTPONLY=True
 SESSION_COOKIE_SAMESITE='Lax'
 SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE','0')=='1'
