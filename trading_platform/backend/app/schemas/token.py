from pydantic import BaseModel

class TokenBase(BaseModel):
    symbol: str
    exchange: str
    description: str | None = None

class Token(TokenBase):
    id: int

    class Config:
        orm_mode = True
