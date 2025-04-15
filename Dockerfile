FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY .streamlit /app/.streamlit

EXPOSE 8501

CMD ["streamlit", "run", "your_app_name.py"]

# Reminder: Create a .dockerignore file to exclude unnecessary files and directories,
# such as your local .git directory, virtual environment, and potentially the
# .streamlit/secrets.toml file if you are managing secrets differently in Docker.