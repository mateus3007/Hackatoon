# 📘 Plataforma Inteligente de Recomendação de Trilhas e Vagas

## 🚀 Visão Geral
Este projeto é uma API desenvolvida com *FastAPI, **SQLAlchemy* e *OpenAI* que tem como objetivo:

- Analisar as *habilidades técnicas* de um usuário;
- Comparar com *requisitos de vagas de estágio e emprego*;
- Identificar *gaps de conhecimento*;
- Gerar uma *trilha personalizada de estudo* baseada em fontes como *roadmap.sh* e *Universidade Livre*;
- Sugerir *recursos educativos* e oportunidades reais de estágio ou emprego;
- Retornar análises automatizadas com uso de *IA Generativa (OpenAI)*.

---

## 🛠️ Tecnologias Utilizadas
- *FastAPI* – estrutura principal da API
- *SQLite + SQLAlchemy* – banco de dados leve com ORM
- *Pydantic* – validação de modelos
- *Sentence Transformers* – embeddings para análise semântica
- *OpenAI GPT-3.5* – para gerar análises de compatibilidade e resumos de trilha
- *dotenv* – gestão de variáveis sensíveis
- *requests* – integração com APIs públicas de vagas

---

## 📦 Funcionalidades

### 👤 Usuários
- Criar usuário com habilidades técnicas
- Listar usuários

### 🧠 Análise de Compatibilidade
- Comparação de habilidades com vagas mock e reais (GitHub Jobs, Reed, Adzuna)
- Cálculo de compatibilidade exata e semântica (por embeddings)
- Análise textual automática com IA explicando forças, fraquezas e recomendações

### 🧪 Matching com Vagas
- Identifica vagas *compatíveis* e *incompatíveis*
- Armazena resultados no banco com score e análise

### 🧮 Análise de Habilidades
- Detecta *matches, **gaps* e *sugestões de aprendizado* para cada usuário/vaga

### 📚 Trilhas Personalizadas
- Gera trilhas com base em roadmap.sh ou Universidade Livre
- Organiza conteúdos por tecnologia, origem, link e tópicos
- Retorna trilhas existentes ou cria novas

### 📃 Resumo com IA
- Geração automática de resumo textual da trilha de estudo
- Apresenta sequência lógica, tom motivador e clareza

### 🔍 Recursos Sugeridos
- Sugere cursos e materiais gratuitos por tecnologia (por fonte confiável)

---

## 📂 Organização das Tabelas
- usuarios: dados e habilidades do usuário
- vagas: descrição, requisitos e empresa
- match_vagas: relacionamento entre usuário ↔ vaga com scores
- trilhas: trilhas geradas para cada usuário
- conteudos_externos: fontes como roadmap.sh e Universidade-Livre

---

## ▶️ Como Rodar Localmente

1. *Clone o projeto*
bash
git clone <repo_url>
cd <repo>


2. *Crie ambiente virtual e instale as dependências*
bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt


3. *Crie um arquivo .env* com sua chave da OpenAI:
env
OPENAI_API_KEY=sua-chave-aqui


4. *Inicie o servidor*
bash
uvicorn main:app --reload


5. *Acesse a documentação*
- [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔒 Observações Importantes
- Certifique-se de configurar a chave da OpenAI corretamente no .env
- O projeto utiliza *mock de vagas*, mas pode ser integrado a fontes reais
- Todas as trilhas e vagas são salvas no banco usuarios.db

---

## 📌 Créditos & Inspirações
- [roadmap.sh](https://roadmap.sh)
- [Universidade-Livre](https://github.com/Universidade-Livre)
- [OpenAI](https://openai.com)

---

## 🧠 Ideias Futuras
- Autenticação JWT para usuários
- Dashboard visual com progresso
- Upload de currículos em PDF
- Match com empresas reais via API do Gupy ou Vagas.com

---

Criado com ❤️ para conectar estudantes às oportunidades certas com tecnologia e inteligência artificial.
