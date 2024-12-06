# 베이스 이미지로 Python 3.10-slim 사용..
FROM python:3.10-slim

# C 컴파일러 및 필수 개발 도구 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libcurl4-openssl-dev \
        libcjson-dev \
        pkg-config \
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

# PATH 환경 변수에 /usr/local/bin 추가 (gunicorn 설치 경로 포함)
ENV PATH="/usr/local/bin:${PATH}"

# pip 업그레이드 및 Python 패키지 설치
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# Gunicorn 설치 확인
RUN gunicorn --version && which gunicorn

# 프로덕션용 WSGI 서버 실행
# 여기서 gunicorn을 직접 호출하기보다는 python -m gunicorn으로 시도해보세요.
CMD ["python", "-m", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
