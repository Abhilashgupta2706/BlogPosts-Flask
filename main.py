from pyexpat import native_encoding
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask import Flask, redirect, render_template, flash, request, template_rendered, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
from datetime import datetime
from decouple import config
import uuid as uuid
import os

from wtform import LoginForm, UserForm, BlogPostsForm, NamerForm, PasswordForm, SearchForm

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = 'my secret key'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{config("user")}:{config("passwrd")}@{config("host")}/brcahktpjiq5j4y7htq0'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/images/'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html')

    else:
        flash('Restricted Access to Admin ONLY')
        return redirect(url_for('dashboard'))


# Pass things to Extended Files
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = BlogPosts.query
    if form.validate_on_submit():
        post_search = form.search.data

        posts = posts.filter(BlogPosts.content.like('%' + post_search + '%'))
        posts = posts.order_by(BlogPosts.title).all()
        return render_template('search.html', form=form, search=post_search, posts=posts)


@app.route('/user/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = Users.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password_hash, password):
                login_user(user)
                flash(f'Welcome {username} .')
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password! Try again...')
        else:
            flash('Username does not exist! Check again...')

    return render_template('login.html', form=form)


@app.route('/user/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/user/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.about_user = request.form['about_user']

        if request.files['user_profile_pic']:
            name_to_update.user_profile_pic = request.files['user_profile_pic']

            profile_pic_filename = secure_filename(
                name_to_update.user_profile_pic.filename)
            generate_profile_pic_name = str(
                uuid.uuid1()) + "_" + profile_pic_filename

            saver = request.files['user_profile_pic']

            saver.save(os.path.join(
                app.config["UPLOAD_FOLDER"], generate_profile_pic_name))

            name_to_update.user_profile_pic = generate_profile_pic_name

            try:
                db.session.commit()

                flash("User updated successfully.")
                return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)

            except:
                flash("Error! Try Again...")
                return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
        else:
            db.session.commit()
            flash("User updated successfully.")
            return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)

    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)


@app.route('/user/add', methods=["GET", "POST"])
def add_user():
    form = UserForm()
    name, email = None, None
    if form.validate_on_submit():
        name, username, email, favorite_color, password_hash = form.name.data, form.username.data, form.email.data, form.favorite_color.data, form.password_hash.data
        new_user = Users.query.filter_by(email=email).first()

        if new_user is None:
            hash_pw = generate_password_hash(password_hash, 'sha256')

            new_user = Users(name=name, username=username, email=email,
                             favorite_color=favorite_color, password_hash=hash_pw)
            db.session.add(new_user)
            db.session.commit()

        form.name.data, form.username.data, form.email.data, form.favorite_color.data, form.password_hash.data = '', '', '', '', ''
        flash("User added successfully.")

    our_users = Users.query.order_by(Users.dateTime)

    return render_template('add_user.html', form=form, name=name, our_users=our_users)


@app.route('/update/<int:id>', methods=["GET", "POST"])
@login_required
def update_user(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        name_to_update.favorite_color = request.form['favorite_color']

        try:
            db.session.commit()
            flash("User updated successfully.")
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

        except:
            flash("Error! Try Again...")
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)


@app.route('/delete/<int:id>', methods=["GET", "POST"])
@login_required
def delete_user(id):
    if id == current_user.id:
        user_to_delete = Users.query.get_or_404(id)

        try:
            db.session.delete(user_to_delete)
            db.session.commit()

            form = UserForm()
            name, email = None, None
            our_users = Users.query.order_by(Users.dateTime)

            flash("User deleted successfully.")
            return render_template('add_user.html', form=form, name=name, our_users=our_users)

        except:
            flash("Error while deleting user! Try again..")
            return render_template('add_user.html', form=form, name=name, our_users=our_users)
    else:
        flash("Access Denied! Cannot delete other User's Profile")
        return redirect(url_for('dashboard'))


@app.route('/blog-posts')
def blog_posts():
    posts = BlogPosts.query.order_by(BlogPosts.date_posted)
    return render_template('blog_posts.html', posts=posts)


@app.route('/blog-posts/<int:id>')
@login_required
def blog_posts_id(id):
    post = BlogPosts.query.get_or_404(id)

    return render_template('post.html', post=post)


@app.route('/add-posts', methods=["GET", "POST"])
@login_required
def add_posts():
    form = BlogPostsForm()

    if form.validate_on_submit():
        poster = current_user.id
        title,  slug, content = form.title.data,  form.slug.data, form.content.data
        # author = form.author.data

        post = BlogPosts(title=title, poster_id=poster,
                         slug=slug, content=content)
        form.title.data,  form.slug.data, form.content.data = '', '', ''

        db.session.add(post)
        db.session.commit()

        flash('Blog post submitted successfully.')

    return render_template('add_post.html', form=form)


@app.route('/blog-posts/update/<int:id>', methods=["GET", "POST"])
@login_required
def blog_post_update(id):
    post_to_update = BlogPosts.query.get_or_404(id)
    form = BlogPostsForm()

    if form.validate_on_submit():

        post_to_update.title = form.title.data
        # post_to_update.author = form.author.data
        post_to_update.slug = form.slug.data
        post_to_update.content = form.content.data

        db.session.add(post_to_update)
        db.session.commit()
        flash("Blog has been updated.")
        return redirect(url_for('blog_posts_id', id=post_to_update.id))

    if current_user.id == post_to_update.poster_id or current_user.id  == 1:

        form.title.data = post_to_update.title
        # form.author.data = post_to_update.author
        form.slug.data = post_to_update.slug
        form.content.data = post_to_update.content
        return render_template('update_post.html', form=form)

    else:
        flash('Access Denied! You are not authorized to edit this Blog Post')
        posts = BlogPosts.query.order_by(BlogPosts.date_posted)
        return render_template('blog_posts.html', posts=posts)


@app.route('/blog_posts/delete/<int:id>', methods=["GET", "POST"])
@login_required
def delete_bog_post(id):
    post_to_delete = BlogPosts.query.get_or_404(id)

    id = current_user.id

    if id == post_to_delete.poster.id or id == 1:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            posts = BlogPosts.query.order_by(BlogPosts.date_posted)

            flash("Blog deleted successfully.")
            return render_template('blog_posts.html', posts=posts)

        except:
            flash("Error while deleting blog! Try again..")
            return render_template('blog_posts.html', posts=posts)

    else:
        posts = BlogPosts.query.order_by(BlogPosts.date_posted)
        flash("Access Denied! Cannot delete other user's Blog Posts.")
        return render_template('blog_posts.html', posts=posts)


@app.route('/name', methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()

    # Validation
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form submitted successfully.")

    return render_template('name.html', name=name, form=form)


@app.errorhandler(404)
def Invalid_URL(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('505.html'), 404


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100))
    about_user = db.Column(db.Text(300), nullable=True)
    user_profile_pic = db.Column(db.Text, nullable=True)
    dateTime = db.Column(db.DateTime, default=datetime.utcnow)

    password_hash = db.Column(db.String(128))

    user_posts = db.relationship("BlogPosts", backref='poster')

    @property
    def password(self):
        raise AttributeError('Password is not a readable Attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'{self.name} -> {self.email} '


class BlogPosts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    # author = db.Column(db.String(255))
    slug = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


if __name__ == '__main__':
    app.run(debug=True)
