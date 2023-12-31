from pydantic import BaseModel

from interface.schema.base_schema import ModelBaseInfo


class BaseUser(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class User(ModelBaseInfo, BaseUser):
    ...


class UpdateUser(BaseUser):
    ...
