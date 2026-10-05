from flask import Flask


def create_app():
    app = Flask(__name__)
    
    from app.routes import bp_health
    app.register_blueprint(bp_health)
    
    return app
    
