FROM python:3.14-slim

# make python logs visible in docker logs
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=student_service.settings.production

WORKDIR /app

RUN pip install --no-cache-dir uv==0.11.7

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

RUN useradd --create-home appuser && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD [".venv/bin/gunicorn", "student_service.wsgi:application", "--bind", "0.0.0.0:8000"]
