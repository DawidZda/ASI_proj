FROM python:3.12-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory to /src
WORKDIR /src

# Copy requirements files
COPY requirements/base.txt requirements/prod.txt ./requirements/

# Install production dependencies with increased timeout and retries
RUN pip install --no-cache-dir --timeout 100 --retries 10 -r requirements/prod.txt || \
    pip install --no-cache-dir --timeout 100 --retries 10 -r requirements/prod.txt || \
    pip install --no-cache-dir --timeout 100 --retries 10 -r requirements/prod.txt

# Install FastAPI and uvicorn (also with increased reliability)
RUN pip install --no-cache-dir --timeout 100 --retries 10 fastapi uvicorn

# Copy only the contents of src directory, not the directory itself
COPY src/ ./
COPY tools/unzipped_model/ /unzipped_model/
COPY credentials/ /credentials/

# Set environment variables
ENV GOOGLE_CREDENTIALS=/credentials/asiprojekt.json
ENV UPLOAD_MODEL=false
ENV MODEL_PATH=/unzipped_model
ENV PYTHONPATH=/src

# Expose port for FastAPI
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]