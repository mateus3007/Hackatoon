from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, JSON, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
from datetime import datetime
from contextlib import contextmanager
import numpy as np
import traceback
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests

# Carrega variáveis de ambiente
load_dotenv()

# Configuração OpenAI
client = OpenAI(api_key=os.getenv("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"))

# Lazy loading do modelo
model = None

def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./usuarios.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    habilidades = Column(JSON)
    matches = relationship("MatchVaga", back_populates="usuario")
    trilhas = relationship("Trilha", back_populates="usuario")

class Vaga(Base):
    __tablename__ = "vagas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    empresa = Column(String, index=True)
    descricao = Column(Text)
    requisitos = Column(JSON)
    local = Column(String)
    url_aplicacao = Column(String)
    matches = relationship("MatchVaga", back_populates="vaga")

class MatchVaga(Base):
    __tablename__ = "match_vagas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    vaga_id = Column(Integer, ForeignKey("vagas.id"))
    score = Column(Float)
    score_semantico = Column(Float, nullable=True)
    analise_texto = Column(Text, nullable=True)
    status = Column(String)  # "compativel" ou "incompativel"
    data_match = Column(String, default=datetime.now().isoformat())
    
    usuario = relationship("Usuario", back_populates="matches")
    vaga = relationship("Vaga", back_populates="matches")

class Trilha(Base):
    __tablename__ = "trilhas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    tecnologia = Column(String, index=True)
    origem = Column(String)  # "roadmap.sh" ou "Universidade-Livre"
    link = Column(String)
    topicos = Column(JSON)  # Lista de tópicos em formato JSON
    data_criacao = Column(String, default=datetime.now().isoformat())
    
    usuario = relationship("Usuario", back_populates="trilhas")

class ConteudoExterno(Base):
    __tablename__ = "conteudos_externos"

    id = Column(Integer, primary_key=True, index=True)
    tecnologia = Column(String, index=True)
    origem = Column(String)  # "roadmap.sh" ou "Universidade-Livre"
    link = Column(String)
    fonte_nome = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class UsuarioCreate(BaseModel):
    nome: str
    habilidades: List[str]

class UsuarioResponse(UsuarioCreate):
    id: int

    class Config:
        from_attributes = True

class VagaBase(BaseModel):
    titulo: str
    empresa: str
    descricao: str
    requisitos: List[str]
    local: str
    url_aplicacao: str

class VagaResponse(VagaBase):
    id: int
    compatibilidade: Optional[float] = None
    compatibilidade_semantica: Optional[float] = None
    compativel_semantico: Optional[bool] = None
    analise_texto: Optional[str] = None

    class Config:
        from_attributes = True

class VagasUsuarioResponse(BaseModel):
    vagas_compativeis: List[VagaResponse]
    vagas_incompativeis: List[VagaResponse]

class MatchVagaResponse(BaseModel):
    id: int
    usuario_id: int
    vaga_id: int
    score: float
    score_semantico: Optional[float]
    analise_texto: Optional[str]
    status: str
    data_match: str

    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    titulo: str
    tecnologias: List[str]
    empresa: str
    link: str

class PublicJobResponse(BaseModel):
    nome: str
    empresa: str
    localidade: str
    descricao: str
    requisitos: List[str]

class AnaliseHabilidades(BaseModel):
    match: List[str]
    gaps: List[str]
    sugestao: List[str]

class TrilhaRequest(BaseModel):
    usuario_id: int
    gaps: List[str]

class TopicoTrilha(BaseModel):
    tecnologia: str
    origem: str
    link: str
    topicos: List[str]

class TrilhaResponse(BaseModel):
    trilhas: List[TopicoTrilha]

    class Config:
        from_attributes = True

class TrilhaUsuarioResponse(BaseModel):
    usuario_id: int
    trilhas: List[TopicoTrilha]

    class Config:
        from_attributes = True

