import os
from .routes import db
from flask import Flask

#Application factory

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY= "dev",
            DATABASE=os.path.join(app.instance_path,"data.db"),
        )
    #ensuring instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    db.init_app(app)

    from .routes import auth,user,home,groups,sessions,tasks,members,joinrequests,search
    
    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(groups.bp)
    app.register_blueprint(sessions.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(members.bp)
    app.register_blueprint(joinrequests.bp)
    app.register_blueprint(search.bp)

    return app
