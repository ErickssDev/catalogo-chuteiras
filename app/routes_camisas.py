from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlmodel import Session, select
from app.database import get_session
from app.models import Liga, TimeCamisa, ModeloCamisa, FotoModeloCamisa
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

router = APIRouter()

# ── LIGAS ──────────────────────────────────────────────────

@router.get("/ligas")
def listar_ligas(session: Session = Depends(get_session)):
    return session.exec(select(Liga)).all()

@router.post("/ligas")
def criar_liga(liga: Liga, session: Session = Depends(get_session)):
    session.add(liga)
    session.commit()
    session.refresh(liga)
    return liga

@router.put("/ligas/{id}")
def editar_liga(id: int, dados: Liga, session: Session = Depends(get_session)):
    liga = session.get(Liga, id)
    if not liga:
        raise HTTPException(status_code=404, detail="Liga não encontrada")
    liga.nome = dados.nome
    session.commit()
    session.refresh(liga)
    return liga

@router.delete("/ligas/{id}")
def deletar_liga(id: int, session: Session = Depends(get_session)):
    liga = session.get(Liga, id)
    if not liga:
        raise HTTPException(status_code=404, detail="Liga não encontrada")
    session.delete(liga)
    session.commit()
    return {"mensagem": "Liga deletada com sucesso"}

# ── TIMES ──────────────────────────────────────────────────

@router.get("/times")
def listar_times(session: Session = Depends(get_session)):
    return session.exec(select(TimeCamisa)).all()

@router.get("/ligas/{liga_id}/times")
def listar_times_por_liga(liga_id: int, session: Session = Depends(get_session)):
    liga = session.get(Liga, liga_id)
    if not liga:
        raise HTTPException(status_code=404, detail="Liga não encontrada")
    times = session.exec(select(TimeCamisa).where(TimeCamisa.liga_id == liga_id)).all()
    return {"liga": liga.nome, "times": times}

@router.post("/times")
def criar_time(time: TimeCamisa, session: Session = Depends(get_session)):
    session.add(time)
    session.commit()
    session.refresh(time)
    return time

@router.put("/times/{id}")
def editar_time(id: int, dados: TimeCamisa, session: Session = Depends(get_session)):
    time = session.get(TimeCamisa, id)
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    time.nome    = dados.nome
    time.liga_id = dados.liga_id
    session.commit()
    session.refresh(time)
    return time

@router.delete("/times/{id}")
def deletar_time(id: int, session: Session = Depends(get_session)):
    time = session.get(TimeCamisa, id)
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    session.delete(time)
    session.commit()
    return {"mensagem": "Time deletado com sucesso"}

# ── MODELOS DE CAMISA ──────────────────────────────────────

@router.get("/camisas")
def listar_camisas(session: Session = Depends(get_session)):
    modelos = session.exec(select(ModeloCamisa)).all()
    resultado = []
    for modelo in modelos:
        fotos = session.exec(
            select(FotoModeloCamisa).where(FotoModeloCamisa.modelo_id == modelo.id)
        ).all()
        time = session.get(TimeCamisa, modelo.time_id)
        liga = session.get(Liga, time.liga_id)
        resultado.append({
            "id": modelo.id,
            "nome": modelo.nome,
            "time": time.nome,
            "liga": liga.nome,
            "fotos": [{"id": f.id, "url": f.url} for f in fotos],
        })
    return resultado

@router.get("/camisas/{id}")
def buscar_camisa(id: int, session: Session = Depends(get_session)):
    modelo = session.get(ModeloCamisa, id)
    if not modelo:
        raise HTTPException(status_code=404, detail="Camisa não encontrada")
    fotos = session.exec(
        select(FotoModeloCamisa).where(FotoModeloCamisa.modelo_id == id)
    ).all()
    time = session.get(TimeCamisa, modelo.time_id)
    liga = session.get(Liga, time.liga_id)
    return {
        "id": modelo.id,
        "nome": modelo.nome,
        "time": time.nome,
        "liga": liga.nome,
        "fotos": [{"id": f.id, "url": f.url} for f in fotos],
    }

@router.get("/times/{time_id}/camisas")
def listar_camisas_por_time(time_id: int, session: Session = Depends(get_session)):
    time = session.get(TimeCamisa, time_id)
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    modelos = session.exec(
        select(ModeloCamisa).where(ModeloCamisa.time_id == time_id)
    ).all()
    resultado = []
    for modelo in modelos:
        fotos = session.exec(
            select(FotoModeloCamisa).where(FotoModeloCamisa.modelo_id == modelo.id)
        ).all()
        resultado.append({
            "id": modelo.id,
            "nome": modelo.nome,
            "fotos": [{"id": f.id, "url": f.url} for f in fotos],
        })
    return {"time": time.nome, "camisas": resultado}

@router.post("/camisas")
def criar_camisa(modelo: ModeloCamisa, session: Session = Depends(get_session)):
    session.add(modelo)
    session.commit()
    session.refresh(modelo)
    return modelo

@router.put("/camisas/{id}")
def editar_camisa(id: int, dados: ModeloCamisa, session: Session = Depends(get_session)):
    modelo = session.get(ModeloCamisa, id)
    if not modelo:
        raise HTTPException(status_code=404, detail="Camisa não encontrada")
    modelo.nome    = dados.nome
    modelo.time_id = dados.time_id
    session.commit()
    session.refresh(modelo)
    return modelo

@router.delete("/camisas/{id}")
def deletar_camisa(id: int, session: Session = Depends(get_session)):
    modelo = session.get(ModeloCamisa, id)
    if not modelo:
        raise HTTPException(status_code=404, detail="Camisa não encontrada")
    for foto in session.exec(
        select(FotoModeloCamisa).where(FotoModeloCamisa.modelo_id == id)
    ).all():
        session.delete(foto)
    session.delete(modelo)
    session.commit()
    return {"mensagem": "Camisa deletada com sucesso"}

# ── FOTOS ──────────────────────────────────────────────────

@router.post("/camisas/{id}/fotos")
def upload_foto(id: int, foto: UploadFile = File(...), session: Session = Depends(get_session)):
    modelo = session.get(ModeloCamisa, id)
    if not modelo:
        raise HTTPException(status_code=404, detail="Camisa não encontrada")
    resultado = cloudinary.uploader.upload(foto.file, folder="gsesportes/camisas")
    url = resultado["secure_url"]
    nova_foto = FotoModeloCamisa(modelo_id=id, url=url)
    session.add(nova_foto)
    session.commit()
    return {"mensagem": "Foto adicionada com sucesso", "url": url}

@router.delete("/camisas/{id}/fotos/{foto_id}")
def deletar_foto(id: int, foto_id: int, session: Session = Depends(get_session)):
    foto = session.get(FotoModeloCamisa, foto_id)
    if not foto or foto.modelo_id != id:
        raise HTTPException(status_code=404, detail="Foto não encontrada")
    session.delete(foto)
    session.commit()
    return {"mensagem": "Foto deletada com sucesso"}