# Mock data for jobs
VAGAS_MOCK = [
    {
        "id": 1,
        "titulo": "Desenvolvedor Python Backend",
        "empresa": "TechCorp Brasil",
        "descricao": "Estamos procurando um desenvolvedor Python para trabalhar em projetos de alta escala. Você será responsável por desenvolver e manter APIs RESTful, trabalhar com microsserviços e garantir a qualidade do código.",
        "requisitos": ["Python", "FastAPI", "SQL", "Docker", "AWS", "Testes Automatizados"],
        "local": "São Paulo - Remoto",
        "url_aplicacao": "https://techcorp.com/vagas/backend-python"
    },
    {
        "id": 2,
        "titulo": "Cientista de Dados",
        "empresa": "DataScience Co",
        "descricao": "Procuramos um Cientista de Dados para trabalhar em projetos de análise preditiva e machine learning. Você irá desenvolver modelos de ML, realizar análises estatísticas e criar dashboards interativos.",
        "requisitos": ["Python", "Machine Learning", "SQL", "Pandas", "Scikit-learn", "TensorFlow"],
        "local": "Rio de Janeiro - Híbrido",
        "url_aplicacao": "https://datascience.co/vagas/cientista-dados"
    },
    {
        "id": 3,
        "titulo": "Desenvolvedor Full Stack",
        "empresa": "StartupInovadora",
        "descricao": "Vaga para desenvolvedor full stack em startup em crescimento. Você irá trabalhar tanto no frontend quanto no backend, desenvolvendo novas features e melhorando a experiência do usuário.",
        "requisitos": ["Python", "JavaScript", "React", "SQL", "Docker", "Git"],
        "local": "Belo Horizonte - Remoto",
        "url_aplicacao": "https://startupinovadora.com/vagas/fullstack"
    },
    {
        "id": 4,
        "titulo": "DevOps Engineer",
        "empresa": "CloudTech Solutions",
        "descricao": "Procuramos um engenheiro DevOps para gerenciar nossa infraestrutura em nuvem e automatizar processos de CI/CD. Você será responsável por garantir a disponibilidade e performance dos nossos serviços.",
        "requisitos": ["Docker", "Kubernetes", "Python", "AWS", "Terraform", "Jenkins"],
        "local": "Curitiba - Híbrido",
        "url_aplicacao": "https://cloudtech.com/vagas/devops"
    },
    {
        "id": 5,
        "titulo": "Desenvolvedor Mobile",
        "empresa": "AppMakers",
        "descricao": "Vaga para desenvolvedor mobile com foco em React Native. Você irá desenvolver aplicativos móveis multiplataforma e trabalhar em conjunto com a equipe de design para criar interfaces intuitivas.",
        "requisitos": ["React Native", "JavaScript", "TypeScript", "Redux", "Git", "CI/CD"],
        "local": "Porto Alegre - Remoto",
        "url_aplicacao": "https://appmakers.com/vagas/mobile"
    },
    {
        "id": 6,
        "titulo": "Desenvolvedor Frontend Senior",
        "empresa": "WebTech Solutions",
        "descricao": "Procuramos um desenvolvedor frontend senior para liderar o desenvolvimento de interfaces modernas e responsivas. Experiência com frameworks modernos e arquitetura de componentes é essencial.",
        "requisitos": ["React", "TypeScript", "Next.js", "GraphQL", "Jest", "Styled Components"],
        "local": "São Paulo - Remoto",
        "url_aplicacao": "https://webtech.com/vagas/frontend-senior"
    },
    {
        "id": 7,
        "titulo": "Arquiteto de Software",
        "empresa": "Enterprise Systems",
        "descricao": "Vaga para arquiteto de software com foco em sistemas distribuídos e microsserviços. Você será responsável por definir a arquitetura técnica e garantir a escalabilidade dos sistemas.",
        "requisitos": ["Java", "Spring Boot", "Kubernetes", "MongoDB", "RabbitMQ", "Microservices"],
        "local": "Brasília - Híbrido",
        "url_aplicacao": "https://enterprise.com/vagas/arquiteto"
    },
    {
        "id": 8,
        "titulo": "Desenvolvedor Backend Node.js",
        "empresa": "API Masters",
        "descricao": "Estamos procurando um desenvolvedor backend especializado em Node.js para trabalhar em APIs de alta performance. Experiência com sistemas assíncronos e otimização de performance é desejável.",
        "requisitos": ["Node.js", "TypeScript", "PostgreSQL", "Redis", "Docker", "REST APIs"],
        "local": "Salvador - Remoto",
        "url_aplicacao": "https://apimasters.com/vagas/nodejs"
    },
    {
        "id": 9,
        "titulo": "Engenheiro de Machine Learning",
        "empresa": "AI Solutions",
        "descricao": "Vaga para engenheiro de ML com foco em processamento de linguagem natural. Você irá desenvolver e implementar modelos de NLP para análise de texto e classificação de documentos.",
        "requisitos": ["Python", "TensorFlow", "PyTorch", "NLP", "BERT", "Transformers"],
        "local": "Campinas - Híbrido",
        "url_aplicacao": "https://aisolutions.com/vagas/ml-engineer"
    },
    {
        "id": 10,
        "titulo": "Desenvolvedor Full Stack Java",
        "empresa": "Enterprise Software",
        "descricao": "Procuramos um desenvolvedor full stack com experiência em Java e frameworks modernos. Você irá trabalhar no desenvolvimento de sistemas empresariais e integração com sistemas legados.",
        "requisitos": ["Java", "Spring Boot", "Angular", "PostgreSQL", "Docker", "Jenkins"],
        "local": "Recife - Remoto",
        "url_aplicacao": "https://enterprise.com/vagas/fullstack-java"
    }
]

# Roadmap data structure
ROADMAP_DATA = {
    "React": {
        "link": "https://roadmap.sh/react",
        "etapas": [
            "JSX", "Components", "Props", "State", "Lifecycle Methods",
            "Hooks", "Context API", "Routing", "State Management",
            "Server Side Rendering", "Testing", "Performance Optimization"
        ]
    },
    "Docker": {
        "link": "https://roadmap.sh/docker",
        "etapas": [
            "Containers", "Images", "Dockerfile", "Docker Compose",
            "Networking", "Volumes", "Docker Swarm", "Security",
            "CI/CD Integration", "Monitoring"
        ]
    },
    "Node.js": {
        "link": "https://roadmap.sh/nodejs",
        "etapas": [
            "JavaScript Basics", "Node.js Core", "NPM", "Express.js",
            "REST APIs", "Authentication", "Database Integration",
            "Testing", "Deployment", "Performance Optimization"
        ]
    }
}

