from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import ForeignKey

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    date_of_birth = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_anonymous = False
    trials = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    is_reported = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self.is_active and self._authenticated

    def authenticate(self, password):
        checked = self.is_active and check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id


class Message(db.Model):

    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Unicode(128))
    id_sender = db.Column(db.Unicode(128), ForeignKey('user.id'))
    id_receiver = db.Column(db.Unicode(128), ForeignKey('user.id'))
    draft = db.Column(db.Boolean, default=False)
    delivered = db.Column(db.Boolean, default=False)
    read = db.Column(db.Boolean, default=False)
    date_delivery = db.Column(db.DateTime(timezone=True))
    date_send = db.Column(db.DateTime(timezone=True))
    deleted = db.Column(db.Boolean, default=False)
    blacklisted = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)


class Blacklist(db.Model):

    __tablename__ = 'blacklist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Unicode(128), ForeignKey('user.id'))
    id_blacklisted = db.Column(db.Unicode(128), ForeignKey('user.id'))

    def __init__(self, *args, **kw):
        super(Blacklist, self).__init__(*args, **kw)


class Attachments(db.Model):

    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_message = db.Column(db.Unicode(128), ForeignKey('message.id'))
    data = db.Column(db.LargeBinary)


class Reports(db.Model):

    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Unicode(128), ForeignKey('user.id'))
    id_reported = db.Column(db.Unicode(128), ForeignKey('user.id'))

    def __init__(self, *args, **kw):
        super(Reports, self).__init__(*args, **kw)


class ContentFilter(db.Model):

    __tablename__ = 'content_filter'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Unicode(128))
    words = db.Column(db.Unicode(128))
    private = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kw):
        super(ContentFilter, self).__init__(*args, **kw)


class UserContentFilter(db.Model):

    __tablename__ = 'user_content_filter'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, ForeignKey('user.id'))
    id_content_filter = db.Column(db.Integer, ForeignKey('content_filter.id'))
    active = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kw):
        super(UserContentFilter, self).__init__(*args, **kw)
