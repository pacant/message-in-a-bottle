from flask import Blueprint, redirect, render_template
from flask_login import login_user, logout_user

from monolith.database import User, db
from monolith.forms import LoginForm

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    is_reported = False
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password']
        q = db.session.query(User).filter(User.email == email, User.is_active.is_(True))
        active_user = q.first()
        is_reported = db.session.query(User).filter(User.email == email, User.is_reported.is_(True)).first() is not None
        if active_user is None and not is_reported:
            return redirect('/create_user')
        if not is_reported and active_user is not None and active_user.authenticate(password):
            login_user(active_user)
            return redirect('/')
    return render_template('login.html', form=form, is_reported=is_reported)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect('/')
