# Usamos uma imagem base leve do Python
FROM python:3.10-slim

# Define variáveis de ambiente para o Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala as dependências do sistema
# dos2unix: para converter finais de linha de Windows para Unix
RUN apt-get update && apt-get install -y build-essential libpq-dev netcat-openbsd dos2unix

# Copia APENAS o arquivo de dependências primeiro.
# Isso aproveita o cache do Docker. Se este arquivo não mudar,
# o Docker não reinstalará as dependências em todos os builds.
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Agora, copia o RESTANTE do código da aplicação.
COPY . .

# --- CORREÇÃO PERMANENTE APLICADA NA ORDEM CORRETA ---
# Primeiro, garantimos que o entrypoint.sh tenha os finais de linha corretos.
RUN dos2unix /app/entrypoint.sh

# Depois, damos permissão de execução ao script já corrigido.
RUN chmod +x /app/entrypoint.sh

# Expõe a porta que a aplicação vai rodar
EXPOSE 8000

# Define o entrypoint para ser o nosso script.
ENTRYPOINT ["/app/entrypoint.sh"]