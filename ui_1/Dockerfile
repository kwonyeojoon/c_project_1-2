# 베이스 이미지 설정
FROM python:3.10-slim

# 필수 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \  # 빌드 필수 도구들 (gcc, make 등)
        curl \
        git \
        libcurl4-openssl-dev \
        libcjson-dev \
        pkg-config \
        sqlite3 \
        libsqlite3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 모든 파일을 /app으로 복사
COPY . /app/

# db_manager 빌드 (db_manager.c 파일 컴파일)
WORKDIR /app/db_manager
RUN gcc -o db_manager db_manager.c

# pip 업그레이드 및 Python 패키지 설치
WORKDIR /app
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# CMD를 python 모듈 형태로 실행하여 gunicorn 실행
CMD ["python", "-m", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
