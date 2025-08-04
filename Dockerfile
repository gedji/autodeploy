FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set Python path to handle imports correctly
ENV PYTHONPATH=/workspace/src

CMD ["sleep", "infinity"]