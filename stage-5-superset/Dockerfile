FROM apache/superset:master-lean
USER root
RUN . /app/.venv/bin/activate && uv pip install "clickhouse-connect>=1.8.0,<2.0"
USER superset