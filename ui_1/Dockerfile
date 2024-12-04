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

# ui_1 폴더의 내용을 /app 디렉토리로 복사
COPY ./ui_1 /app/

# /app/ui_1 디렉토리로 이동
WORKDIR /app/ui_1

# requirements.txt를 현재 디렉토리로 복사
COPY ./requirements.txt ./requirements.txt

# 필요한 Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# Flask 앱 실행
CMD ["python", "app.py"]  # app.py가 main 파일이라면 실행
