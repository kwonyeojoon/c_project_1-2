# 베이스 이미지로 Python 3.10-slim 사용..
FROM python:3.10-slim

# 패키지 설치 및 업데이트
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        make \
        curl \
        git \
        libcurl4-openssl-dev \
        libcjson-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# cJSON 라이브러리 클론 및 빌드
RUN git clone https://github.com/DaveGamble/cJSON.git /cJSON && \
    cd /cJSON && \
    make && \
    make install && \
    rm -rf /cJSON

# 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 모든 내용을 /app으로 복사
COPY . /app/

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# Flask 앱 실행
CMD ["python", "app.py"]
