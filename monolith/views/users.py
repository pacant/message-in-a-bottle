from flask import Blueprint, redirect, render_template, request

from monolith.database import User, Blacklist, db
from monolith.forms import UserForm
from flask_login import current_user

users = Blueprint('users', __name__)


@users.route('/users')
def _users():
    _users = db.session.query(User)
    return render_template("users.html", users=_users)


@users.route('/create_user', methods=['POST', 'GET'])
def create_user():
    form = UserForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            """ Password should be hashed with some salt. For example if you choose a hash function x,
            where x is in [md5, sha1, bcrypt], the hashed_password should be = x(password + s) where
            s is a secret key.
            """
            result = db.session.query(User).filter(User.email == new_user.email).all()
            if not result:
                new_user.set_password(form.password.data)
                db.session.add(new_user)
                db.session.commit()
                return redirect('/')
            return render_template("create_user.html",emailError = True, form=form)
    elif request.method == 'GET':
        return render_template('create_user.html', form=form)
    else:
        raise RuntimeError('This should not happen!')


@users.route('/delete_user')
def delete_user():
    User.query.filter_by(id=current_user.id).delete()
    db.session.commit()
    return redirect('/')


@users.route('/userinfo')
def get_user_info():
    user = db.session.query(User).filter(current_user.id == User.id).all()
    return render_template('user_info.html', user=user)


@users.route('/blacklist/add', methods=['GET', 'POST'])
def add_user_to_blacklist():
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'POST':
            blacklist = Blacklist()
            blacklist.id_user = current_user.id
            email = request.form.get('email')
            blacklist.id_blacklisted = db.session.query(User.id).filter(User.email == email)
            db.session.add(blacklist)
            db.session.commit()
            return redirect('/blacklist')
        else:
            users = db.session.query(User).filter(User.email != current_user.email)
            return render_template('add_to_blacklist.html', users=users)
    else:
        return redirect('/')


@users.route('/blacklist', methods=['GET'])
def get_blacklist():
    blacklist = db.session.query(Blacklist, User).filter(
                Blacklist.id_blacklisted == User.id).filter(
                    Blacklist.id_user==current_user.id
                ).all()
    return render_template('blacklist.html', blacklist=blacklist)


@users.route('/blacklist/remove', methods=['GET', 'POST'])
def remove_user_from_blacklist():
    if current_user is not None and hasattr(current_user, 'id'):
        if request.method == 'POST':
            email = request.form["radioEmail"]
            id_blklst = db.session.query(User.id).filter(User.email == email).all()
            db.session.query(Blacklist).filter(Blacklist.id_blacklisted == id_blklst[0].id).delete()
            db.session.commit()
            return redirect('/blacklist')
        else:
            blacklist = db.session.query(Blacklist, User).filter(
                Blacklist.id_blacklisted == User.id).filter(
                    Blacklist.id_user==current_user.id
                ).all()
            return render_template('blacklist.html', blacklist=blacklist)
    else:
        return redirect('/')