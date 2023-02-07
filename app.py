from flask import Flask, make_response, redirect, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/user/<name>/<int:age>')
def user_age(name, age):
    """
    :param name: the name of the user, second item in URL
    :param age: the age of the user, third item in URL
    :returns: an instance of Response object containing a coockie and a greeting text
    """

    response = make_response(f'<h1>{name} is {age} years old!<h1/>')
    response.set_cookie('greetings', 'fuck off')

    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# if __name__ == '__main__':
#     app.run(debug=True)
