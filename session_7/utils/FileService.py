from werkzeug.utils import secure_filename
from flask import current_app
import uuid, magic, os

from models.ModelFile import ModelFile


def upload_file(files) -> list[ModelFile]: #add allowed extensions?
    file_models : list[ModelFile] = []
    for file in files:
        model = ModelFile()

        original_name = secure_filename(file.filename)

        model.filename = original_name
        model.mime_type = magic.from_buffer(file.read(), mime=True)
        file.seek(0)

        file.filename = uuid.uuid4().hex+original_name

        full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)
        file.save(full_path)

        model.storage_path = full_path

        file_models.append(model)
    return file_models



# if file and not file.filename == '' and AllowedFileName(file.filename):
#     filename = secure_filename(file.filename)
#     ufilename = UniqueFileName(filename)
#     file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], ufilename.filename))
#     post.files = post.files + [ufilename.filename]  # upload is halfdone
#     print(post.files)

# from uuid import uuid4
#
# def make_unique(string):
#     ident = uuid4().__str__()
#     return f"{ident}-{string}"
#
# class UniqueFileName:
#     def __init__(self, filename):
#         self.filename : str = make_unique(filename)

# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
#
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS #rewrite
#
# class AllowedFileName:
#     def __init__(self, filename):
#         self.filename = allowed_file(filename)