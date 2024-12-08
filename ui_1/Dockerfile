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

# requirements.txt 먼저 복사하여 캐싱 활용
COPY requirements.txt /app/

# pip 업그레이드 및 Python 패키지 설치
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# 나머지 애플리케이션 파일 복사
COPY . /app/

# C 프로그램 빌드 (필요 시)
RUN cd ui_1/db_manager && make && \
    cd ../transit && make

# 또는, Makefile이 없고 직접 컴파일하는 경우:
# RUN gcc -o /app/ui_1/db_manager/db_manager /app/ui_1/db_manager/db_manager.c && \
#     gcc -o /app/ui_1/transit/get_coordinates /app/ui_1/transit/get_coordinates.c && \
#     gcc -o /app/ui_1/transit/get_route_info /app/ui_1/transit/get_route_info.c

# C 프로그램에 실행 권한 부여 및 권한 확인
RUN chmod +x /app/ui_1/db_manager/db_manager \
    /app/ui_1/transit/get_coordinates \
    /app/ui_1/transit/get_route_info && \
    ls -l /app/ui_1/db_manager/db_manager && \
    ls -l /app/ui_1/transit/get_coordinates && \
    ls -l /app/ui_1/transit/get_route_info

# 포트 설정
EXPOSE $PORT

# CMD 설정: Exec form 사용
CMD ["python", "-m", "gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "app:app"]