# FastAPI app
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calcular_compatibilidade(habilidades_usuario: List[str], requisitos_vaga: List[str]) -> float:
    matches = sum(1 for hab in habilidades_usuario if hab.lower() in [req.lower() for req in requisitos_vaga])
    total_requisitos = len(requisitos_vaga)
    return round(matches / total_requisitos * 100, 2) if total_requisitos > 0 else 0

def calcular_similaridade_semantica(perfil: str, descricao: str) -> float:
    try:
        # Codifica os textos
        model = get_model()
        perfil_embedding = model.encode(perfil, convert_to_tensor=True)
        descricao_embedding = model.encode(descricao, convert_to_tensor=True)
        
        # Converte para numpy para cálculos
        perfil_embedding = perfil_embedding.cpu().numpy()
        descricao_embedding = descricao_embedding.cpu().numpy()
        
        # Calcula a similaridade do cosseno
        similarity = np.dot(perfil_embedding, descricao_embedding) / (
            np.linalg.norm(perfil_embedding) * np.linalg.norm(descricao_embedding)
        )
        
        return round(float(similarity), 4)
    except Exception as e:
        print(f"Erro ao calcular similaridade semântica: {str(e)}")
        print(traceback.format_exc())
        return 0.0

def salvar_matches(db: Session, usuario_id: int, vagas_compativeis: List[dict], vagas_incompativeis: List[dict]):
    # Limpa matches anteriores do usuário
    db.query(MatchVaga).filter(MatchVaga.usuario_id == usuario_id).delete()
    
    # Salva novos matches
    for vaga in vagas_compativeis:
        match = MatchVaga(
            usuario_id=usuario_id,
            vaga_id=vaga["id"],
            score=vaga["compatibilidade"],
            score_semantico=vaga.get("compatibilidade_semantica"),
            status="compativel"
        )
        db.add(match)
    
    for vaga in vagas_incompativeis:
        match = MatchVaga(
            usuario_id=usuario_id,
            vaga_id=vaga["id"],
            score=vaga["compatibilidade"],
            score_semantico=vaga.get("compatibilidade_semantica"),
            status="incompativel"
        )
        db.add(match)
    
    db.commit()

