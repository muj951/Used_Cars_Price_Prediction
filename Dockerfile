# 1. Base Image: Start with a lightweight version of Python
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy dependencies first (This speeds up re-builds!)
COPY requirements.txt .

# 4. Install the libraries
# We add --no-cache-dir to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your actual project code into the container
COPY . .

# 6. Expose the port Streamlit runs on
EXPOSE 8501

# 7. The Command to run when the container starts
CMD ["streamlit", "run", "app.py", "--server.address=127.0.0.1"]