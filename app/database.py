from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL = "sqlite:///./gsesportes.db"

engine = create_engine(DATABASE_URL, echo=True)

def criar_tabelas():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session