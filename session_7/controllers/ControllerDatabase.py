from loguru import logger

from models.ModelFile import ModelFile
from models.ModelSession import ModelSession
from models.ModelPost import ModelPost
import sqlite3, secrets, bcrypt
from datetime import datetime, timedelta, timezone
from models.Database import db
from sqlalchemy import select, delete

from models.ModelUsers import ModelUser


class ControllerDatabase:

    @staticmethod
    def insert_post(post: ModelPost, current_session, file_models : list[ModelFile] = None) -> int:
        user_query = select(ModelSession).where(ModelSession.token == current_session)
        user = db.session.scalar(user_query)

        if user:
            post.owner_uuid = user.user_id

            if file_models:
                for file_model in file_models:
                    file_model.owner_id = user.user_id
                    post.files.append(file_model)

        db.session.add(post)
        db.session.commit()
        return post.post_id

    @staticmethod
    def update_post(post: ModelPost, current_session: str = None, file_models : list[ModelFile] = None) -> bool:
        is_success = False

        user_query = select(ModelSession).where(ModelSession.token == current_session)
        user = db.session.scalar(user_query)

        # nested because scalar already started a transaction
        if user and user.user_id == post.owner_uuid:
            if file_models:
                for file_model in file_models:
                    file_model.owner_id = user.user_id
                    post.files.append(file_model)

        db.session.merge(post)
        db.session.commit()
        is_success = True

        return is_success

    @staticmethod
    def get_post(post_id: int = None, url_slug: str = None) -> ModelPost:
        post = None
        if post_id is not None:
            post_query = select(ModelPost).where(ModelPost.post_id == post_id)
        else:
            post_query = select(ModelPost).where(ModelPost.url_slug == url_slug)
        post = db.session.scalar(post_query)

        files_query = select(ModelFile).where(ModelFile.post_id == post.post_id)
        files = db.session.scalars(files_query)

        if post.parent_post_id:
            post.parent_post = ControllerDatabase.get_post(post_id=post.parent_post_id)

        post.children_posts = ControllerDatabase.get_all_posts(parent_post_id=post.post_id)

        return post

    @staticmethod
    def get_file(file_id):
        if not file_id:
            return None

        file_query = select(ModelFile).where(ModelFile.file_id == file_id)
        file: ModelFile = db.session.scalar(file_query)

        if file:
            return file.storage_path

        return None

    @staticmethod
    def delete_post(post_id: int) -> bool:
        is_success = False
        try: #example of still using try catch
            stmt = delete(ModelPost).where(ModelPost.post_id == post_id)
            db.session.execute(stmt) #a nother way of writing commands
            db.session.commit()

            is_success = True

        except Exception as exc:
            logger.error(exc)

        return is_success

    @staticmethod
    def get_all_posts(parent_post_id=None):
        posts = []
        post_query = select(ModelPost).where(ModelPost.parent_post_id == parent_post_id)
        posts = db.session.scalars(post_query).all()

        return posts

    @staticmethod
    def get_all_posts_flattened(parent_post_id=None, exclude_branch_post_id=None):
        posts_flattened = []
        post_hierarchy = ControllerDatabase.get_all_posts(parent_post_id)
        posts_flattened = post_hierarchy

        return posts_flattened

    @staticmethod
    def verify_session(session_token: str = None) -> bool:
        verified = False

        if session_token:
            token_query = select(ModelSession).where(ModelSession.token == session_token,
                                                     ModelSession.is_active == True)
            token : ModelSession = db.session.scalar(token_query)

            if token.expires_at < datetime.now(timezone.utc):
                token.is_active = False
                db.session.merge(token)
                return verified

            verified = True

        return verified

    @staticmethod
    def login(auth: ModelUser) -> str | None:
        with db.session.begin():
            user_query = select(ModelUser).where(ModelUser.username == auth.username)
            user = db.session.scalar(user_query)

            if user and bcrypt.checkpw(auth.password.encode(), user.password.encode()):
                expires_at = datetime.now() + timedelta(hours=1)

                new_session = ModelSession()
                new_session.user_id = user.uuid
                new_session.token = secrets.token_hex(32)
                new_session.expires_at = expires_at

                db.session.add(new_session)
                return new_session.token

        return None

    @staticmethod
    def logout(session_token: str = None) -> bool:
        with db.session.begin():
            stmt = select(ModelSession).where(ModelSession.token == session_token)
            current_session = db.session.scalar(stmt)
            if current_session:
                current_session.is_active = False
                return True

        return False


