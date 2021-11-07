from flask import Blueprint, redirect, render_template, request, abort
from flask_login.utils import login_required
from monolith.database import User, Blacklist, Reports, ContentFilter, UserContentFilter, db
from monolith.forms import UserForm
from flask_login import current_user
import datetime

NUM_REPORTS = 2


users = Blueprint('users', __name__)


@users.route('/users')
def _users():
    _users = db.session.query(User).filter(User.is_active.is_(True))
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
            result = db.session.query(User).filter(User.email == new_user.email, User.is_active.is_(True)).all()
            reported_user = db.session.query(User).filter(
                User.email == new_user.email,
                User.firstname == new_user.firstname,
                User.lastname == new_user.lastname,
                User.date_of_birth == new_user.date_of_birth,
                User.is_reported.is_(True)).first()
            
            if result:
                return render_template("create_user.html", emailError=True, form=form)
            elif reported_user:
                return render_template('create_user.html', form=form, is_reported=True)
            
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
            
    elif request.method == 'GET':
        return render_template('create_user.html', form=form)


@login_required
@users.route('/delete_user')
def delete_user():
    User.query.filter_by(id=current_user.id).update({"is_active":False})
    db.session.commit()
    return redirect('/')


@login_required
@users.route('/userinfo', methods=["GET", "POST"])
def get_user_info():
    if request.method == "GET":
        user = db.session.query(User).filter(current_user.id == User.id).first()
        return render_template('user_info.html', user=user)
    if request.method == "POST":
        new_email = request.form["email"]
        checkEmail = db.session.query(User).filter(User.email == new_email).all()
        new_firstname = request.form["firstname"]
        new_lastname = request.form["lastname"]
        new_date_of_birth = datetime.strptime(request.form["date_of_birth"], '%Y-%m-%d').date()
        new_password = request.form["password"]
        user_dict = dict(email=new_email, firstname=new_firstname, lastname=new_lastname,
                         date_of_birth=new_date_of_birth)
        if checkEmail:
            return render_template('user_info.html', emailError=True, user=user_dict)
        user = db.session.query(User).filter(current_user.id == User.id)
        if new_password != "":
            user.first().set_password(new_password)
        user.update(user_dict)
        db.session.commit()
        return render_template('user_info.html', user=user_dict)


@ login_required
@ users.route('/userinfo/content_filter')
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
        content_filter_list.append({'id': result.ContentFilter.id,
                                    'name': result.ContentFilter.name,
                                    'words': result.ContentFilter.words,
                                   'active': True if result.UserContentFilter and
                                    result.UserContentFilter.active else False})

    return {'list': content_filter_list}


@ login_required
@ users.route('/userinfo/content_filter/<id_filter>', methods=['GET', 'PUT'])
def get_user_content_filter(id_filter):
    content_filter = db.session.query(ContentFilter, UserContentFilter).filter(
        ContentFilter.id == int(id_filter)
    ).join(UserContentFilter, isouter=True).first()

    if content_filter is None:
        abort(404)

    if content_filter.ContentFilter.private and content_filter.UserContentFilter.id_user != current_user.id:
        abort(403)

    if request.method == 'PUT':
        active = request.form.get('active') == 'true'
        print(active)
        if content_filter.UserContentFilter is None and active:
            new_user_content_filter = UserContentFilter()
            new_user_content_filter.id_content_filter = id_filter
            new_user_content_filter.id_user = current_user.id
            new_user_content_filter.active = True
            db.session.add(new_user_content_filter)
            db.session.commit()
        elif content_filter.UserContentFilter is not None:
            content_filter.UserContentFilter.active = active
            db.session.commit()

    return {'id': content_filter.ContentFilter.id,
            'name': content_filter.ContentFilter.name,
            'words': content_filter.ContentFilter.words,
            'active': True if content_filter.UserContentFilter and
            content_filter.UserContentFilter.active else False}


@ login_required
@ users.route('/blacklist/add', methods=['GET', 'POST'])
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


@login_required
@users.route('/report', methods=['GET'])
def get_report():
    report = db.session.query(Reports, User).filter(
        Reports.id_reported == User.id).filter(
            Reports.id_user == current_user.id).all()
    return render_template('report.html', report=report)


@login_required
@users.route('/report/add', methods=['GET', 'POST'])
def report_user():
    if request.method == 'POST':
        report = Reports()
        report.id_user = current_user.id
        email = request.form.get('email')
        report.id_reported = db.session.query(User.id).filter(User.email == email)
        db.session.add(report)
        db.session.commit()

        num_reports = db.session.query(Reports).filter(Reports.id_reported == report.id_reported).all()
        print(len(num_reports))
        if len(num_reports) == NUM_REPORTS:
            print('dentro if')
            user = db.session.query(Reports, User).filter(report.id_reported == User.id).first()
            print(user)
            user.User.is_reported = True
            db.session.commit()

        return redirect('/report')
    else:
        report = db.session.query(User.id).join(Reports, Reports.id_reported == User.id).filter(
            Reports.id_user == current_user.id)
        users = db.session.query(User).filter(User.email != current_user.email).filter(User.id.not_in(report)).filter(
            User.is_reported == False)
        return render_template('report_user.html', users=users)
