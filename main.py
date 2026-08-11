from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

# Definição do modelo dos livros com pydantic
class Livro(BaseModel):
    id: int
    nome: str
    autor: str
    ano_lancamento: int 

# Simulação do Banco de Dados
Livros:dict[int, Livro] = {}

app=FastAPI(
    title="API para Livros",
    description="API para catalogar livros",
    version="0.1.0"
)

# Função assíncrona do Endpoint para buscar os livros no banco de dados. Utiliza um sistema de paginação para retornar apenas uma quantia dos livros armazenados e um simulador de tempo de busca.
@app.get("/livros")
async def get_livros(page: int = 1, limit: int = 10):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400,detail="Pagina ou Limite invalidos.")
    
    # Simulação do tempo de busca no Banco de Dados
    await asyncio.sleep(0.4)

    if not Livros:
        return {"message": "Não existe nenhum livro!"}
    start = (page - 1) * limit
    end = start + limit
    lista_livros = list(Livros.values())
    Livros_Paginados = lista_livros[start:end]
    Pagina_Livros = [{"_id": livro.id, "Nome":livro.nome, "Autor":livro.autor, "Ano Lançamento": livro.ano_lancamento} for livro in Livros_Paginados]
    return {
        "Page": page,
        "Limit": limit,
        "Total": len(Livros),
        "livros": Pagina_Livros 
    }

# Função assíncrona do Endpoint para adicionar livros no banco de dados. Com Simulação de tempo de busca e tratamento se o id do livro ja existir no banco de dados.
@app.post("/livros", status_code=201)
async def post_livros(livro: Livro):

    # Simulação do tempo de busca no Banco de Dados
    await asyncio.sleep(0.5)

    if livro.id in Livros:
        raise HTTPException(status_code=400, detail="O livro ja existe!")
    Livros[livro.id] = livro
    return {"message":"Livro adicionado com sucesso!"}

# Função assíncrona do Endpoint para deletar um livro do banco de dados. A função recebe via parametro o id do livro a ser deletado, apresentando tratamento de erro caso o livro não exista e simulação de tempo de busca no banco de dados.
@app.delete("/livros/{_id}")
async def delete_livros(_id: int):

    # Simulação do tempo para deletar
    await asyncio.sleep(0.3)

    if _id not in Livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    del Livros[_id]
    return {"message":"Livro deletado com sucesso!"}

# Função assíncrona do Endpoint para atualizar as informações de um livro no banco de dados. A função recebe via parametro o id do livro para ser atualizado com tratamento de erro para caso o livro não exista no banco, também, apresentando simulação de tempo de busca.
@app.put("/livros/{_id}")
async def put_livros(_id: int, livro: Livro):

    # Simulação do tempo para atualizar o livro
    await asyncio.sleep(0.2)

    if _id not in Livros:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")
    Livros[_id] = livro
    return {"message": "Livro atualizado com sucesso!"}