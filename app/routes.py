from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlmodel import Session, select
from app.database import get_session
from app.models import Marca, Modelo, Chuteira, FotoChuteira
import shutil
import uuid
from pathlib import Path
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

router = APIRouter()

# ---- MARCAS ----

@router.get("/marcas")
def listar_marcas(session: Session = Depends(get_session)):
    return session.exec(select(Marca)).all()

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

# ---- MODELOS ----

@router.get("/modelos")
def listar_modelos(session: Session = Depends(get_session)):
    return session.exec(select(Modelo)).all()

@router.post("/modelos")
def criar_modelo(modelo: Modelo, session: Session = Depends(get_session)):
    session.add(modelo)
    session.commit()
    session.refresh(modelo)
    return modelo

@router.put("/modelos/{id}")
def editar_modelo(id: int, dados: Modelo, session: Session = Depends(get_session)):
    modelo = session.get(Modelo, id)
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")
    modelo.nome = dados.nome
    modelo.tipo = dados.tipo
    modelo.marca_id = dados.marca_id
    session.commit()
    session.refresh(modelo)
    return modelo

@router.delete("/modelos/{id}")
def deletar_modelo(id: int, session: Session = Depends(get_session)):
    modelo = session.get(Modelo, id)
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")
    session.delete(modelo)
    session.commit()
    return {"mensagem": "Modelo deletado com sucesso"}

@router.get("/marcas/{id}/modelos")
def listar_modelos_por_marca(id: int, session: Session = Depends(get_session)):
    marca = session.get(Marca, id)
    if not marca:
        raise HTTPException(status_code=404, detail="Marca não encontrada")
    modelos = session.exec(select(Modelo).where(Modelo.marca_id == id)).all()
    return {"marca": marca.nome, "modelos": modelos}

@router.get("/modelos/tipo/{tipo}")
def listar_modelos_por_tipo(tipo: str, session: Session = Depends(get_session)):
    modelos = session.exec(select(Modelo).where(Modelo.tipo == tipo)).all()
    return modelos

# ---- CHUTEIRAS ----

@router.get("/chuteiras")
def listar_chuteiras(session: Session = Depends(get_session)):
    chuteiras = session.exec(select(Chuteira)).all()
    resultado = []
    for chuteira in chuteiras:
        fotos = session.exec(select(FotoChuteira).where(FotoChuteira.chuteira_id == chuteira.id)).all()
        modelo = session.get(Modelo, chuteira.modelo_id)
        marca = session.get(Marca, modelo.marca_id)
        resultado.append({
            "id": chuteira.id,
            "cor": chuteira.cor,
            "modelo": modelo.nome,
            "tipo": modelo.tipo,
            "marca": marca.nome,
            "preco_pix": chuteira.preco_pix,
            "preco_cartao": chuteira.preco_cartao,
            "fotos": [f.url for f in fotos]
        })
    return resultado

@router.get("/chuteiras/{id}")
def buscar_chuteira(id: int, session: Session = Depends(get_session)):
    chuteira = session.get(Chuteira, id)
    if not chuteira:
        raise HTTPException(status_code=404, detail="Chuteira não encontrada")
    fotos = session.exec(select(FotoChuteira).where(FotoChuteira.chuteira_id == id)).all()
    modelo = session.get(Modelo, chuteira.modelo_id)
    marca = session.get(Marca, modelo.marca_id)
    return {
        "id": chuteira.id,
        "cor": chuteira.cor,
        "modelo": modelo.nome,
        "tipo": modelo.tipo,
        "marca": marca.nome,
        "preco_pix": chuteira.preco_pix,
        "preco_cartao": chuteira.preco_cartao,
        "fotos": [f.url for f in fotos]
    }

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
    chuteira.cor = dados.cor
    chuteira.modelo_id = dados.modelo_id
    chuteira.preco_pix = dados.preco_pix
    chuteira.preco_cartao = dados.preco_cartao
    session.commit()
    session.refresh(chuteira)
    return chuteira

@router.delete("/chuteiras/{id}")
def deletar_chuteira(id: int, session: Session = Depends(get_session)):
    chuteira = session.get(Chuteira, id)
    if not chuteira:
        raise HTTPException(status_code=404, detail="Chuteira não encontrada")
    fotos = session.exec(select(FotoChuteira).where(FotoChuteira.chuteira_id == id)).all()
    for foto in fotos:
        session.delete(foto)
    session.delete(chuteira)
    session.commit()
    return {"mensagem": "Chuteira deletada com sucesso"}

@router.get("/modelos/{id}/chuteiras")
def listar_chuteiras_por_modelo(id: int, session: Session = Depends(get_session)):
    modelo = session.get(Modelo, id)
    if not modelo:
        raise HTTPException(status_code=404, detail="Modelo não encontrado")
    chuteiras = session.exec(select(Chuteira).where(Chuteira.modelo_id == id)).all()
    resultado = []
    for chuteira in chuteiras:
        fotos = session.exec(select(FotoChuteira).where(FotoChuteira.chuteira_id == chuteira.id)).all()
        resultado.append({
            "id": chuteira.id,
            "cor": chuteira.cor,
            "preco_pix": chuteira.preco_pix,
            "preco_cartao": chuteira.preco_cartao,
            "fotos": [f.url for f in fotos]
        })
    return {"modelo": modelo.nome, "tipo": modelo.tipo, "chuteiras": resultado}

# ---- FOTOS ----

@router.post("/chuteiras/{id}/fotos")
def upload_foto(id: int, foto: UploadFile = File(...), session: Session = Depends(get_session)):
    chuteira = session.get(Chuteira, id)
    if not chuteira:
        raise HTTPException(status_code=404, detail="Chuteira não encontrada")
    
    resultado = cloudinary.uploader.upload(foto.file, folder="gsesportes")
    url = resultado["secure_url"]
    
    nova_foto = FotoChuteira(chuteira_id=id, url=url)
    session.add(nova_foto)
    session.commit()
    return {"mensagem": "Foto adicionada com sucesso", "url": url}

@router.delete("/chuteiras/{id}/fotos/{foto_id}")
def deletar_foto(id: int, foto_id: int, session: Session = Depends(get_session)):
    foto = session.get(FotoChuteira, foto_id)
    if not foto or foto.chuteira_id != id:
        raise HTTPException(status_code=404, detail="Foto não encontrada")
    session.delete(foto)
    session.commit()
    return {"mensagem": "Foto deletada com sucesso"}