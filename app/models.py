from datetime import datetime,timezone
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from app.extensions import db
def utcnow(): return datetime.now(timezone.utc)
class User(UserMixin,db.Model):
 id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(100),nullable=False); email=db.Column(db.String(180),unique=True,nullable=False,index=True); password_hash=db.Column(db.String(255),nullable=False)
 networks=db.relationship("Network",back_populates="owner",cascade="all, delete-orphan")
 def set_password(self,p): self.password_hash=generate_password_hash(p)
 def check_password(self,p): return check_password_hash(self.password_hash,p)
class Network(db.Model):
 id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),nullable=False); description=db.Column(db.String(500),default=""); location=db.Column(db.String(120),default="Primary site"); owner_id=db.Column(db.Integer,db.ForeignKey("user.id",ondelete="CASCADE"),nullable=False,index=True); created_at=db.Column(db.DateTime(timezone=True),default=utcnow)
 owner=db.relationship("User",back_populates="networks"); devices=db.relationship("Device",back_populates="network",cascade="all, delete-orphan"); incidents=db.relationship("Incident",back_populates="network",cascade="all, delete-orphan")
class Device(db.Model):
 id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),nullable=False); hostname=db.Column(db.String(120),default=""); ip_address=db.Column(db.String(45),nullable=False); device_type=db.Column(db.String(30),default="server",nullable=False); status=db.Column(db.String(20),default="unknown",nullable=False); response_ms=db.Column(db.Float); x=db.Column(db.Float,default=300); y=db.Column(db.Float,default=200); is_simulated=db.Column(db.Boolean,default=True); last_checked_at=db.Column(db.DateTime(timezone=True)); network_id=db.Column(db.Integer,db.ForeignKey("network.id",ondelete="CASCADE"),nullable=False,index=True)
 network=db.relationship("Network",back_populates="devices"); checks=db.relationship("MonitoringCheck",back_populates="device",cascade="all, delete-orphan",order_by="desc(MonitoringCheck.checked_at)")
class MonitoringCheck(db.Model):
 id=db.Column(db.Integer,primary_key=True); status=db.Column(db.String(20),nullable=False); response_ms=db.Column(db.Float); detail=db.Column(db.String(300),default=""); checked_at=db.Column(db.DateTime(timezone=True),default=utcnow,index=True); device_id=db.Column(db.Integer,db.ForeignKey("device.id",ondelete="CASCADE"),nullable=False,index=True); device=db.relationship("Device",back_populates="checks")
class Incident(db.Model):
 id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(180),nullable=False); severity=db.Column(db.String(20),default="medium"); status=db.Column(db.String(20),default="open"); description=db.Column(db.Text,default=""); opened_at=db.Column(db.DateTime(timezone=True),default=utcnow); resolved_at=db.Column(db.DateTime(timezone=True)); network_id=db.Column(db.Integer,db.ForeignKey("network.id",ondelete="CASCADE"),nullable=False,index=True); device_id=db.Column(db.Integer,db.ForeignKey("device.id",ondelete="SET NULL")); network=db.relationship("Network",back_populates="incidents"); device=db.relationship("Device")