def analisar_compatibilidade(habilidades_usuario: List[str], vaga: dict) -> str:
    try:
        prompt = f"""
        Analise a compatibilidade entre o perfil do usuário e a vaga, identificando pontos fortes e fracos.
        
        Perfil do usuário:
        - Habilidades: {', '.join(habilidades_usuario)}
        
        Vaga:
        - Título: {vaga['titulo']}
        - Requisitos: {', '.join(vaga['requisitos'])}
        - Descrição: {vaga['descricao']}
        
        Forneça uma análise concisa (máximo 3 frases) sobre:
        1. Quais habilidades do usuário são compatíveis
        2. Quais requisitos da vaga não são atendidos
        3. Recomendações específicas para aumentar a compatibilidade
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de compatibilidade entre candidatos e vagas de tecnologia."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro ao gerar análise de compatibilidade: {str(e)}")
        return "Não foi possível gerar a análise de compatibilidade."

@app.post("/usuario", response_model=UsuarioResponse)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = Usuario(nome=usuario.nome, habilidades=usuario.habilidades)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@app.get("/usuarios", response_model=List[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return usuarios

@app.post("/vagas/compativel", response_model=List[VagaResponse])
def buscar_vagas_compativeis(habilidades: List[str]):
    vagas_compativeis = []
    perfil_texto = " ".join(habilidades)
    
    for vaga in VAGAS_MOCK:
        compatibilidade = calcular_compatibilidade(habilidades, vaga["requisitos"])
        compatibilidade_semantica = calcular_similaridade_semantica(perfil_texto, vaga["descricao"])
        compativel_semantico = compatibilidade_semantica > 0.6
        
        vaga_response = dict(vaga)
        vaga_response["compatibilidade"] = compatibilidade
        vaga_response["compatibilidade_semantica"] = compatibilidade_semantica
        vaga_response["compativel_semantico"] = compativel_semantico
        vagas_compativeis.append(vaga_response)
    
    # Ordena por compatibilidade semântica (maior para menor)
    vagas_compativeis.sort(key=lambda x: x["compatibilidade_semantica"], reverse=True)
    return vagas_compativeis

@app.get("/vagas/{usuario_id}", response_model=VagasUsuarioResponse)
def buscar_vagas_por_usuario(usuario_id: int, db: Session = Depends(get_db)):
    try:
        # Busca o usuário
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        vagas_compativeis = []
        vagas_incompativeis = []
        perfil_texto = " ".join(usuario.habilidades)
        
        for vaga in VAGAS_MOCK:
            try:
                compatibilidade = calcular_compatibilidade(usuario.habilidades, vaga["requisitos"])
                compatibilidade_semantica = calcular_similaridade_semantica(perfil_texto, vaga["descricao"])
                compativel_semantico = compatibilidade_semantica > 0.6
                analise_texto = analisar_compatibilidade(usuario.habilidades, vaga)
                
                vaga_response = dict(vaga)
                vaga_response["compatibilidade"] = compatibilidade
                vaga_response["compatibilidade_semantica"] = compatibilidade_semantica
                vaga_response["compativel_semantico"] = compativel_semantico
                vaga_response["analise_texto"] = analise_texto
                
                if compatibilidade >= 70 or compativel_semantico:
                    vagas_compativeis.append(vaga_response)
                else:
                    vagas_incompativeis.append(vaga_response)
            except Exception as e:
                print(f"Erro ao processar vaga {vaga['id']}: {str(e)}")
                continue
        
        # Ordena ambas as listas por compatibilidade semântica (maior para menor)
        vagas_compativeis.sort(key=lambda x: x["compatibilidade_semantica"], reverse=True)
        vagas_incompativeis.sort(key=lambda x: x["compatibilidade_semantica"], reverse=True)
        
        # Salva os resultados no banco
        try:
            salvar_matches(db, usuario_id, vagas_compativeis, vagas_incompativeis)
        except Exception as e:
            print(f"Erro ao salvar matches: {str(e)}")
        
        return {
            "vagas_compativeis": vagas_compativeis,
            "vagas_incompativeis": vagas_incompativeis
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Erro ao buscar vagas: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Erro interno ao processar vagas")

@app.get("/matches/{usuario_id}", response_model=List[MatchVagaResponse])
def listar_matches_usuario(usuario_id: int, db: Session = Depends(get_db)):
    matches = db.query(MatchVaga).filter(MatchVaga.usuario_id == usuario_id).all()
    return matches

@app.get("/vagas/codante", response_model=List[JobResponse])
async def buscar_vagas_codante(keyword: Optional[str] = None):
    raise HTTPException(status_code=501, detail="Endpoint temporariamente indisponível")

@app.get("/vagas/github", response_model=List[PublicJobResponse])
async def buscar_vagas_github(descricao: str = "developer", localidade: str = "remote"):
    try:
        url = f"https://jobs.github.com/positions.json?description={descricao}&location={localidade}"
        response = requests.get(url)
        response.raise_for_status()
        jobs_data = response.json()
        jobs = []
        tech_keywords = [
            "Python", "JavaScript", "Java", "C#", "C++", "Ruby", "PHP",
            "React", "Angular", "Vue", "Node.js", "Django", "Flask",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "SQL",
            "MongoDB", "PostgreSQL", "MySQL", "Redis", "Git"
        ]
        for job in jobs_data:
            descricao = job.get("description", "")
            requisitos = [k for k in tech_keywords if k.lower() in descricao.lower()]
            jobs.append(PublicJobResponse(
                nome=job.get("title", ""),
                empresa=job.get("company", ""),
                localidade=job.get("location", ""),
                descricao=descricao,
                requisitos=requisitos
            ))
        return jobs[:100]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar vagas do GitHub Jobs: {str(e)}")

@app.get("/vagas/reed", response_model=List[PublicJobResponse])
async def buscar_vagas_reed(descricao: str = "developer", localidade: str = "remote"):
    try:
        url = f"https://www.reed.co.uk/api/1.0/search?keywords={descricao}&location={localidade}&distanceFromLocation=100"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        jobs_data = response.json().get("results", [])
        jobs = []
        tech_keywords = [
            "Python", "JavaScript", "Java", "C#", "C++", "Ruby", "PHP",
            "React", "Angular", "Vue", "Node.js", "Django", "Flask",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "SQL",
            "MongoDB", "PostgreSQL", "MySQL", "Redis", "Git"
        ]
        for job in jobs_data:
            descricao = job.get("jobDescription", "")
            requisitos = [k for k in tech_keywords if k.lower() in descricao.lower()]
            jobs.append(PublicJobResponse(
                nome=job.get("jobTitle", ""),
                empresa=job.get("employerName", ""),
                localidade=job.get("locationName", ""),
                descricao=descricao,
                requisitos=requisitos
            ))
        return jobs[:100]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar vagas do Reed: {str(e)}")

@app.get("/vagas/adzuna", response_model=List[PublicJobResponse])
async def buscar_vagas_adzuna(descricao: str = "developer", localidade: str = "remote"):
    try:
        url = f"https://api.adzuna.com/v1/api/jobs/gb/search/1?what={descricao}&where={localidade}&content-type=application/json"
        response = requests.get(url)
        response.raise_for_status()
        jobs_data = response.json().get("results", [])
        jobs = []
        tech_keywords = [
            "Python", "JavaScript", "Java", "C#", "C++", "Ruby", "PHP",
            "React", "Angular", "Vue", "Node.js", "Django", "Flask",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "SQL",
            "MongoDB", "PostgreSQL", "MySQL", "Redis", "Git"
        ]
        for job in jobs_data:
            descricao = job.get("description", "")
            requisitos = [k for k in tech_keywords if k.lower() in descricao.lower()]
            jobs.append(PublicJobResponse(
                nome=job.get("title", ""),
                empresa=job.get("company", {}).get("display_name", ""),
                localidade=job.get("location", {}).get("display_name", ""),
                descricao=descricao,
                requisitos=requisitos
            ))
        return jobs[:100]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar vagas do Adzuna: {str(e)}")

def extrair_requisitos_tecnicos(descricao: str) -> List[str]:
    tech_keywords = [
        "Python", "JavaScript", "Java", "C#", "C++", "Ruby", "PHP",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "SQL",
        "MongoDB", "PostgreSQL", "MySQL", "Redis", "Git",
        "TypeScript", "GraphQL", "REST", "API", "Microservices",
        "CI/CD", "Jenkins", "Terraform", "Ansible", "Linux",
        "Agile", "Scrum", "Jira", "Confluence", "DevOps"
    ]
    
    requisitos = []
    descricao_lower = descricao.lower()
    
    for keyword in tech_keywords:
        if keyword.lower() in descricao_lower:
            requisitos.append(keyword)
    
    return list(set(requisitos))  # Remove duplicatas

async def coletar_e_salvar_vagas(db: Session):
    try:
        # Coleta do GitHub Jobs
        url_github = "https://jobs.github.com/positions.json?description=developer&location=remote"
        response_github = requests.get(url_github)
        response_github.raise_for_status()
        jobs_github = response_github.json()

        # Coleta do Reed
        url_reed = "https://www.reed.co.uk/api/1.0/search?keywords=developer&location=remote&distanceFromLocation=100"
        headers = {"Accept": "application/json"}
        response_reed = requests.get(url_reed, headers=headers)
        response_reed.raise_for_status()
        jobs_reed = response_reed.json().get("results", [])

        # Coleta do Adzuna
        url_adzuna = "https://api.adzuna.com/v1/api/jobs/gb/search/1?what=developer&where=remote&content-type=application/json"
        response_adzuna = requests.get(url_adzuna)
        response_adzuna.raise_for_status()
        jobs_adzuna = response_adzuna.json().get("results", [])

        # Processa e salva vagas do GitHub
        for job in jobs_github:
            descricao = job.get("description", "")
            requisitos = extrair_requisitos_tecnicos(descricao)
            vaga = Vaga(
                titulo=job.get("title", ""),
                empresa=job.get("company", ""),
                descricao=descricao,
                requisitos=requisitos,
                local=job.get("location", ""),
                url_aplicacao=job.get("url", "")
            )
            db.add(vaga)

        # Processa e salva vagas do Reed
        for job in jobs_reed:
            descricao = job.get("jobDescription", "")
            requisitos = extrair_requisitos_tecnicos(descricao)
            vaga = Vaga(
                titulo=job.get("jobTitle", ""),
                empresa=job.get("employerName", ""),
                descricao=descricao,
                requisitos=requisitos,
                local=job.get("locationName", ""),
                url_aplicacao=job.get("jobUrl", "")
            )
            db.add(vaga)

        # Processa e salva vagas do Adzuna
        for job in jobs_adzuna:
            descricao = job.get("description", "")
            requisitos = extrair_requisitos_tecnicos(descricao)
            vaga = Vaga(
                titulo=job.get("title", ""),
                empresa=job.get("company", {}).get("display_name", ""),
                descricao=descricao,
                requisitos=requisitos,
                local=job.get("location", {}).get("display_name", ""),
                url_aplicacao=job.get("redirect_url", "")
            )
            db.add(vaga)

        # Commit das alterações
        db.commit()
        return {"message": "Vagas coletadas e salvas com sucesso!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao coletar e salvar vagas: {str(e)}")

@app.post("/vagas/coletar")
async def coletar_vagas(db: Session = Depends(get_db)):
    return await coletar_e_salvar_vagas(db)

def analisar_habilidades(habilidades_usuario: List[str], requisitos_vaga: List[str]) -> AnaliseHabilidades:
    # Normaliza as strings (remove espaços, converte para minúsculo)
    habilidades_norm = [h.strip().lower() for h in habilidades_usuario]
    requisitos_norm = [r.strip().lower() for r in requisitos_vaga]
    
    # Encontra matches e gaps
    matches = []
    gaps = []
    
    for req in requisitos_norm:
        # Verifica se o requisito está nas habilidades do usuário
        if any(req in hab for hab in habilidades_norm):
            # Encontra a habilidade original (com case original)
            for hab in habilidades_usuario:
                if req in hab.lower():
                    matches.append(hab)
                    break
        else:
            # Encontra o requisito original (com case original)
            for req_orig in requisitos_vaga:
                if req == req_orig.lower():
                    gaps.append(req_orig)
                    break
    
    # Gera sugestões de estudo
    sugestoes = []
    niveis = {
        "Python": "intermediário",
        "JavaScript": "intermediário",
        "Java": "intermediário",
        "C#": "intermediário",
        "C++": "avançado",
        "Ruby": "intermediário",
        "PHP": "intermediário",
        "React": "intermediário",
        "Angular": "intermediário",
        "Vue": "intermediário",
        "Node.js": "intermediário",
        "Django": "intermediário",
        "Flask": "intermediário",
        "AWS": "intermediário",
        "Azure": "intermediário",
        "GCP": "intermediário",
        "Docker": "intermediário",
        "Kubernetes": "avançado",
        "SQL": "intermediário",
        "MongoDB": "intermediário",
        "PostgreSQL": "intermediário",
        "MySQL": "intermediário",
        "Redis": "intermediário",
        "Git": "básico",
        "TypeScript": "intermediário",
        "GraphQL": "intermediário",
        "REST": "intermediário",
        "API": "intermediário",
        "Microservices": "avançado",
        "CI/CD": "intermediário",
        "Jenkins": "intermediário",
        "Terraform": "intermediário",
        "Ansible": "intermediário",
        "Linux": "intermediário",
        "Agile": "básico",
        "Scrum": "básico",
        "Jira": "básico",
        "Confluence": "básico",
        "DevOps": "intermediário"
    }
    
    for gap in gaps:
        nivel = niveis.get(gap, "intermediário")
        sugestoes.append(f"Estudar {gap} (nível {nivel})")
    
    return AnaliseHabilidades(
        match=list(set(matches)),  # Remove duplicatas
        gaps=list(set(gaps)),      # Remove duplicatas
        sugestao=sugestoes
    )

@app.post("/analise/habilidades", response_model=AnaliseHabilidades)
async def analisar_compatibilidade_habilidades(habilidades: List[str], requisitos: List[str]):
    return analisar_habilidades(habilidades, requisitos)

async def buscar_trilha_universidade_livre(tecnologia: str) -> Optional[dict]:
    """
    Busca trilhas no repositório Universidade-Livre.
    """
    try:
        # Simula busca no repositório
        trilhas = {
            "React": {
                "link": "https://github.com/Universidade-Livre/ciencia-da-computacao/blob/main/roadmap/frontend/react.md",
                "topicos": [
                    "Fundamentos do React",
                    "Componentes e Props",
                    "Hooks e Estado",
                    "Roteamento",
                    "Gerenciamento de Estado",
                    "Testes"
                ]
            },
            "Node.js": {
                "link": "https://github.com/Universidade-Livre/ciencia-da-computacao/blob/main/roadmap/backend/nodejs.md",
                "topicos": [
                    "Fundamentos do Node.js",
                    "Express.js",
                    "APIs RESTful",
                    "Banco de Dados",
                    "Autenticação",
                    "Deploy"
                ]
            },
            "Docker": {
                "link": "https://github.com/Universidade-Livre/ciencia-da-computacao/blob/main/roadmap/devops/docker.md",
                "topicos": [
                    "Conceitos Básicos",
                    "Containers",
                    "Imagens",
                    "Docker Compose",
                    "Networking",
                    "Volumes"
                ]
            }
        }
        
        return trilhas.get(tecnologia)
    except Exception as e:
        print(f"Erro ao buscar trilha na Universidade-Livre: {str(e)}")
        return None

@app.post("/trilha", response_model=TrilhaResponse)
async def criar_trilha(request: TrilhaRequest, db: Session = Depends(get_db)):
    """
    Cria ou recupera uma trilha de estudos para o usuário.
    """
    # Verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == request.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Lista para armazenar as trilhas (existentes ou novas)
    trilhas_finais = []
    
    # Para cada gap, verifica se já existe trilha salva
    for gap in request.gaps:
        # Busca trilha existente para esta tecnologia
        trilha_existente = db.query(Trilha).filter(
            Trilha.usuario_id == request.usuario_id,
            Trilha.tecnologia == gap
        ).first()
        
        if trilha_existente:
            # Se existe, adiciona à lista de retorno
            trilhas_finais.append(trilha_existente)
        else:
            # Se não existe, busca dados dos conteúdos externos
            conteudos = db.query(ConteudoExterno).filter(
                ConteudoExterno.tecnologia.ilike(gap)
            ).all()
            
            if conteudos:
                for conteudo in conteudos:
                    # Busca dados da roadmap
                    roadmap_data = get_roadmap_data(gap, db)
                    if roadmap_data:
                        # Salva trilha
                        trilha = Trilha(
                            usuario_id=request.usuario_id,
                            tecnologia=gap,
                            origem=conteudo.origem,
                            link=conteudo.link,
                            topicos=[etapa["topico"] for etapa in roadmap_data["etapas"]]
                        )
                        db.add(trilha)
                        trilhas_finais.append(trilha)
    
    try:
        # Commit apenas se houver novas trilhas para salvar
        if any(t.id is None for t in trilhas_finais):
            db.commit()
            # Atualiza os objetos com os IDs gerados
            for trilha in trilhas_finais:
                if trilha.id is None:
                    db.refresh(trilha)
        
        return TrilhaResponse(trilhas=[
            TopicoTrilha(
                tecnologia=t.tecnologia,
                origem=t.origem,
                link=t.link,
                topicos=t.topicos
            ) for t in trilhas_finais
        ])
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar trilhas: {str(e)}")

def gerar_resumo_trilha(tecnologias: List[str], gaps: List[str], roadmap_data: dict) -> str:
    """
    Gera um resumo textual da trilha de estudos usando OpenAI.
    
    Args:
        tecnologias (List[str]): Lista de tecnologias
        gaps (List[str]): Lista de gaps identificados
        roadmap_data (dict): Dados da roadmap para cada tecnologia
        
    Returns:
        str: Resumo textual da trilha de estudos
    """
    try:
        # Prepara o prompt com os dados da trilha
        prompt = f"""
        Gere um resumo conciso e motivador da trilha de estudos para as seguintes tecnologias:
        
        Tecnologias: {', '.join(tecnologias)}
        Gaps identificados: {', '.join(gaps)}
        
        Para cada tecnologia, temos os seguintes tópicos sugeridos:
        """
        
        for tech in tecnologias:
            if tech in roadmap_data:
                etapas = roadmap_data[tech]["etapas"]
                prompt += f"\n\n{tech}:\n"
                for etapa in etapas:
                    prompt += f"- {etapa['topico']} ({etapa['dificuldade']})\n"
        
        prompt += """
        Gere um texto fluido e natural que:
        1. Explique a ordem lógica de estudos
        2. Conecte os tópicos de forma coerente
        3. Mantenha um tom motivador
        4. Seja conciso (máximo 3 parágrafos)
        5. Use linguagem natural e conversacional
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um mentor de desenvolvimento de software experiente, especializado em criar trilhas de aprendizado personalizadas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro ao gerar resumo da trilha: {str(e)}")
        return "Não foi possível gerar o resumo da trilha de estudos."

