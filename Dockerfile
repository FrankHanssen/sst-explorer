FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

COPY . .

ENV PORT=8080

CMD ["sh", "-c", "uv run streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port ${PORT}"]