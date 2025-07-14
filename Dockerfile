# Dockerfile

FROM python:3.12-slim

# Set the working directory inside the container to match your repo name
WORKDIR /inthum

# Install system dependencies (optional depending on your app)
RUN apt-get update && apt-get install -y \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the full repo into the container
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit when the container starts
CMD ["streamlit", "run", "app.py"]