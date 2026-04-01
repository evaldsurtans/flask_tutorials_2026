import functools
import flask, os
from flask import request, redirect, url_for, current_app, send_from_directory
from werkzeug.utils import secure_filename

from controllers.ControllerDatabase import ControllerDatabase
from models.ModelPost import ModelPost
from utils.AllowedFileName import AllowedFileName
from utils.UniqueFileName import UniqueFileName


class ControllerPosts:
    blueprint = flask.Blueprint("posts", __name__, url_prefix="/posts")

    @staticmethod
    @blueprint.route("/new", methods=["POST", "GET"])
    @blueprint.route("/edit/<post_id>", methods=["POST", "GET"])
    def post_edit(post_id=None):
        try:
            post = ModelPost()
            if post_id:
                post_id = int(post_id)
                if post_id > 0:
                    post = ControllerDatabase.get_post(post_id)

            posts_flattened = ControllerDatabase.get_all_posts_flattened(exclude_branch_post_id=post_id)
            post_parent_id_and_title = [
                (None, "No parent")
            ]

            if request.method == "POST":
                button_type = request.form.get("button_type")
                if button_type == "delete":
                    ControllerDatabase.delete_post(post_id)
                    return redirect('/?deleted=1')

                post.title = request.form.get('post_title').strip()
                post.body = request.form.get('post_body').strip()
                post.url_slug = request.form.get('url_slug').strip()
                post.tags = request.form.get('tags').strip()

                if request.files.get('file'):
                    file = request.files['file']
                    if file and not file.filename == '' and AllowedFileName(file.filename):
                        filename = secure_filename(file.filename)
                        ufilename = UniqueFileName(filename)
                        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], ufilename.filename))
                        existing = post.files or ""
                        post.files = (existing + "," + ufilename.filename).lstrip(",")
                        print(post.files)

                print(post)
                if post.post_id > 0:
                    ControllerDatabase.update_post(post)
                    return redirect(f"/?edited={post.url_slug}")
                else:
                    post_id = ControllerDatabase.insert_post(post)

                return redirect(url_for('posts.post_view', url_slug=post.url_slug))


            return flask.render_template(
                'posts/edit.html',
                post=post,
                post_parent_id_and_title=post_parent_id_and_title
            )
        except Exception as exc:
            print(exc)

    @blueprint.route('/download/<filename>')
    def download_file(filename):
        uploads = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
        return send_from_directory(uploads, filename)

    @staticmethod
    @blueprint.route("/view/<url_slug>", methods=["GET"])
    def post_view(url_slug):
        post = ControllerDatabase.get_post(url_slug=url_slug)
        return flask.render_template(
            'posts/view.html',
            post=post
        )