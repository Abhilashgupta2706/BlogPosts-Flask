from concurrent.futures import process
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decouple import config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my secret key'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{config("user")}:{config("passwrd")}@{config("host")}/bwe0ewbvmzknevisoqez'
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    dateTime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'{self.Name} -> {self.email} '


# Create a User form
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a form class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/add', methods=["GET", "POST"])
def add_user():
    form = UserForm()
    name, email = None, None
    if form.validate_on_submit():
        name, email = form.name.data, form.email.data
        new_user = Users.query.filter_by(email=email).first()
        if new_user is None:
            new_user = Users(name=name, email=email)
            db.session.add(new_user)
            db.session.commit()

        form.name.data, form.email.data = '', ''
        flash("User added successfully.")

    our_users = Users.query.order_by(Users.dateTime)

    return render_template('add_user.html', form=form, name=name, our_users=our_users)


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


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)


@app.errorhandler(404)
def Invalid_URL(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('505.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
