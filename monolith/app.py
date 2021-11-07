from flask import Flask

from monolith.auth import login_manager
from monolith.database import ContentFilter, db
from monolith.views import blueprints
import json


def create_app():
    app = Flask(__name__)
    app.config['WTF_CSRF_SECRET_KEY'] = 'A SECRET KEY'
    app.config['SECRET_KEY'] = 'ANOTHER ONE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../mmiab.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # create a first admin user
    with app.app_context():
        q = db.session.query(ContentFilter).filter(ContentFilter.name == 'Default')
        content_filter = q.first()
        if content_filter is None:
            default_content_filter = ContentFilter()
            default_content_filter.name = 'Default'
            default_content_filter.private = False
            word_list = []
            file1 = open('monolith/badwords.txt', 'r')
            Lines = file1.readlines()
            for line in Lines:
                word_list.append(line.strip())
            word_list.sort(key=lambda el: len(el))
            default_content_filter.words = json.dumps(word_list)
            db.session.add(default_content_filter)
            db.session.commit()

    return app


app = create_app()


if __name__ == '__main__':
    app.run()
