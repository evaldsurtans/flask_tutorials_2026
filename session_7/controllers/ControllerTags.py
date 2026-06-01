from functools import wraps
import flask
from asgiref import current_thread_executor
from flask import request, flash, redirect, url_for, session
from loguru import logger

from controllers.ControllerDatabase import ControllerDatabase

def session_required(f): #fix duplicate in future
    @wraps(f)
    def wrapper(*args, **kwargs): # args passed variables, kwargs extra variables
        current_session = session.get('session_token')
        if not ControllerDatabase.verify_session(current_session):
            flash("Please login first")
            return redirect('/')

        kwargs['current_session'] = current_session
        return f(*args, **kwargs)
    return wrapper

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

    @staticmethod
    @logger.catch(reraise=True)
    @blueprint.route('/edit/<tag_id>', methods=['GET', 'POST'])
    @session_required
    def edit_tags(current_session,tag_id):
        tag = ControllerDatabase.get_tag(tag_id)
        logger.error(current_session)

        if request.method == "POST":
            button_type = request.form.get("button_type")
            if button_type == "delete":
                if ControllerDatabase.delete_tag(tag=tag, current_session=current_session):
                    flash("Post deleted")
                else:
                    flash("Post failed to delete")
                return redirect(url_for('tags.view_tags'))
            tag.tag_name = request.form.get("tag_title").strip()

            if tag.tag_name is not "":
                if ControllerDatabase.edit_tag(tag=tag, current_session=current_session):
                    flash(f"Tag edited= {tag.tag_name}")
                    return redirect(url_for('tags.view_tags'))
                else:
                    flash(f"Error happened= {tag.tag_name}")
                    return redirect(url_for('tags.view_tags'))

        if tag:
            return flask.render_template("tags/edit.html", tag=tag)
        else:
            logger.log("WARNING", f"Tag id not found: {tag_id}")
            flash("Tag not found")
            return redirect(url_for('tags.view_tags'))
