# 베이스 이미지로 Python 3.10-slim 사용
FROM python:3.10-slim

# 패키지 설치 및 업데이트
RUN apt-get update && \
    apt-get install -y \
    gcc \
    make \
    curl \
    git \
    libcurl4-openssl-dev \
    libcjson-dev \
    && apt-get clean

# cJSON 라이브러리 클론 및 빌드
RUN git clone https://github.com/DaveGamble/cJSON.git /cJSON && \
    cd /cJSON && \
    make && \
    make install

# cJSON 헤더 파일 위치 확인
RUN find / -name "cJSON.h"

# 작업 디렉토리 설정
WORKDIR /app

# 프로젝트 파일 복사
COPY ui_1 /app

# 필요한 라이브러리 설치 (requirements.txt가 존재하는 경우)
COPY requirements.txt ./  # requirements.txt 경로도 확인
RUN pip install --no-cache-dir -r requirements.txt

# Flask 앱 실행
CMD ["python", "app.py"]
