from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ClientBase(BaseModel):
    client_id: str
    name: str

class ClientCreate(ClientBase):
    api_key: str
    api_secret: str
    password: str
    two_fa: str

class Client(ClientBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
