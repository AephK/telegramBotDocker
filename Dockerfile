FROM alpine:edge

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 1. Install system dependencies
RUN apk add --no-cache \
    curl gnupg python3 py3-pip unzip ca-certificates

# Add Jellyfin repository and key
RUN sed -i 's/^#\(.*community.*\)/\1/' /etc/apk/repositories
RUN apk update

# Install jellyfin-ffmpeg6
RUN apk add --no-cache jellyfin-ffmpeg

#Install JS library for yt-dlp
RUN curl -fsSL https://deno.land/install.sh | sh

# Symlink ffmpeg and ffprobe to PATH
RUN ln -s /usr/lib/jellyfin-ffmpeg/ffmpeg /usr/local/bin/ffmpeg \
 && ln -s /usr/lib/jellyfin-ffmpeg/ffprobe /usr/local/bin/ffprobe

# 3. Set working directory
WORKDIR /app

# 4. Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

# 5. Copy Python script
COPY botDocker.py /app/

# 6. Default command (adjust to your script name)
CMD ["python3", "botDocker.py"]
