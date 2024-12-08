# 베이스 이미지 설정
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

# 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 모든 파일을 /app으로 복사
COPY . /app/

# pip 업그레이드 및 Python 패키지 설치
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# C 바이너리 컴파일
# db_manager 컴파일
RUN cd db_manager && \
    gcc -o db_manager db_manager.c

# transit 프로그램 컴파일
RUN cd transit && \
    gcc -o get_coordinates get_coordinates.c && \
    gcc -o get_route_info get_route_info.c

# 실행 권한 부여
RUN chmod +x db_manager/db_manager transit/get_coordinates transit/get_route_info

# CMD를 gunicorn 실행 명령어로 설정
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
