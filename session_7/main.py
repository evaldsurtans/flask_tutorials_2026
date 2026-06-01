import flask, logging, sys
from loguru import logger

from models.Database import Base, db
from models.ModelUsers import ModelUser
from models.ModelPost import ModelPost # init for safety measures I guess
from models.ModelSession import ModelSession
from models.ModelFile import ModelFile
from models.ModelTags import ModelTags
from models.ModelTagsInPost import ModelTagsInPost

from controllers.ControllerTags import ControllerTags
from controllers.ControllerDatabase import ControllerDatabase
from controllers.ControllerPosts import ControllerPosts
from controllers.ControllerAuth import ControllerLogin
app = flask.Flask(__name__, template_folder='views')
app.register_blueprint(ControllerPosts.blueprint)
app.register_blueprint(ControllerLogin.blueprint)
app.register_blueprint(ControllerTags.blueprint)

app.secret_key = 'e6245cf83a39d4632edcaab284334f4fd6b73abccb1e4b8acf24a20eef3ad651' #atslega sha256
app.config["UPLOAD_FOLDER"] = "Uploads"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_ENGINES'] = {"default": 'sqlite:///blog.sqlite'}

db.init_app(app)

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

werkzeug_logger = logging.getLogger("werkzeug") #flaskam nak lidz werkzeug handler ari
werkzeug_logger.handlers = [InterceptHandler()]
werkzeug_logger.propagate = False #avoid dublikati

logger.remove()
logger.add(sys.stdout, level="DEBUG", colorize=True)

with app.app_context():
    Base.metadata.create_all(db.engine)

@logger.catch(reraise=True)
@app.route("/", methods=['GET'])
def home():
    posts = ControllerDatabase.get_all_posts()

    return flask.render_template(
        'home.html',
        posts=posts
    )

app.run( #hello
    host='localhost', # localhost == 127.0.0.1
    port=8000, # by default HTTP 80, HTTPS 443 // 8000, 8080
    debug=True,
    use_reloader=True
)