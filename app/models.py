from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Marca(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str

class Modelo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    tipo: str  # FG = Campo, TF = Society, IC = Quadra
    marca_id: int = Field(foreign_key="marca.id")

class FotoChuteira(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chuteira_id: int = Field(foreign_key="chuteira.id")
    url: str

class Chuteira(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cor: str
    modelo_id: int = Field(foreign_key="modelo.id")
    preco_pix: float
    preco_cartao: float
    fotos: List[FotoChuteira] = Relationship()