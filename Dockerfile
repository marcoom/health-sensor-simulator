FROM tiangolo/uvicorn-gunicorn:python3.11

# Set configurable environment variables with defaults
ENV FASTAPI_HOST=0.0.0.0
ENV FASTAPI_PORT=8000
ENV STREAMLIT_HOST=0.0.0.0
ENV STREAMLIT_PORT=8501
ENV LOG_LEVEL=INFO
ENV ALARM_ENDPOINT_URL=http://localhost:8080/alerts

# Install only production dependencies
COPY ./requirements/base.txt .
RUN pip install -r base.txt

# Copy only the src folder with required code
COPY ./src /app/src
WORKDIR /app

# Expose configurable ports
EXPOSE $FASTAPI_PORT $STREAMLIT_PORT

# Use our integrated launcher as entrypoint
CMD ["python", "-m", "src.main"]