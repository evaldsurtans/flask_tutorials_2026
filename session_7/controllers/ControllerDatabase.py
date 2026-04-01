from flask import session

from models.ModelPost import ModelPost
import sqlite3, secrets

from models.ModelUsers import ModelUser
from utils.UtilDatabaseCursor import UtilDatabaseCursor


class ControllerDatabase:

    @staticmethod
    def __connection():
        return sqlite3.connect("./blog.sqlite")

    @staticmethod
    def insert_post(post: ModelPost) -> int:
        post_id = 0
        try:
            current_session = session.get('session_token')

            if current_session:
                with ControllerDatabase.__connection() as conn:
                    cursor = conn.cursor()
                    user = cursor.execute("SELECT * FROM users WHERE session_token = :session_token LIMIT 1",
                                          {'session_token': current_session}).fetchone()
                    if user:
                        post.owner_uuid = user[0] #is copying to modelUser mandatory?
                        cursor.execute(
                            "INSERT INTO posts (title, body, url_slug, parent_post_id, tags, files, owner_uuid) "
                            "VALUES (:title, :body, :url_slug, :parent_post_id, :tags, :files, :owner_uuid);",
                            post.__dict__
                        )
                        post_id = cursor.execute("SELECT last_insert_rowid()").fetchone()[0] #ka man sutit errorus atpakal
                    cursor.close()
        except Exception as exc:
            print(exc)
        return post_id

    @staticmethod
    def update_post(post: ModelPost):
        try:
            current_session = session.get('session_token')
            print(current_session)
            if current_session:
                with ControllerDatabase.__connection() as conn:
                    cursor = conn.cursor()
                    user = cursor.execute("SELECT * FROM users WHERE session_token = :session_token LIMIT 1",
                                         {'session_token': current_session}).fetchone()

                    if user[0] == post.owner_uuid:
                        cursor.execute(
                            "UPDATE posts SET (title, body, url_slug, parent_post_id, tags, files) = "
                            "(:title, :body, :url_slug, :parent_post_id, :tags, :files) WHERE post_id = :post_id",
                            post.__dict__

                        )
                        cursor.close()

        except Exception as exc:
            print(exc)

    @staticmethod
    def get_post(post_id: int = None, url_slug: str = None) -> ModelPost:
        post = None
        try:
            with ControllerDatabase.__connection() as conn:
                cursor = conn.cursor()
                if post_id:
                    query = cursor.execute(
                        "SELECT * FROM posts WHERE post_id = :post_id LIMIT 1;",
                        {'post_id': post_id}
                    )
                else:
                    query = cursor.execute(
                        "SELECT * FROM posts WHERE url_slug = :url_slug LIMIT 1;",
                        {'url_slug': url_slug}
                    )

                col = query.fetchone() # tuple of all * col values
                if col is not None: # rowcount is only meant for INSERT, UPDATE, DELETE
                    post = ModelPost() # instance of object

                    (
                        post.post_id,
                        post.title,
                        post.body,
                        post.created,
                        post.modified,
                        post.url_slug,
                        post.thumbnail_uuid,
                        post.status,
                        post.parent_post_id,
                        post.tags,
                        post.files,
                        post.owner_uuid
                        # post.parent_post,
                        # post.children_posts
                    ) = col # pythonic wat to copy one by one variable from one tuple to another tuple
                cursor.close()

                if post.files:
                    post.files = post.files.split(",") #idk how to ignore this error

                if post.parent_post_id:
                    post.parent_post = ControllerDatabase.get_post(post_id=post.parent_post_id)

                # post.children_posts = ControllerDatabase.get_all_posts(parent_post_id=post.post_id)

        except Exception as exc:
            print(exc)
        return post

    @staticmethod
    def delete_post(post_id: int) -> bool:
        is_success = False
        try:
            with ControllerDatabase.__connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM posts WHERE post_id = ?;",
                    [post_id]
                )
                is_success = True
        except Exception as exc:
            print(exc)
        return is_success

    @staticmethod
    def get_all_posts(parent_post_id=None):
        posts = []
        try:
            with UtilDatabaseCursor() as cursor:
                cursor.execute(
                    f"SELECT post_id FROM posts WHERE parent_post_id {'=' if parent_post_id else 'IS'} ?",
                    [parent_post_id]
                )
                for post_id, in cursor.fetchall():
                    post = ControllerDatabase.get_post(post_id=post_id)
                    posts.append(post)
        except Exception as exc:
            print(exc)
        return posts

    @staticmethod
    def get_all_posts_flattened(parent_post_id=None, exclude_branch_post_id=None):
        posts_flattened = []
        try:
            post_hierarchy = ControllerDatabase.get_all_posts(parent_post_id)
            posts_flattened = post_hierarchy

        except Exception as exc:
            print(exc)
        return posts_flattened

    @staticmethod
    def login(auth: ModelUser):
        is_success: bool = False

        try:
            with UtilDatabaseCursor() as cursor:
                col = cursor.execute("SELECT * FROM users WHERE username = :username LIMIT 1", {'username': auth.username}).fetchone()
                if col:
                    user = ModelUser()
                    (user.uuid,
                     user.username,
                     user.password,
                     user.session_token) = col
                    if user.password == auth.password:
                        session.clear()
                        session['session_token'] = secrets.token_urlsafe(16)
                        user.session_token = session.get('session_token')
                        cursor.execute("UPDATE users SET session_token = :session_token WHERE uuid = :uuid",
                                       {'session_token': user.session_token, 'uuid': user.uuid})

                        is_success = True
            cursor.close()

        except Exception as exc:
            print(exc)
        return is_success


