from flask import Blueprint, redirect, render_template, request, abort
from flask_login.utils import login_required
from monolith.database import UserContentFilter, ContentFilter, User, Blacklist, db
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
            return render_template("create_user.html", emailError=True, form=form)
    else:
        return render_template('create_user.html', form=form)


@login_required
@users.route('/delete_user')
def delete_user():
    User.query.filter_by(id=current_user.id).delete()
    db.session.commit()
    return redirect('/')


@login_required
@users.route('/userinfo')
def get_user_info():
    user = db.session.query(User).filter(current_user.id == User.id).all()
    return render_template('user_info.html', user=user)


@login_required
@users.route('/userinfo/content_filter')
def get_user_content_filter_list():

    list = db.session.query(UserContentFilter).filter(
        UserContentFilter.id_user == current_user.id
    ).all()

    results = db.session.query(ContentFilter, UserContentFilter).filter(
        ContentFilter.id.in_(list)
    ).join(UserContentFilter, isouter=True).union_all(
        db.session.query(ContentFilter, UserContentFilter).filter(
            ContentFilter.private.is_(False)
        ).join(UserContentFilter, isouter=True)
    )
    content_filter_list = []
    for result in results:
        content_filter_list.append({'id': result.ContentFilter.id, 'name': result.ContentFilter.name, 'words': result.ContentFilter.words, 'active': True if result.UserContentFilter and result.UserContentFilter.active else False})

    return {'list':content_filter_list}

@login_required
@users.route('/userinfo/content_filter/<id_filter>', methods=['GET', 'PUT'])
def get_user_content_filter(id_filter):
    content_filter = db.session.query(ContentFilter, UserContentFilter).filter(
        ContentFilter.id == int(id_filter)
    ).join(UserContentFilter, isouter=True).first()

    if content_filter is None:
        abort(404)

    if content_filter.ContentFilter.private and content_filter.UserContentFilter.id_user!=current_user.id:
        abort(403)

    if request.method == 'PUT':
        active = request.form.get('active')=='true'
        print(active)
        if content_filter.UserContentFilter is None and active:
            new_user_content_filter = UserContentFilter()
            new_user_content_filter.id_content_filter=id_filter
            new_user_content_filter.id_user=current_user.id
            new_user_content_filter.active=True
            db.session.add(new_user_content_filter)
            db.session.commit()
        elif content_filter.UserContentFilter is not None:
            content_filter.UserContentFilter.active=active
            db.session.commit()

    return {'id': content_filter.ContentFilter.id, 'name': content_filter.ContentFilter.name, 'words': content_filter.ContentFilter.words, 'active': True if content_filter.UserContentFilter and content_filter.UserContentFilter.active else False}



@login_required
@users.route('/blacklist/add', methods=['GET', 'POST'])
def add_user_to_blacklist():
    if request.method == 'POST':
        blacklist = Blacklist()
        blacklist.id_user = current_user.id
        email = request.form.get('email')
        blacklist.id_blacklisted = db.session.query(User.id).filter(User.email == email)
        db.session.add(blacklist)
        db.session.commit()
        return redirect('/blacklist')
    else:
        blacklist = db.session.query(User.id).join(Blacklist, Blacklist.id_blacklisted == User.id).filter(
            Blacklist.id_user == current_user.id)
        users = db.session.query(User).filter(User.email != current_user.email).filter(User.id.not_in(blacklist))
        return render_template('add_to_blacklist.html', users=users)


@login_required
@users.route('/blacklist', methods=['GET'])
def get_blacklist():
    blacklist = db.session.query(Blacklist, User).filter(
        Blacklist.id_blacklisted == User.id).filter(
            Blacklist.id_user == current_user.id).all()
    return render_template('blacklist.html', blacklist=blacklist)


@login_required
@users.route('/blacklist/remove', methods=['GET', 'POST'])
def remove_user_from_blacklist():
    if request.method == 'POST':
        email = request.form["email"]
        id_blklst = db.session.query(User.id).filter(User.email == email).all()
        db.session.query(Blacklist).filter(Blacklist.id_blacklisted == id_blklst[0].id).delete()
        db.session.commit()
        return redirect('/blacklist')
    else:
        blacklist = db.session.query(Blacklist, User).filter(
            Blacklist.id_blacklisted == User.id).filter(
                Blacklist.id_user == current_user.id).all()
        return render_template('blacklist.html', blacklist=blacklist)
