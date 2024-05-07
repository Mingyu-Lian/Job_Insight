

import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_user, current_user,logout_user
from .forms import LoginForm, SignUpForm,UploadForm, IconForm, ProfileForm
from .models import db, User,UserDetails,Post



main = Blueprint('main', __name__)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.home'))
    return render_template('login.html', title='Sign In', form=form)


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('The email is already registered')
            return redirect(url_for('main.signup'))
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.flush()

        new_user_details = UserDetails(id=new_user.id)
        db.session.add(new_user_details)

        db.session.commit()
        flash('Successfully registered!')
        return redirect(url_for('main.login'))
    return render_template('signup.html', title='Sign Up', form=form)


@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))


@main.route('/')
@main.route('/home')
def home():
    filter_type = request.args.get('filter', 'all')

    if filter_type == 'following':
        if not current_user.is_authenticated:
            return redirect(url_for('main.login'))
        followed_users = [followed.id for followed in current_user.followed]
        posts = Post.query.filter(Post.author_id.in_(followed_users)).order_by(Post.created_at.desc()).all()
    else:
        posts = Post.query.order_by(Post.created_at.desc()).all()

    return render_template('home.html', title='Home', posts=posts, filter=filter_type)


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    user_profile = UserDetails.query.filter_by(id=current_user.id).first()
    if not user_profile:
        flash('User not found and please inform this error to dev.', 'error')
        return redirect(url_for('main.home'))
    return render_template('profile.html', user_profile=user_profile)


@main.route('/profile/set_profile', methods=['GET', 'POST'])
def set_profile():
    form = ProfileForm()
    user_profile = UserDetails.query.filter_by(id=current_user.id).first()
    if form.validate_on_submit():
        if user_profile:
            user_profile.address = form.address.data
            user_profile.company = form.company.data
            user_profile.city = form.city.data
            user_profile.country = form.country.data
            user_profile.phone = form.phone.data
            user_profile.job_title = form.job_title.data
            user_profile.job_description = form.job_description.data
            user_profile.education_level = form.education_level.data
            user_profile.academic_institution = form.academic_institution.data
        else:
            flash('Got problems processing the data, please inform the web dev')
            return redirect(url_for('main.profile'))
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    return render_template('set_profile.html', title='Profile', form=form, user_profile=user_profile)


@main.route('/profile/set_icon', methods=['GET', 'POST'])
def set_icon():
    form = IconForm()
    user_profile = UserDetails.query.filter_by(id=current_user.id).first()
    if form.validate_on_submit():
        if user_profile:
            file = form.img.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], file_path))
            user_profile.img = file_path
            db.session.commit()
            flash('Icon updated successfully!', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('User profile not found.', 'error')
            return redirect(url_for('main.profile'))

    return render_template('set_icon.html', title='Profile', form=form, user_profile=user_profile)



@main.route('/upload/product', methods=['GET', 'POST'])
def upload_product():
    form = UploadForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        tag = form.tag.data
        image_file = form.image.data

        if image_file:
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_post = Post(title=title, description=description, tag=tag, image_filename=filename)
            db.session.add(new_post)
            db.session.commit()

            flash('Post uploaded successfully!', 'success')
            return redirect(url_for('main.home'))

    return render_template('upload.html', title='Upload Post', form=form)



@main.route('/post')
def post():
    return render_template('home.html', title='Post')


@main.route('/channel')
def channel():
    return render_template('channel.html', title='Channel')


@main.route('/search')
def search():
    return render_template('search.html', title='Search')

