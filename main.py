from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv
import os, secrets, redis, json

# CONFIGURAÇÕES/FUNÇÕES ================================================================================================

# Isso para carregar as variáves de ambiente primeiro.
load_dotenv()

# Essas sãos as configurações do SQLite para o funcionamento do banco de dados.
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Criação do client do redis.
REDIS_HOST = os.getenv("REDIS_HOST")
redis_client = redis.asyncio.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)

# modelo de criação da tabela onde é armazenado os livros no banco de dados.
class LivroDB(Base):
    __tablename__ = 'livros'

    _id = Column(Integer, primary_key=True, index=True)
    nome_livro = Column(String, index=True)
    autor_livro = Column(String, index=True)
    ano_livro = Column(Integer)

# modelo para criação do objeto para definir as informações de um Livro.
class Livro(BaseModel):
    _id: int
    nome_livro: str
    autor_livro: str
    ano_livro: int

# Cria a tabela de acordo com o modelo.
Base.metadata.create_all(bind=engine)

# Inicia o FastAPI.
app = FastAPI(
    title="Api para Livros",
    description="API para catalogar livros",
    version="0.1.0",
    contact={
        "name":"Pedro Américo",
        "email":"pedrobravo1406@gmail.com"
    }
)

# Variáveis para definir um Usuário e Senha pelas variáveis de ambiente.
LOGIN_USUARIO = os.getenv("LOGIN_USUARIO")
SENHA_USUARIO = os.getenv("SENHA_USUARIO")

# Funções do redis para salvar livros no cache e deletar livros no cache.
async def salvar_livros_redis(cache_key: str, livros: dict):
    chave = cache_key
    dados_json = json.dumps(livros)
    await redis_client.set(chave, dados_json, ex=300)
async def deletar_livros_redis():
    await redis_client.delete("livros")

# Garante que cada requisição no banco de dados funcione com sua prorpia sessão e que ela seja devidademnte fechada no fim.
def session_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configurações de autendicação com função para conferir se as credenciais estão corretas.
security = HTTPBasic()
def autendicacao(credentials: HTTPBasicCredentials = Depends(security)):
    is_login_correct = secrets.compare_digest(credentials.username, LOGIN_USUARIO)
    is_senha_correct = secrets.compare_digest(credentials.password, SENHA_USUARIO)

    if not (is_login_correct and is_senha_correct):
        raise HTTPException(status_code=401,detail="Senha ou usuario invalidos.",headers={"WWW-Authenticate":"Basic"})


#ENDPOITS ==============================================================================================================

# Endpoint principal para o método GET: primeiro confere se tem as informações no cache, caso tenha ele ja entrega a resposta, caso não ele retorna do banco de dados e salva um novo cache. 
@app.get("/livros")
async def get_livros(page: int = 1, limit: int = 10, db: Session = Depends(session_db), credentials: HTTPBasicCredentials = Depends(autendicacao)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page ou Limit estão invalidos!!")
    cache_key = "livros"
    cached = await redis_client.get(cache_key)
    if cached is not None:
        return json.loads(cached)
    
    livros = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()
    if not livros:
        return {"message":"Não existe nenhum livro no banco de dados"}
    total_livros = db.query(LivroDB).count()
    lista_livros = [{"id": livro._id,"nome":livro.nome_livro,"autor":livro.autor_livro, "ano":livro.ano_livro} for livro in livros]
    
    resposta = {
        "page": page,
        "limit": limit,
        "total livros": total_livros,
        "Livros": lista_livros
    }
    await salvar_livros_redis(cache_key, resposta)
    return resposta

# Endpoint principal para o método POST: adiciona um livro no banco de dados e, para manter a consistência dos dados caso exista um cache salvo, ele é deletado.
@app.post("/livros", status_code=201)
async def post_livros(livro: Livro, db: Session = Depends(session_db), credentials: HTTPBasicCredentials = Depends(autendicacao)):
    db_livro = db.query(LivroDB).filter(LivroDB.nome_livro == livro.nome_livro).first()
    if db_livro:
        raise HTTPException(status_code=400, detail="Este livro ja existe!")
    new_livro = LivroDB(nome_livro=livro.nome_livro, autor_livro=livro.autor_livro, ano_livro=livro.ano_livro)
    db.add(new_livro)
    db.commit()
    db.refresh(new_livro)
    await deletar_livros_redis()
    return {"message":"Livro criado com sucesso!"}

# Endpoint principal para o método PUT: para editar e atualizar informações de um livro ja existente no banco de dados, deleta o cache, caso exista, para manter a consistência nos dados.
@app.put("/livros/{_id}")
async def put_livros(_id: int, livro: Livro, db: Session = Depends(session_db), credentials: HTTPBasicCredentials = Depends(autendicacao)):
    db_livro = db.query(LivroDB).filter(LivroDB._id == _id).first()
    if not db_livro:
        raise HTTPException(status_code=404,detail="Este livro não foi encontrado!")
    db_livro.nome_livro = livro.nome_livro
    db_livro.autor_livro = livro.autor_livro
    db_livro.ano_livro = livro.ano_livro
    db.commit() 
    db.refresh(db_livro)
    await deletar_livros_redis()
    return {"message":"O livro foi atualizado com sucesso!"}

# Endpoint principal para o método DELETE: deleta um livro no banco de dados atravez do ID, também deleta o cache, caso exista, para manter a consistência dos dados.
@app.delete("/livros/{_id}")
async def delete_livros(_id: int, db: Session = Depends(session_db), credentials: HTTPBasicCredentials = Depends(autendicacao)):
    db_livro = db.query(LivroDB).filter(LivroDB._id == _id).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Esse livro não foi encontrado!")
    db.delete(db_livro)
    db.commit()
    await deletar_livros_redis()
    return {"message":"Seu livro foi deletado com sucesso!"}

# Endpoint GET para debug do cache do redis: retorna o cache salvo no momento e o Time to Live (ttl) atual dos dados no cache
@app.get("/debug/get")
async def ver_cache_redis():
    chaves = await redis_client.keys("livros")
    livros = []
    for chave in chaves:
        valor = await redis_client.get(chave)
        ttl = await redis_client.ttl(chave)
        livros.append({"chave": chave, "valor": json.loads(valor), "ttl": ttl})
    return livros