@app.post("/trilha/resumo")
async def gerar_resumo_trilha_endpoint(request: TrilhaRequest, db: Session = Depends(get_db)):
    """
    Endpoint para gerar um resumo textual da trilha de estudos.
    """
    # Verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == request.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Coleta os dados da roadmap para cada tecnologia
    roadmap_data = {}
    for gap in request.gaps:
        # Busca conteúdos externos
        conteudos = db.query(ConteudoExterno).filter(
            ConteudoExterno.tecnologia.ilike(gap)
        ).all()
        
        if conteudos:
            data = get_roadmap_data(gap, db)
            if data:
                roadmap_data[gap] = data
    
    # Gera o resumo
    resumo = gerar_resumo_trilha(
        tecnologias=request.gaps,
        gaps=request.gaps,
        roadmap_data=roadmap_data
    )
    
    return {"resumo": resumo}

def get_roadmap_data(tecnologia: str, db: Session) -> dict:
    """
    Retorna os dados da roadmap para uma tecnologia específica.
    
    Args:
        tecnologia (str): Nome da tecnologia (ex: "React", "Node.js")
        db (Session): Sessão do banco de dados
        
    Returns:
        dict: Dicionário contendo o link da roadmap e as etapas ordenadas por dificuldade
    """
    # Busca conteúdo externo no banco
    conteudo = db.query(ConteudoExterno).filter(
        ConteudoExterno.tecnologia.ilike(tecnologia)
    ).first()
    
    if not conteudo:
        return None
    
    # Dicionário de palavras-chave para classificação de dificuldade
    dificuldade_keywords = {
        "basico": [
            "basics", "fundamentals", "introduction", "overview", "getting started",
            "basico", "fundamentos", "introdução", "visão geral", "primeiros passos"
        ],
        "intermediario": [
            "advanced", "intermediate", "core", "essential", "main",
            "intermediário", "essencial", "principal", "núcleo"
        ],
        "avancado": [
            "expert", "master", "professional", "enterprise", "production",
            "avançado", "especialista", "profissional", "produção"
        ]
    }

    def get_dificuldade(topic: str) -> str:
        topic_lower = topic.lower()
        for nivel, keywords in dificuldade_keywords.items():
            if any(keyword in topic_lower for keyword in keywords):
                return nivel
        return "intermediario"  # default

    # Etapas padrão para cada tecnologia
    etapas_padrao = {
        "Frontend": [
            {"topico": "HTML & CSS", "dificuldade": "basico"},
            {"topico": "JavaScript", "dificuldade": "basico"},
            {"topico": "React", "dificuldade": "intermediario"},
            {"topico": "State Management", "dificuldade": "intermediario"},
            {"topico": "Testing", "dificuldade": "intermediario"},
            {"topico": "Performance", "dificuldade": "avancado"}
        ],
        "Backend": [
            {"topico": "Node.js", "dificuldade": "basico"},
            {"topico": "Express.js", "dificuldade": "intermediario"},
            {"topico": "Databases", "dificuldade": "intermediario"},
            {"topico": "Authentication", "dificuldade": "intermediario"},
            {"topico": "API Design", "dificuldade": "avancado"},
            {"topico": "Testing", "dificuldade": "intermediario"}
        ],
        "DevOps": [
            {"topico": "Linux", "dificuldade": "basico"},
            {"topico": "Docker", "dificuldade": "intermediario"},
            {"topico": "CI/CD", "dificuldade": "intermediario"},
            {"topico": "Kubernetes", "dificuldade": "avancado"},
            {"topico": "Monitoring", "dificuldade": "intermediario"},
            {"topico": "Security", "dificuldade": "avancado"}
        ]
    }
    
    # Retorna os dados formatados
    return {
        "link": conteudo.link,
        "etapas": etapas_padrao.get(tecnologia, [])
    }

