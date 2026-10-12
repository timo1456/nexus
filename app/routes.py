import ipaddress,random
from datetime import datetime,timezone
from flask import Blueprint,render_template,redirect,url_for,flash,request,jsonify,abort
from flask_login import current_user,login_user,logout_user,login_required
from app.extensions import db
from app.models import User,Network,Device,MonitoringCheck,Incident
main=Blueprint("main",__name__); auth=Blueprint("auth",__name__)
def owned(nid):
 n=Network.query.filter_by(id=nid,owner_id=current_user.id).first()
 if not n: abort(404)
 return n
@main.route("/")
def landing(): return redirect(url_for("main.dashboard")) if current_user.is_authenticated else render_template("landing.html")
@auth.route("/register",methods=["GET","POST"])
def register():
 if current_user.is_authenticated:return redirect(url_for("main.dashboard"))
 if request.method=="POST":
  name=request.form.get("name","").strip(); email=request.form.get("email","").strip().lower(); pw=request.form.get("password","")
  if not name or len(name)>100 or not email or len(pw)<10: flash("Enter your name and email, and use a password of at least 10 characters.","error")
  elif User.query.filter_by(email=email).first():flash("An account with that email already exists.","error")
  else:
   u=User(name=name,email=email);u.set_password(pw);db.session.add(u);db.session.commit();login_user(u);return redirect(url_for("main.dashboard"))
 return render_template("auth.html",mode="register")
@auth.route("/login",methods=["GET","POST"])
def login():
 if current_user.is_authenticated:return redirect(url_for("main.dashboard"))
 if request.method=="POST":
  u=User.query.filter_by(email=request.form.get("email","").strip().lower()).first()
  if u and u.check_password(request.form.get("password","")):login_user(u,remember=bool(request.form.get("remember")));return redirect(url_for("main.dashboard"))
  flash("Email or password was not recognised.","error")
 return render_template("auth.html",mode="login")
@auth.route("/logout",methods=["POST"])
@login_required
def logout():logout_user();return redirect(url_for("main.landing"))
@main.route("/dashboard")
@login_required
def dashboard():
 ns=Network.query.filter_by(owner_id=current_user.id).order_by(Network.id.desc()).all(); ds=Device.query.join(Network).filter(Network.owner_id==current_user.id).all()
 inc=Incident.query.join(Network).filter(Network.owner_id==current_user.id,Incident.status=="open").order_by(Incident.opened_at.desc()).all()
 checks=MonitoringCheck.query.join(Device).join(Network).filter(Network.owner_id==current_user.id).order_by(MonitoringCheck.checked_at.desc()).limit(8).all()
 return render_template("dashboard.html",networks=ns,devices=ds,incidents=inc,checks=checks,total=len(ds),online=sum(d.status=="online" for d in ds),degraded=sum(d.status=="degraded" for d in ds),offline=sum(d.status=="offline" for d in ds))
@main.route("/networks/new",methods=["POST"])
@login_required
def create_network():
 name=request.form.get("name","").strip()
 if not name or len(name)>120:flash("Network name is required.","error")
 else:
  n=Network(name=name,location=request.form.get("location","").strip()[:120] or "Primary site",description=request.form.get("description","").strip()[:500],owner=current_user);db.session.add(n);db.session.commit();return redirect(url_for("main.network_detail",network_id=n.id))
 return redirect(url_for("main.dashboard"))
@main.route("/networks/demo",methods=["POST"])
@login_required
def demo():
 if Network.query.filter_by(owner_id=current_user.id,name="Northstar Office Network").first():return redirect(url_for("main.dashboard"))
 n=Network(name="Northstar Office Network",location="Lagos · HQ",description="Sample network. Monitoring is simulated; no physical devices contacted.",owner=current_user);db.session.add(n);db.session.flush()
 rows=[("Edge Router","edge-rtr-01","192.168.10.1","router","online",4.2,150,100),("Core Switch","core-sw-01","192.168.10.2","switch","online",2.1,350,120),("Access Point","ap-west-01","192.168.10.10","access_point","online",8.6,540,100),("File Server","files-01","192.168.10.20","server","online",12.4,350,290),("Workstation 04","ws-04","192.168.10.44","workstation","degraded",146.2,540,300),("Backup Node","backup-01","192.168.10.30","server","offline",None,150,300)]
 for name,host,ip,kind,status,lat,x,y in rows:
  d=Device(name=name,hostname=host,ip_address=ip,device_type=kind,status=status,response_ms=lat,x=x,y=y,network=n,last_checked_at=datetime.now(timezone.utc));db.session.add(d);db.session.flush();db.session.add(MonitoringCheck(status=status,response_ms=lat,detail="Seeded demo observation; not a live probe.",device=d))
 backup=next(d for d in n.devices if d.hostname=="backup-01");db.session.add(Incident(title="Backup Node is unreachable",severity="high",description="Sample incident from simulated observations.",network=n,device=backup));db.session.commit();flash("Demo workspace loaded with six simulated devices.","success");return redirect(url_for("main.dashboard"))
