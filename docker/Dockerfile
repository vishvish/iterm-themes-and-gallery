FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir Pillow==10.4.0

WORKDIR /app
COPY generate_previews.py .

# Mount your Color Presets directory to /data/presets
# Output previews will be written to /data/previews
VOLUME ["/data/presets", "/data/previews"]

ENTRYPOINT ["python3", "generate_previews.py", "/data/presets", "/data/previews"]
