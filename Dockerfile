
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1



# 1. Install system dependencies
RUN apt-get update && apt-get install -y \
    curl gnupg python3 python3-pip unzip\
    && rm -rf /var/lib/apt/lists/*


# Install minimal tools needed to add the repo
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg apt-transport-https ca-certificates\
 && rm -rf /var/lib/apt/lists/*

# Add Jellyfin APT key and sources file
RUN set -eux; \
    curl -fsSL https://repo.jellyfin.org/ubuntu/jellyfin_team.gpg.key \
      | gpg --dearmor > /usr/share/keyrings/jellyfin.gpg; \
    printf 'deb [signed-by=/usr/share/keyrings/jellyfin.gpg] https://repo.jellyfin.org/ubuntu noble main\n' \
      > /etc/apt/sources.list.d/jellyfin.list

# Install jellyfin-ffmpeg6
RUN apt-get update \
 && apt-get install -y --no-install-recommends jellyfin-ffmpeg6 \
 && rm -rf /var/lib/apt/lists/*

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
