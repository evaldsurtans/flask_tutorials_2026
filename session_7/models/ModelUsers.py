import dataclasses

@dataclasses.dataclass
class ModelUser:
    uuid: str = None
    username: str = None
    password: str = None
    session_token: int = None