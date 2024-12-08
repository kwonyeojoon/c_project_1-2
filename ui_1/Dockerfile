FROM python:3.10-slim

# 필수 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libcurl4-openssl-dev \
        libcjson-dev \
        pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# cJSON 빌드 및 설치
RUN git clone https://github.com/DaveGamble/cJSON.git /cJSON && \
    cd /cJSON && \
    make && \
    make install && \
    rm -rf /cJSON

WORKDIR /app

COPY . /app/

# pip 업그레이드 및 Python 패키지 설치
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# C 프로그램에 실행 권한 부여
RUN chmod +x /app/db_manager/db_manager \
    /app/transit/get_coordinates \
    /app/db_manager/get_route_info

# 포트 설정
EXPOSE $PORT

# CMD 설정: Exec form 사용
CMD ["python", "-m", "gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "app:app"]
