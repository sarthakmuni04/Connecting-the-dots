# Use an amd64-compatible PyTorch image with CUDA support for 8-bit quant
FROM --platform=linux/amd64 pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY hierarchical_headings_extractor.py .

ENTRYPOINT ["python", "main.py"]
CMD []
