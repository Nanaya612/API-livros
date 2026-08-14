# API livros
<span style="font-size: 135%;">Uma API simples para catalogar livros, feita com Python e FastAPI, com um sistema de Containers, Banco de Dados com SQLite e sistema de cache com Redis.<span>

# Instalação
## 1. Pré-requisitos:
* Python 3.4
* FastAPI
* podman / docker
* podman-compose / docker-compose

## 2. Clone o Reposítorio:
* Utilize o comando no terminal `git clone https://github.com/Nanaya612/API-livros`.
* Depois utilize `cd API-livros`.

## 3. Inicie a aplicação:
* Utilize o comando no termial `podman machine init` e depois `podman machine start` para iniciar a maquina virtual.
* Depois utilize o comando `podman-compose build` para montar as imagens dos containers.
* Depois utilize o comando `podman-compose up -d` para rodar a aplicação e o redis.

## 4. Acesso e uso:

<strong style="font-size: 110%; margin-right: 5px">Método GET:</strong> Acessando o endpoint `http://127.0.0.1:8000/livros` para requisitar os livros salvos, pode definir um número como parâmetros **page** e **limit** para customizar qual página e o tamanha dela na resposta.

<strong style="font-size: 110%; margin-right: 5px">Método POST:</strong> Acessando o endpoint `http://127.0.0.1:8000/livros` para adicionar um livro ao banco de dados passando as variáveis **"nome_livro"**, **"autor_livro"**, **"ano_livro"** no corpo da requisição.

<strong style="font-size: 110%; margin-right: 5px">Método PUT:</strong> Acessando o endpoint `http://127.0.0.1:8000/livros/{id}` para alterar as informações de um livro existente atravez do ID passando as variáveis pelo corpo da requisição.

<strong style="font-size: 110%; margin-right: 5px">Método DELETE:</strong> Acessando o endpoint `http://127.0.0.1:8000/livros/{id}` para deletar um livro específico atravez do ID.


_para parar os serviços utilize `podman-compose stop` e para desligar e apagar os containers utilize `podman-compose down`_