from flask import Flask 
 
def create_app(): 
 
    app = Flask(__name__) 
 
     # Load configuration 
    app.config.from_object('config.Config') 
    app.config.from_pyfile('../instance/config.py') 
 
    with app.app_context(): 
         # Import parts of our application 
        from . import routes 
 
        return app 
