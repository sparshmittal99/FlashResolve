# 1. Use the official lightweight Python image
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy our requirements file first
COPY requirements.txt .

# 4. Install the Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of our code into the container
COPY . .

# 6. Command to run when the container starts
CMD ["python", "-u", "main.py"]