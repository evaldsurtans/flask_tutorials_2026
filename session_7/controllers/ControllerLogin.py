import flask
from flask import request, redirect, session, flash

from controllers.ControllerDatabase import ControllerDatabase
from models.ModelUsers import ModelUser

class ControllerLogin:
    blueprint = flask.Blueprint('auth', __name__, url_prefix='/')

    @staticmethod
    @blueprint.route("/login", methods=["POST", "GET"])
    @blueprint.route("/register", methods=["POST", "GET"])
    def login():
        try:
            auth = ModelUser()
            if request.method == 'POST':
                auth.username = request.form.get('username')
                auth.password = request.form.get('password')

                if auth.username and auth.password:
                    if ControllerDatabase.login(auth):
                        return redirect('/?login=1')


        except Exception as exc:
            print(exc)

        return flask.render_template(
            'auth/login.html'
        )

    @staticmethod
    @blueprint.route("/logout", methods=["POST"]) #redirect
    def logout():
        try:
            token = session.get('session_token')

            if not ControllerDatabase.logout(token):
                print("devops help me")
            session.clear()
            flash('Successfully logged out')

        except Exception as exc:
            print(exc)

        return redirect('/') #flask flash messages