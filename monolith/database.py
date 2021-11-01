from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    date_of_birth = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id

class Message(db.Model):

    __tablename__ = 'message'


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Unicode(128))
    id_sender = db.Column(db.Unicode(128))
    id_receiver = db.Column(db.Unicode(128))
    draft = db.Column(db.Boolean, default = False)
    is_read = db.Column(db.Boolean, default=False)
    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

     '''
     logic for when a receiver reads a message
     '''
    def read(self):
        self.is_read = True
        pass    