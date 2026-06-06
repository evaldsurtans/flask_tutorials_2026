from loguru import logger
from sqlalchemy.sql.operators import contains

from models.ModelFile import ModelFile
from models.ModelSession import ModelSession
from models.ModelPost import ModelPost
import secrets, bcrypt
from datetime import datetime, timedelta, timezone
from models.Database import db
from sqlalchemy import select, delete

from models.ModelTags import ModelTags
from models.ModelUsers import ModelUser
from models.ModelTagsInPost import ModelTagsInPost

from flask import url_for

class ControllerDatabase:

    @staticmethod
    def insert_post(post: ModelPost, current_session, file_models : list[ModelFile] = None, tags: list = None) -> int:
        user_query = select(ModelSession).where(ModelSession.token == current_session)
        user = db.session.scalar(user_query)

        if user:
            post.owner_uuid = user.user_id

            if file_models:
                for file_model in file_models:
                    file_model.owner_id = user.user_id
                    post.files.append(file_model)

            for tag in tags:
                stmt = select(ModelTags).where(ModelTags.tag_name == tag)
                existing_tag = db.session.scalar(stmt)

                if existing_tag:
                    link = ModelTagsInPost(tags=existing_tag)
                    post.post_tags.append(link)
                else:
                    new_tag = ModelTags(tag_name=tag)
                    new_tag.owner_uuid = user.user_id
                    new_link = ModelTagsInPost(tags=new_tag)
                    post.post_tags.append(new_link)

        db.session.add(post)
        db.session.commit()
        return post.post_id

    @staticmethod
    def update_post(post: ModelPost, current_session: str = None, file_models : list[ModelFile] = None, deleted_ids: list = None, tags: list = None) -> bool:
        is_success = False

        user_query = select(ModelSession).where(ModelSession.token == current_session)
        user = db.session.scalar(user_query)

        # nested because scalar already started a transaction
        if user and user.user_id == post.owner_uuid:

            post.post_tags.clear()
            for tag in tags:
                stmt = select(ModelTags).where(ModelTags.tag_name == tag)
                existing_tag = db.session.scalar(stmt)

                if existing_tag:
                    link = ModelTagsInPost(tags=existing_tag)
                    post.post_tags.append(link)
                else:
                    new_tag = ModelTags(tag_name=tag)
                    new_tag.owner_uuid = user.user_id
                    new_link = ModelTagsInPost(tags=new_tag)
                    post.post_tags.append(new_link)

            if file_models:
                for file_model in file_models:
                    file_model.owner_id = user.user_id
                    post.files.append(file_model)

            if deleted_ids:
                stmt = select(ModelFile).where(ModelFile.file_id.in_(deleted_ids))
                files = db.session.scalars(stmt)
                for file in files:
                    file.is_deleted = True

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

        if post:
            #files_query = select(ModelFile).where(ModelFile.post_id == post.post_id)
            #files = db.session.scalars(files_query)

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

            if token and token.expires_at < datetime.now():
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

    @staticmethod
    def get_all_tags(query_filter : str = None, query_tab : str = None):
        with db.session.begin():
            tags_query = select(ModelTags).limit(20)
            if query_filter:
                tags_query = select(ModelTags).limit(20).filter(ModelTags.tag_name.contains(query_filter))
                print("has")

            tags = db.session.scalars(tags_query)

            serialized_tags = [
                {"tag_id": tag.tag_id, "tag_name": tag.tag_name, "tag_url": url_for('tags.edit_tags', tag_id=tag.tag_id), "created": tag.created}
                for tag in tags
            ]

            return serialized_tags

    @staticmethod
    def get_tag(tag_id : int = None) -> ModelTags:
        tag_query = select(ModelTags).where(ModelTags.tag_id == tag_id)
        tag = db.session.scalar(tag_query)
        return tag

    @staticmethod
    def delete_tag(tag : ModelTags = None, current_session = None):
        is_success = False
        user_query = select(ModelSession).where(ModelSession.token == current_session)
        user = db.session.scalar(user_query)

        if user and user.user_id == tag.owner_uuid:
            stmt = delete(ModelTags).where(ModelTags.tag_id == tag.tag_id)
            db.session.execute(stmt)
            db.session.commit()
            is_success = True

        return is_success

    @staticmethod
    def edit_tag(tag : ModelTags = None, current_session = None):
        is_success = False
        user_query = select(ModelSession).where(ModelSession.token == current_session)
        user = db.session.scalar(user_query)

        if user and user.user_id == tag.owner_uuid:
            db.session.merge(tag)
            db.session.commit()
            is_success = True
        return is_success

