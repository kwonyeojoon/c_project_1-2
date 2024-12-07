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

# cJSON 빌드
RUN git clone https://github.com/DaveGamble/cJSON.git /cJSON && \
    cd /cJSON && \
    make && \
    make install && \
    rm -rf /cJSON

WORKDIR /app

COPY . /app/

# pip 업그레이드 및 패키지 설치
RUN python -m pip install --upgrade pip && python -m pip install --no-cache-dir -r requirements.txt

# gunicorn 설치 확인용 (디버깅)
RUN python -m pip show gunicorn && gunicorn --version && which gunicorn || (echo "Gunicorn not found" && exit 1)

# 수정된 CMD 라인 (Shell form)
CMD python -m gunicorn -w 4 -b 0.0.0.0:$PORT app:app
