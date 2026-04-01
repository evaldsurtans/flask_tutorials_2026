import flask
from flask import url_for

from controllers.ControllerDatabase import ControllerDatabase
from controllers.ControllerPosts import ControllerPosts
from controllers.ControllerLogin import ControllerLogin

app = flask.Flask(__name__, template_folder='views')
app.register_blueprint(ControllerPosts.blueprint)
app.register_blueprint(ControllerLogin.blueprint)

app.secret_key = 'e6245cf83a39d4632edcaab284334f4fd6b73abccb1e4b8acf24a20eef3ad651' #atslega sha256
app.config["UPLOAD_FOLDER"] = "Uploads"
app.config['SESSION_TYPE'] = 'filesystem'
# comment

@app.route("/", methods=['GET'])
def home():
    params_GET = flask.request.args
    message = ""
    posts = ControllerDatabase.get_all_posts()
    if params_GET.get("deleted"):
        message = "Post deleted"
    if params_GET.get("edited"):
        message = "Post edited"
    if params_GET.get("login"):
        message = "Successfully login!"

    return flask.render_template(
        'home.html',
        message=message,
        posts=posts
    )

app.run( #hello
    host='localhost', # localhost == 127.0.0.1
    port=8000, # by default HTTP 80, HTTPS 443 // 8000, 8080
    debug=True
)
