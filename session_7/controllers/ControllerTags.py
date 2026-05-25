import flask
from flask import request, jsonify
from loguru import logger

from controllers.ControllerDatabase import ControllerDatabase


class ControllerTags:
    blueprint = flask.Blueprint('tags', __name__, url_prefix='/tags')

    @staticmethod
    @logger.catch(reraise=True)
    @blueprint.route('/', methods=['GET'])
    def view_tags():
        tags = ControllerDatabase.get_all_tags()
        return flask.render_template("tags/tags.html", tags=tags)

    @staticmethod
    @logger.catch(reraise=True)
    @blueprint.route('/search', methods=['GET'])
    def search_tags(query_filter : str = None, query_tab : str = None):
        query_filter = request.args.get('filter')
        tags = ControllerDatabase.get_all_tags(query_filter, query_tab)
        return flask.render_template("tags/tag_cards.html", tags=tags)