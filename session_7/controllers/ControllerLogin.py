import flask
from flask import request, redirect, session, flash
from loguru import logger

from controllers.ControllerDatabase import ControllerDatabase
from models.ModelUsers import ModelUser

class ControllerLogin:
    blueprint = flask.Blueprint('auth', __name__, url_prefix='/')

    @staticmethod
    @logger.catch(reraise=True)
    @blueprint.route("/login", methods=["POST", "GET"])
    @blueprint.route("/register", methods=["POST", "GET"])
    def login():
        try:
            auth = ModelUser()
            if request.method == 'POST':
                auth.username = request.form.get('username')
                auth.password = request.form.get('password')

                if auth.username and auth.password:
                    token = ControllerDatabase.login(auth)
                    if token:
                        #session.clear() -- vai nepieciesams?
                        session['session_token'] = token
                        flash('Successfully logged in')
                        return redirect('/')

                flash('Invalid username or password')

        except Exception as exc:
            print(exc)

        return flask.render_template(
            'auth/login.html'
        )

    @staticmethod
    @logger.catch(reraise=True)
    @blueprint.route("/logout", methods=["POST"]) #redirect
    def logout():
        token = session.get('session_token')
        session.clear()

        if not ControllerDatabase.logout(token):
            logger.log("WARNING", "Logout failed due to invalid token")
            return redirect('/')
        flash('Successfully logged out')

        return redirect('/') #flask flash messages