from sqlmodel import SQLModel, Field
from typing import Optional

class Marca(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str

class Chuteira(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    marca_id: int = Field(foreign_key="marca.id")
    preco_pix: float
    preco_cartao: float
    foto_url: Optional[str] = None