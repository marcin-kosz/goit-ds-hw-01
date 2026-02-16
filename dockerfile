FROM python:3.13.9-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir poetry
RUN poetry install --no-root
CMD ["poetry", "run", "python", "task_ds_1_1.py"]