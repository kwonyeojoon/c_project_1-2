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

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 먼저 복사하여 캐싱 활용
COPY requirements.txt /app/

# pip 업그레이드 및 Python 패키지 설치
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# 나머지 애플리케이션 파일 복사
COPY . /app/

# C 프로그램 빌드
# db_manager 빌드
RUN cd ui_1/db_manager && make

# transit 빌드
RUN cd ui_1/transit && make

# C 프로그램에 실행 권한 부여 및 권한 확인
RUN chmod +x ui_1/db_manager/db_manager \
    ui_1/transit/get_coordinates \
    ui_1/transit/get_route_info && \
    ls -l ui_1/db_manager/db_manager && \
    ls -l ui_1/transit/get_coordinates && \
    ls -l ui_1/transit/get_route_info

# 포트 설정 (Render는 PORT 환경 변수를 자동으로 설정하므로 이를 사용)
EXPOSE $PORT

# CMD 설정: Exec form 사용
CMD ["python", "-m", "gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "app:app"]
