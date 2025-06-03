# Stage 1: Base Build stage
FROM python:3.13-slim AS builder

#Create the app directory
RUN mkdir /app

# Set the working directory
WORKDIR /app

# Set the environment variables to optimize python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1
ENV PYTHONPATH=/app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip 

# Copy the requirements file first
COPY requirements.txt /app/

#Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Download en_core for spacy
RUN python -m spacy download en_core_web_sm

COPY . /app/

# Stage 2: Production stage
FROM python:3.13-slim

RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app
# Copy the python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

#Copy application code
COPY --from=builder --chown=appuser:appuser /app/ /app/

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1 
ENV PYTHONPATH=/app
 
# Switch to non-root user
USER appuser

# Set the working directory
WORKDIR /app/backend

# Expose the application port
EXPOSE 8000

# Start the application using gunicorn
CMD ["gunicorn","--bind","0.0.0.0:8000","--workers","3","SMART.wsgi:application"]
