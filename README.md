# API de Clima com Django e OpenWeatherMap

Este é um projeto de API REST simples, construído com Django e Django REST Framework, que fornece dados climáticos atuais para uma cidade específica.

O sistema utiliza a API do [OpenWeatherMap](https://openweathermap.org/api) para obter os dados, implementa um cache de 10 minutos com Redis para otimizar as consultas e mantém um histórico das últimas 10 cidades pesquisadas usando um banco de dados PostgreSQL.

## Funcionalidades

- Endpoint para buscar o clima atual por cidade.
- Cache de 10 minutos para as respostas da API, reduzindo a latência e o uso da API externa.
- Endpoint para visualizar o histórico das últimas 10 pesquisas.
- Rate limiting (limitação de taxa) para proteger a API contra uso excessivo (10 requisições por minuto por IP).

## Stack Tecnológica

- **Backend:** Python, Django, Django REST Framework
- **Banco de Dados:** PostgreSQL
- **Cache:** Redis
- **Containerização:** Docker, Docker Compose
- **Dependências Python:** `requests`, `python-dotenv`

## Requisitos

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Instalação e Execução

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd <nome-do-repositorio>
    ```

2.  **Crie o arquivo de variáveis de ambiente:**
    Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env`.
    ```bash
    cp .env.example .env
    ```
    Agora, **edite o arquivo `.env`** e substitua o valor de `OPENWEATHERMAP_API_KEY` pela sua chave de API obtida no site do OpenWeatherMap. Você pode obter uma chave gratuita após se registrar.

3.  **Construa e inicie os containers:**
    A partir da raiz do projeto, execute o seguinte comando. Ele fará o build da imagem do Django, baixará as imagens do Postgres e Redis, e iniciará todos os serviços.
    ```bash
    docker-compose up --build
    ```
    O servidor da aplicação estará rodando em `http://localhost:8000`. As migrações do banco de dados serão aplicadas automaticamente na inicialização.

## Uso da API

### 1. Obter Clima Atual

- **Endpoint:** `GET /api/weather/`
- **Parâmetros de Query:**
  - `city` (obrigatório): O nome da cidade.
- **Exemplo de Requisição com cURL:**
  ```bash
  curl -X GET "http://localhost:8000/api/weather/?city=London"
  ```
- **Exemplo de Resposta de Sucesso (200 OK):**
  ```json
  {
      "city": "London",
      "temperature_celsius": 15.7,
      "description": "céu limpo",
      "humidity": 78
  }
  ```
- **Exemplo de Resposta de Erro (404 Not Found):**
  ```json
  {
      "error": "Cidade não encontrada"
  }
  ```

### 2. Obter Histórico de Pesquisas

- **Endpoint:** `GET /api/history/`
- **Exemplo de Requisição com cURL:**
  ```bash
  curl -X GET "http://localhost:8000/api/history/"
  ```
- **Exemplo de Resposta de Sucesso (200 OK):**
  ```json
  [
      {
          "id": 2,
          "city": "Tokyo",
          "timestamp": "2023-10-27T18:35:10.123456Z",
          "data": {
              "city": "Tokyo",
              "humidity": 65,
              "description": "nuvens dispersas",
              "temperature_celsius": 22.5
          }
      },
      {
          "id": 1,
          "city": "London",
          "timestamp": "2023-10-27T18:35:05.987654Z",
          "data": {
              "city": "London",
              "humidity": 78,
              "description": "céu limpo",
              "temperature_celsius": 15.7
          }
      }
  ]
  ```

## Executando os Testes
```bash
docker-compose exec web python manage.py test weather

```