# Função para popular a tabela de conteúdos externos
def popular_conteudos_externos(db: Session):
    conteudos = [
        {
            "tecnologia": "Frontend",
            "origem": "Universidade-Livre",
            "link": "https://github.com/Universidade-Livre/fullstack",
            "fonte_nome": "Universidade-Livre Frontend"
        },
        {
            "tecnologia": "Backend",
            "origem": "Universidade-Livre",
            "link": "https://github.com/Universidade-Livre/backend",
            "fonte_nome": "Universidade-Livre Backend"
        },
        {
            "tecnologia": "DevOps",
            "origem": "Universidade-Livre",
            "link": "https://github.com/Universidade-Livre/devops",
            "fonte_nome": "Universidade-Livre DevOps"
        },
        {
            "tecnologia": "Frontend",
            "origem": "roadmap.sh",
            "link": "https://roadmap.sh/frontend",
            "fonte_nome": "Frontend Developer Roadmap"
        },
        {
            "tecnologia": "Backend",
            "origem": "roadmap.sh",
            "link": "https://roadmap.sh/backend",
            "fonte_nome": "Backend Developer Roadmap"
        },
        {
            "tecnologia": "DevOps",
            "origem": "roadmap.sh",
            "link": "https://roadmap.sh/devops",
            "fonte_nome": "DevOps Roadmap"
        }
    ]
    
    for conteudo in conteudos:
        # Verifica se já existe
        existente = db.query(ConteudoExterno).filter(
            ConteudoExterno.tecnologia == conteudo["tecnologia"],
            ConteudoExterno.origem == conteudo["origem"]
        ).first()
        
        if not existente:
            novo_conteudo = ConteudoExterno(**conteudo)
            db.add(novo_conteudo)
    
    db.commit()

