from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


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
