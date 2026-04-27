FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

COPY "GameScope AI/requirements.txt" /app/requirements.txt
COPY "GameScope AI/GameScope_AI/requirements.txt" /app/GameScope_AI/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY "GameScope AI" /app

EXPOSE 7860

CMD ["sh", "-c", "streamlit run GameScope_AI/app.py --server.address=0.0.0.0 --server.port=${PORT:-7860}"]
