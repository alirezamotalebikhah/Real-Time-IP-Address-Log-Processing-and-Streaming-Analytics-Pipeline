# ---- Stage 1: Builder ----
# This stage builds a virtual environment with our dependencies.
FROM python:3.12-slim as builder

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip

# Install dependencies
RUN pip install confluent-kafka


# ---- Stage 2: Final Image ----
# This is our lean production image.
FROM python:3.12-slim

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code
COPY producer.py .

# Create a non-root user and switch to it
RUN useradd --create-home appuser
USER appuser

# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Command to run the application
CMD [ "python3", "producer.py" ]
