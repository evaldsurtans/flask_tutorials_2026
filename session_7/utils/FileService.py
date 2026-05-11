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