from flask import render_template, make_response
from . import main


@main.route('/')
def hello_world():
    return render_template('index.html')


@main.route('/init')
def init():
    return render_template('index.html')


# @main.route('/delete')
# def delete():
#     orm.delete()
#     return render_template('index.html')


@main.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@main.route('/user/<name>/<int:age>')
def user_age(name, age):
    """
    :param name: the name of the user, second item in URL
    :param age: the age of the user, third item in URL
    :returns: an instance of Response object containing a coockie and a greeting text
    """

    response = make_response(f'<h1>{name} is {age} years old!<h1/>')
    response.set_cookie('greetings', 'fuck off')

    return response
