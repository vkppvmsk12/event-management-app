from flask import Flask
from .views import views
from .auth import auth
#from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "abc"

    '''login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return'''
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    
    return app