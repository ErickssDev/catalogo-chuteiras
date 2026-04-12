from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Marca, Chuteira
import shutil
import uuid
from fastapi import File, UploadFile
from pathlib import Path

router = APIRouter()

# ---- MARCAS ----

@router.get("/marcas")
def listar_marcas(session: Session = Depends(get_session)):
    marcas = session.exec(select(Marca)).all()
    return marcas

@router.post("/marcas")
def criar_marca(marca: Marca, session: Session = Depends(get_session)):
    session.add(marca)
    session.commit()
    session.refresh(marca)
    return marca

@router.put("/marcas/{id}")
def editar_marca(id: int, dados: Marca, session: Session = Depends(get_session)):
    marca = session.get(Marca, id)
    if not marca:
        raise HTTPException(status_code=404, detail="Marca não encontrada")
    marca.nome = dados.nome
    session.commit()
    session.refresh(marca)
    return marca

@router.delete("/marcas/{id}")
def deletar_marca(id: int, session: Session = Depends(get_session)):
    marca = session.get(Marca, id)
    if not marca:
        raise HTTPException(status_code=404, detail="Marca não encontrada")
    session.delete(marca)
    session.commit()
    return {"mensagem": "Marca deletada com sucesso"}

# ---- CHUTEIRAS ----

@router.get("/chuteiras")
def listar_chuteiras(session: Session = Depends(get_session)):
    chuteiras = session.exec(select(Chuteira)).all()
    return chuteiras

@router.get("/chuteiras/{id}")
def buscar_chuteira(id: int, session: Session = Depends(get_session)):
    chuteira = session.get(Chuteira, id)
    if not chuteira:
        raise HTTPException(status_code=404, detail="Chuteira não encontrada")
    return chuteira

@router.get("/marcas/{id}/chuteiras")
def listar_chuteiras_por_marca(id: int, session: Session = Depends(get_session)):
    marca = session.get(Marca, id)
    if not marca:
        raise HTTPException(status_code=404, detail="Marca não encontrada")
    chuteiras = session.exec(select(Chuteira).where(Chuteira.marca_id == id)).all()
    return {"marca": marca.nome, "chuteiras": chuteiras}

@router.post("/chuteiras")
def criar_chuteira(chuteira: Chuteira, session: Session = Depends(get_session)):
    session.add(chuteira)
    session.commit()
    session.refresh(chuteira)
    return chuteira

@router.put("/chuteiras/{id}")
def editar_chuteira(id: int, dados: Chuteira, session: Session = Depends(get_session)):
    chuteira = session.get(Chuteira, id)
    if not chuteira:
        raise HTTPException(status_code=404, detail="Chuteira não encontrada")
    chuteira.nome = dados.nome
    chuteira.marca_id = dados.marca_id
    chuteira.preco_pix = dados.preco_pix
    chuteira.preco_cartao = dados.preco_cartao
    chuteira.foto_url = dados.foto_url
    session.commit()
    session.refresh(chuteira)
    return chuteira

@router.delete("/chuteiras/{id}")
def deletar_chuteira(id: int, session: Session = Depends(get_session)):
    chuteira = session.get(Chuteira, id)
    if not chuteira:
        raise HTTPException(status_code=404, detail="Chuteira não encontrada")
    session.delete(chuteira)
    session.commit()
    return {"mensagem": "Chuteira deletada com sucesso"}

@router.post("/chuteiras/{id}/foto")
def upload_foto(id: int, foto: UploadFile = File(...), session: Session = Depends(get_session)):
    chuteira = session.get(Chuteira, id)
    if not chuteira:
        raise HTTPException(status_code=404, detail="Chuteira não encontrada")
    
    extensao = Path(foto.filename).suffix
    nome_arquivo = f"{uuid.uuid4()}{extensao}"
    caminho = Path("app/fotos") / nome_arquivo
    
    with open(caminho, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)
    
    chuteira.foto_url = f"/fotos/{nome_arquivo}"
    session.commit()
    session.refresh(chuteira)
    return chuteira