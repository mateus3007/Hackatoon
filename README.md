# API de Usuários com FastAPI

API simples para gerenciar usuários e suas habilidades usando FastAPI e SQLite.

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute a aplicação:
```bash
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`

## Endpoints

### POST /usuario
Cria um novo usuário.

Exemplo de requisição:
```json
{
  "nome": "João",
  "habilidades": ["Python", "SQL", "Machine Learning"]
}
```

### GET /usuarios
Retorna todos os usuários cadastrados.

## Documentação
A documentação interativa da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 