from fastapi.testclient import TestClient
from main import app, Base, session_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
import os, pytest, fakeredis

# =========================================================Configurações=========================================================
load_dotenv()

APIclient = TestClient(app)
SENHA = os.getenv("SENHA_USUARIO")
LOGIN = os.getenv("LOGIN_USUARIO")
DATABASE_URL = "sqlite://"

engine = create_engine(DATABASE_URL,connect_args={"check_same_thread": False},poolclass=StaticPool,)
TestingSessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)

@pytest.fixture(name="session", scope="module")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass
    app.dependency_overrides[session_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture(name="redis_mock", autouse=True)
async def mock_redis(monkeypatch):
    fake_client = fakeredis.FakeAsyncRedis(decode_responses=True)
    monkeypatch.setattr("main.redis_client", fake_client)
    return fake_client

# =========================================================Testes=========================================================

def test_autentificacao_de_requisicoes_falha(client):
    resposta = client.get(
        '/livros',
        auth=('Jonatas','444')
    )
    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Senha ou usuario invalidos."

def test_metodo_get_retorna_ok(client):
    resposta = client.get(
        "/livros",
        auth=(LOGIN,SENHA)
    )
    assert resposta.status_code == 200

def test_metodo_post_retorna_ok(client):
    data = {"nome_livro":"Teste 1",
            "autor_livro":"Alguem",
            "ano_livro": "2000"
            }
    resposta = client.post(
        "/livros",
        auth=(LOGIN,SENHA),
        json=data
    )
    assert resposta.status_code == 201

def test_metodo_get_retorna_livro_banco_de_dados(client):
    resposta = client.get(
        "/livros",
        auth=(LOGIN,SENHA)
    )
    assert resposta.json()['Livros'] == [{"id": 1,"nome":"Teste 1","autor":"Alguem","ano":2000}]

def test_metodo_put_retorna_ok(client):
    data = {"nome_livro":"Teste 2",
            "autor_livro":"Eu",
            "ano_livro": "2009"}
    resposta = client.put(
        "/livros/1",
        auth=(LOGIN,SENHA),
        json=data
    )
    assert resposta.status_code == 200

def test_metodo_get_retorna_livro_atualizado(client):
    resposta = client.get(
        "/livros",
        auth=(LOGIN,SENHA)
    )
    assert resposta.json()['Livros'] == [{"id": 1,"nome":"Teste 2","autor":"Eu","ano":2009}]

def test_metodo_delete_retorna_ok(client):
    resposta = client.delete(
        "/livros/1",
        auth=(LOGIN,SENHA)
    )
    assert resposta.status_code == 200

def test_metodo_get_retorna_ok_depois_de_livro_deletado(client):
    resposta = client.get(
        "/livros",
        auth=(LOGIN,SENHA)
    )
    assert resposta.json()['message'] == "Não existe nenhum livro no banco de dados"