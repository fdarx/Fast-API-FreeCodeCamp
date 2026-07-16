
from pydantic import BaseModel

class Post(BaseModel):
    title: str
    content: str
    published: bool = True  #optional, default value is True

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True  #optional, default value is True

class PostCreate(PostBase):
    pass

