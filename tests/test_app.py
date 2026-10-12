def register(client,email="test@example.com"):
 return client.post("/auth/register",data={"name":"Test User","email":email,"password":"correct-horse-battery"},follow_redirects=True)
def test_landing(client):
 r=client.get("/");assert r.status_code==200 and b"Nexus" in r.data
def test_register_and_demo(client):
 assert register(client).status_code==200
 assert client.post("/networks/demo",follow_redirects=True).status_code==200
 from app.models import Network
 with client.application.app_context(): n=Network.query.first();nid=n.id
 r=client.get(f"/api/networks/{nid}/topology");assert r.status_code==200 and len(r.json["nodes"])==6
def test_duplicate_email(client):
 register(client);client.post("/auth/logout");assert b"already exists" in register(client).data
def test_dashboard_requires_login(client): assert client.get("/dashboard").status_code in (302,303)
