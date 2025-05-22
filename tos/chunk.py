from pydantic import BaseModel


class Chunk(BaseModel):
    id: str
    text: str
    meta: dict[str, str]