# Popula a tabela ao iniciar a aplicação
with SessionLocal() as db:
    popular_conteudos_externos(db)

@app.get("/tecnologia/{nome}/links")
async def get_links_tecnologia(nome: str, db: Session = Depends(get_db)):
    """
    Retorna os links da roadmap.sh e Universidade-Livre para uma tecnologia.
    """
    # Busca todos os conteúdos externos para a tecnologia
    conteudos = db.query(ConteudoExterno).filter(
        ConteudoExterno.tecnologia.ilike(nome)
    ).all()
    
    if not conteudos:
        raise HTTPException(status_code=404, detail="Tecnologia não encontrada")
    
    # Formata a resposta
    links = {}
    for conteudo in conteudos:
        links[conteudo.origem] = {
            "link": conteudo.link,
            "fonte_nome": conteudo.fonte_nome
        }
    
    return {
        "tecnologia": nome,
        "links": links
    }

@app.get("/trilha/{usuario_id}", response_model=TrilhaUsuarioResponse)
async def buscar_trilhas_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """
    Busca todas as trilhas salvas para um usuário específico.
    """
    # Verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Busca todas as trilhas do usuário
    trilhas = db.query(Trilha).filter(Trilha.usuario_id == usuario_id).all()
    
    # Converte para o formato de resposta
    trilhas_response = []
    for trilha in trilhas:
        # Busca informações adicionais do conteúdo externo
        conteudo = db.query(ConteudoExterno).filter(
            ConteudoExterno.tecnologia == trilha.tecnologia,
            ConteudoExterno.origem == trilha.origem
        ).first()
        
        trilhas_response.append(TopicoTrilha(
            tecnologia=trilha.tecnologia,
            origem=trilha.origem,
            link=trilha.link,
            topicos=trilha.topicos
        ))
    
    return TrilhaUsuarioResponse(
        usuario_id=usuario_id,
        trilhas=trilhas_response
    )

@app.post("/trilha/recursos")
async def gerar_recursos_endpoint(request: TrilhaRequest, db: Session = Depends(get_db)):
    """
    Endpoint para gerar recursos sugeridos para cada tecnologia.
    """
    # Verifica se o usuário existe
    usuario = db.query(Usuario).filter(Usuario.id == request.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Gera recursos para cada gap
    recursos = []
    for gap in request.gaps:
        # Busca conteúdos externos
        conteudos = db.query(ConteudoExterno).filter(
            ConteudoExterno.tecnologia.ilike(gap)
        ).all()
        
        if conteudos:
            recursos_sugeridos = []
            for conteudo in conteudos:
                recursos_sugeridos.append({
                    "titulo": conteudo.fonte_nome,
                    "plataforma": conteudo.origem,
                    "link": conteudo.link
                })
            
            recursos.append({
                "tecnologia": gap,
                "recursos_sugeridos": recursos_sugeridos
            })
    
    return {"recursos": recursos} 