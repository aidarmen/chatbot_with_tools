# Use a minimal Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system build tools (in case any dependency needs compiling)
# RUN apt-get update && apt-get install -y build-essential gcc

# Install uv (fast package manager)
RUN pip install --upgrade pip && pip install uv 


COPY requirements.txt .

# Install dependencies with uv
RUN uv pip install -r requirements.txt || pip install -r requirements.txt

COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
