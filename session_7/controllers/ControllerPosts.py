import flask, os
from loguru import logger
from flask import request, redirect, url_for, current_app, send_from_directory, session, flash

from controllers.ControllerDatabase import ControllerDatabase
from models.ModelPost import ModelPost
from utils.FileService import upload_file


class ControllerPosts: #flask middleware
    blueprint = flask.Blueprint("posts", __name__, url_prefix="/posts")

    @staticmethod
    @logger.catch(reraise=True)
    @blueprint.route("/new", methods=["POST", "GET"])
    @blueprint.route("/edit/<post_id>", methods=["POST", "GET"])
    def post_edit(post_id=None):
        post = ModelPost()

        current_session = session.get('session_token')
        if not current_session:
            flash("Please login first")
            return redirect('/')

        logger.log("DEBUG", "Post ID: " + str(post_id))

        if post_id:
            post_id = int(post_id)
            if post_id > 0:
                post = ControllerDatabase.get_post(post_id=post_id)

        posts_flattened = ControllerDatabase.get_all_posts_flattened(exclude_branch_post_id=post_id)
        post_parent_id_and_title = [
            (None, "No parent")
        ]

        file_models = []
        if request.method == "POST":
            button_type = request.form.get("button_type")

            if button_type == "delete":
                if ControllerDatabase.delete_post(post_id):
                    flash("Post deleted")
                else:
                    flash("Post failed to delete")
                return redirect('/')

            post.title = request.form.get('post_title').strip()
            post.body = request.form.get('post_body').strip()
            post.url_slug = request.form.get('url_slug').strip()
            post.tags = request.form.get('tags').strip()

            if post.url_slug == "" or post.url_slug is None:  # temporary fix
                post.url_slug = post.title

            current_session = session.get('session_token')
            print(current_session)

            if post.title == "":
                flash("Post title is required")
                return redirect(url_for('home'))

            files = request.files.getlist("files")
            files = [f for f in files if f.filename]

            if files:
                file_models = upload_file(files) # if files else []
                logger.log("CRITICAL","files!!!")

            if post.post_id is not None:
                if ControllerDatabase.update_post(post, current_session, file_models):
                    flash(f"Post edited= {post.url_slug}")
                    return redirect(url_for('home'))
                else:
                    flash(f"Error happened= {post.url_slug}")
                    return redirect(url_for('home'))
            else:
                post_id = ControllerDatabase.insert_post(post, current_session, file_models)
                return redirect(url_for('posts.post_view', post_id=post_id, url_slug=post.url_slug))


        return flask.render_template(
            'posts/edit.html',
            post=post,
            post_parent_id_and_title=post_parent_id_and_title
        )

    @logger.catch(reraise=True)
    @blueprint.route('/download/<int:file_id>', methods=['GET'])
    def download_file(file_id):
        path = ControllerDatabase.get_file(file_id)
        uploads = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
        if path:
            path = os.path.basename(path)
            return send_from_directory(uploads, path, as_attachment=True)
        else:
            logger.log("WARNING", f"File id not found: {file_id}")
            flash("Error happened while downloading file")
            return redirect(url_for('home'))

    @staticmethod
    @logger.catch(reraise=True)
    @blueprint.route("/view/<int:post_id>/<url_slug>", methods=["GET"])
    def post_view(post_id, url_slug):
        post = ControllerDatabase.get_post(post_id=post_id)
        return flask.render_template(
            'posts/view.html',
            post=post
        )