# Backend API - Sistema de Monitoramento de Piscicultura

## 📋 Sobre

Backend da aplicação de monitoramento de qualidade da água para piscicultura. API REST desenvolvida em Python com FastAPI para receber, processar e disponibilizar dados dos sensores instalados nos tanques.

## 🚀 Tecnologias

- **Python 3.10+**
- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL** - Banco de dados relacional
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI
- **Redis** - Cache e filas (opcional)
- **Docker** - Containerização

## ⚙️ Instalação e Configuração

### Pré-requisitos

- Python 3.10 ou superior
- PostgreSQL 14+
- pip ou poetry

### Configuração Local

1. **Clone o repositório**

```bash
git clone git@github.com:airtonm4/aqua-watch.git
cd aqua-watch
```

2. **Crie e ative um ambiente virtual**

**Usando venv:**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**Usando conda:**

```bash
conda create -n aqua-watch python=3.10
conda activate aqua-watch
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### Configuração com Docker

```bash
# Construir e iniciar os containers
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar os containers
docker-compose down
```

## 🔌 Documentação da API

### Documentação Interativa

Após iniciar o servidor, acesse a documentação automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=app tests/

# Executar testes específicos
pytest tests/test_sensors.py
```

## 📈 Performance

- Cache Redis para leituras frequentes
- Índices otimizados no banco de dados
- Paginação em listagens grandes
- Rate limiting para proteger a API

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📝 Licença

[LICENSE](LICENSE)

## 👥 Autor

**[Airton Martins Ferreira]** - [airton.atmi@gmail.com | airton.martins@estudante.ifgoiano.edu.br]

**[Artur Martins Ferreira]** - [artur.ferreira@estudante.ifgoiano.edu.br]

## 🔗 Links Relacionados

- [Frontend Repository](link-do-frontend)
- [Documentação Completa](link-da-documentacao)
- [Firmware dos Sensores](link-do-firmware)
