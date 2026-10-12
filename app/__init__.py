from flask import Flask
from config import Config
from app.extensions import db,login_manager,csrf
def create_app(config_class=Config):
 app=Flask(__name__,template_folder='../templates',static_folder='../static'); app.config.from_object(config_class); db.init_app(app); login_manager.init_app(app); csrf.init_app(app)
 login_manager.login_view='auth.login'; login_manager.login_message_category='info'
 from app.models import User
 @login_manager.user_loader
 def load_user(uid): return db.session.get(User,int(uid))
 from app.routes import main,auth
 app.register_blueprint(main); app.register_blueprint(auth,url_prefix='/auth')
 with app.app_context(): db.create_all()
 return app
