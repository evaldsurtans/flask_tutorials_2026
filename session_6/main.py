import flask
from flask import url_for

from controllers.ControllerDatabase import ControllerDatabase
from controllers.ControllerPosts import ControllerPosts

app = flask.Flask(__name__, template_folder='views')
app.register_blueprint(ControllerPosts.blueprint)



@app.route("/", methods=['GET'])
def home():
    params_GET = flask.request.args
    message = ""
    posts = ControllerDatabase.get_all_posts()
    if params_GET.get("deleted"):
        message = "Post deleted"
    if params_GET.get("edited"):
        message = "Post edited"

    return flask.render_template(
        'home_div.html',
        message=message,
        posts=posts
    )

app.run(
    host='localhost', # localhost == 127.0.0.1
    port=8000, # by default HTTP 80, HTTPS 443 // 8000, 8080
    debug=True
)