@main.route("/networks/<int:network_id>")
@login_required
def network_detail(network_id):
 n=owned(network_id); checks=MonitoringCheck.query.join(Device).filter(Device.network_id==n.id).order_by(MonitoringCheck.checked_at.desc()).limit(25).all();return render_template("network.html",network=n,checks=checks)
@main.route("/networks/<int:network_id>/devices",methods=["POST"])
@login_required
def add_device(network_id):
 n=owned(network_id);name=request.form.get("name","").strip();ip=request.form.get("ip_address","").strip();kind=request.form.get("device_type","server")
 try:ipaddress.ip_address(ip)
 except ValueError:flash("Enter a valid IPv4 or IPv6 address.","error");return redirect(url_for("main.network_detail",network_id=n.id))
 if not name or kind not in {"router","switch","server","workstation","access_point","firewall"}:flash("Provide a device name and type.","error")
 elif Device.query.filter_by(network_id=n.id,ip_address=ip).first():flash("IP address already exists in this network.","error")
 else:db.session.add(Device(name=name,hostname=request.form.get("hostname","")[:120],ip_address=ip,device_type=kind,network=n,x=180+(len(n.devices)%3)*190,y=150+(len(n.devices)//3)*150));db.session.commit();flash("Device added in simulation mode; no live device was contacted.","success")
 return redirect(url_for("main.network_detail",network_id=n.id))
@main.route("/networks/<int:network_id>/check",methods=["POST"])
@login_required
def check(network_id):
 n=owned(network_id);ds=[d for d in n.devices if d.is_simulated]
 for d in ds:
  d.status=random.choices(["online","degraded","offline"],[88,9,3])[0];d.response_ms=round(random.uniform(3,48),1) if d.status!="offline" else None;d.last_checked_at=datetime.now(timezone.utc)
  db.session.add(MonitoringCheck(status=d.status,response_ms=d.response_ms,detail="Simulated probe observation.",device=d))
  if d.status=="offline" and not Incident.query.filter_by(network_id=n.id,device_id=d.id,status="open").first():db.session.add(Incident(title=f"{d.name} is unreachable",severity="high",description="Generated by a simulated probe.",network=n,device=d))
 db.session.commit();flash(f"Completed {len(ds)} simulated checks. No physical devices contacted.","success");return redirect(url_for("main.network_detail",network_id=n.id))
@main.route("/incidents")
@login_required
def incidents():
 rows=Incident.query.join(Network).filter(Network.owner_id==current_user.id).order_by(Incident.opened_at.desc()).all();return render_template("incidents.html",incidents=rows)
@main.route("/incidents/<int:incident_id>/resolve",methods=["POST"])
@login_required
def resolve(incident_id):
 i=Incident.query.join(Network).filter(Incident.id==incident_id,Network.owner_id==current_user.id).first_or_404();i.status="resolved";i.resolved_at=datetime.now(timezone.utc);db.session.commit();return redirect(url_for("main.incidents"))
@main.route("/api/networks/<int:network_id>/topology")
@login_required
def topology(network_id):
 n=owned(network_id);ds=n.devices;nodes=[{"data":{"id":str(d.id),"label":d.name,"ip":d.ip_address,"status":d.status},"position":{"x":d.x,"y":d.y}} for d in ds];hubs=[d for d in ds if d.device_type=="switch"] or [d for d in ds if d.device_type=="router"] or ds[:1];edges=[]
 if hubs:
  root=hubs[0];edges=[{"data":{"id":f"e{root.id}-{d.id}","source":str(root.id),"target":str(d.id)}} for d in ds if d.id!=root.id]
 return jsonify(nodes=nodes,edges=edges)
@main.route("/troubleshooter")
@login_required
def troubleshooter():
 ds=Device.query.join(Network).filter(Network.owner_id==current_user.id).all();return render_template("troubleshooter.html",devices=ds)
@main.route("/api/diagnose",methods=["POST"])
@login_required
def diagnose():
 try:did=int((request.get_json(silent=True) or {}).get("device_id",0))
 except (ValueError,TypeError):return jsonify(error="Choose a valid device."),400
 d=Device.query.join(Network).filter(Device.id==did,Network.owner_id==current_user.id).first()
 if not d:return jsonify(error="Device not found in your workspace."),404
 if d.status=="offline":fs=[("critical","Device marked unreachable","Stored observation reports no response; status is simulated."),("check","Verify link and power","Check power, cabling, interface state, and link lights."),("check","Check addressing and path","Validate IP, subnet, gateway, VLAN membership, and routing.")]
 elif d.status=="degraded" or (d.response_ms is not None and d.response_ms>100):fs=[("warning","Elevated response time",f"Stored response time: {d.response_ms} ms."),("check","Compare path latency","Inspect congestion, duplex mismatch, packet loss, and gateway latency.")]
 else:fs=[("healthy","Latest observation is healthy","Online status does not guarantee application-level health."),("check","Validate service reachability","Check service ports, DNS resolution, and application logs if issues persist.")]
 return jsonify(device=d.name,mode="rule-based",disclaimer="Guidance uses stored demo data, not a verified root cause or AI verdict.",findings=[dict(level=a,title=b,detail=c) for a,b,c in fs])
