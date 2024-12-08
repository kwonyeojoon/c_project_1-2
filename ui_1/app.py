from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from dotenv import load_dotenv
import subprocess
import os
import logging

# 📝 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key')  # 환경 변수로 SECRET_KEY 설정

# 현재 작업 디렉토리 설정
PROJECT_ROOT = os.getcwd()
TRANSIT_DIR = os.path.join(PROJECT_ROOT, "transit")
DB_MANAGER_DIR = os.path.join(PROJECT_ROOT, "db_manager")

# C 바이너리 경로 설정
db_manager_path = os.path.abspath(os.path.join(DB_MANAGER_DIR, "db_manager"))
get_coordinates_path = os.path.abspath(os.path.join(TRANSIT_DIR, "get_coordinates"))
get_route_info_path = os.path.abspath(os.path.join(TRANSIT_DIR, "get_route_info"))

logging.info(f"C 프로그램 경로 설정: db_manager_path='{db_manager_path}'")
logging.info(f"C 프로그램 경로 설정: get_coordinates_path='{get_coordinates_path}'")
logging.info(f"C 프로그램 경로 설정: get_route_info_path='{get_route_info_path}'")

# 추가 라우트: /ping
@app.route('/ping')
def ping():
    logging.info("Ping 라우트에 접속하였습니다.")
    return jsonify({'status': 'success', 'message': 'Pong!'})

# 홈 페이지 라우트
@app.route('/')
def home():
    logging.info("홈 페이지에 접속하였습니다.")
    return render_template('login.html')

# 회원가입 처리 라우트
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    logging.info(f"회원가입 시도: 사용자명='{username}'")

    try:
        # C 바이너리 파일 존재 여부 확인
        if not os.path.isfile(db_manager_path):
            logging.error(f"C 바이너리 파일을 찾을 수 없습니다: {db_manager_path}")
            return jsonify({'status': 'fail', 'message': '서버 오류: 실행 파일을 찾을 수 없습니다.'}), 500

        # C 바이너리 파일 실행 권한 확인
        if not os.access(db_manager_path, os.X_OK):
            logging.error(f"C 바이너리에 실행 권한이 없습니다: {db_manager_path}")
            return jsonify({'status': 'fail', 'message': '서버 오류: 실행 권한이 없습니다.'}), 500

        # C 프로그램 실행 준비 로그 (비밀번호는 마스킹)
        logging.info(f"C 프로그램 실행 준비: {db_manager_path}, 사용자명='{username}', 비밀번호='******'")

        # C 프로그램 실행
        result = subprocess.check_output([db_manager_path, 'register', username, password], text=True).strip()
        logging.info(f"회원가입 결과: {result}")

        if result == 'success':
            return jsonify({'status': 'success', 'message': '회원가입이 완료되었습니다!'})
        else:
            return jsonify({'status': 'fail', 'message': '이미 존재하는 아이디입니다.'})

    except subprocess.CalledProcessError as e:
        logging.error(f"회원가입 중 C 프로그램 오류: Return Code={e.returncode}, Output='{e.output.strip()}'")
        return jsonify({'status': 'fail', 'message': f'회원가입 중 오류가 발생했습니다: {e.output.strip()}'})
    except Exception as e:
        logging.error(f"회원가입 중 예외 발생: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'회원가입 중 예상치 못한 오류가 발생했습니다: {str(e)}'})

# 로그인 처리 라우트
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    logging.info(f"로그인 시도: 사용자명='{username}'")

    try:
        # C 바이너리 파일 존재 여부 확인
        if not os.path.isfile(db_manager_path):
            logging.error(f"C 바이너리 파일을 찾을 수 없습니다: {db_manager_path}")
            return jsonify({'status': 'fail', 'message': '서버 오류: 실행 파일을 찾을 수 없습니다.'}), 500

        # C 바이너리 파일 실행 권한 확인
        if not os.access(db_manager_path, os.X_OK):
            logging.error(f"C 바이너리에 실행 권한이 없습니다: {db_manager_path}")
            return jsonify({'status': 'fail', 'message': '서버 오류: 실행 권한이 없습니다.'}), 500

        # C 프로그램 실행 준비 로그 (비밀번호는 마스킹)
        logging.info(f"C 프로그램 실행 준비: {db_manager_path}, 사용자명='{username}', 비밀번호='******'")

        # C 프로그램 실행
        result = subprocess.check_output([db_manager_path, 'login', username, password], text=True).strip()
        logging.info(f"로그인 결과: {result}")

        if result == 'success':
            session['username'] = username
            return jsonify({'status': 'success', 'redirect': url_for('calendar')})
        else:
            return jsonify({'status': 'fail', 'message': '아이디 또는 비밀번호가 잘못되었습니다.'})

    except subprocess.CalledProcessError as e:
        logging.error(f"로그인 중 C 프로그램 오류: Return Code={e.returncode}, Output='{e.output.strip()}'")
        return jsonify({'status': 'fail', 'message': f'로그인 중 오류가 발생했습니다: {e.output.strip()}'})
    except Exception as e:
        logging.error(f"로그인 중 예외 발생: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'로그인 중 예상치 못한 오류가 발생했습니다: {str(e)}'})

# 달력 페이지 라우트
@app.route('/calendar')
def calendar():
    if 'username' not in session:
        logging.warning("달력 페이지 접근 시 비로그인 상태")
        return redirect(url_for('home'))
    logging.info(f"달력 페이지에 접속: 사용자명='{session['username']}'")
    return render_template('calendar.html')

# 타임라인 이벤트 저장 라우트
@app.route('/saveTimeline', methods=['POST'])
def save_timeline():
    if 'username' not in session:
        logging.warning("이벤트 저장 시 비로그인 상태")
        return jsonify({'status': 'fail', 'message': '로그인이 필요합니다.'}), 401

    username = session['username']
    data = request.get_json()
    title = str(data.get('title', '')).strip()
    date = str(data.get('date', '')).strip()
    start_time = str(data.get('startTime', '')).strip()
    end_time = str(data.get('endTime', '')).strip()
    trans_time = str(data.get('transTime', '')).strip()

    logging.info(f"이벤트 저장 시도: 사용자명='{username}', 제목='{title}', 날짜='{date}'")

    try:
        cmd = [
            db_manager_path,
            'save_event',
            username,
            date,
            title,
            start_time,
            end_time,
            trans_time
        ]

        logging.info(f"이벤트 저장 명령어 실행: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        logging.info(f"이벤트 저장 결과: Return Code={result.returncode}, Stdout='{result.stdout.strip()}', Stderr='{result.stderr.strip()}'")

        if result.returncode == 0 and result.stdout.strip() == 'success':
            return jsonify({'status': 'success'})
        else:
            error_output = result.stderr.strip() or result.stdout.strip()
            logging.error(f"이벤트 저장 실패: {error_output}")
            return jsonify({'status': 'fail', 'message': f'이벤트 저장에 실패했습니다: {error_output}'})
    except Exception as e:
        logging.error(f"이벤트 저장 중 예외 발생: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'이벤트 저장 중 오류가 발생했습니다: {str(e)}'})

# 타임라인 이벤트 로드 라우트
@app.route('/loadTimeline', methods=['POST'])
def load_timeline():
    if 'username' not in session:
        logging.warning("이벤트 로드 시 비로그인 상태")
        return jsonify({'status': 'fail', 'message': '로그인이 필요합니다.'}), 401

    username = session['username']
    data = request.get_json()
    date = str(data.get('sDate', '')).strip()

    logging.info(f"이벤트 로드 시도: 사용자명='{username}', 날짜='{date}'")

    try:
        cmd = [db_manager_path, 'load_events', username, date]
        logging.info(f"이벤트 로드 명령어 실행: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)

        logging.info(f"이벤트 로드 결과: Return Code={result.returncode}, Stdout='{result.stdout.strip()}', Stderr='{result.stderr.strip()}'")

        if result.returncode == 0:
            output = result.stdout.strip()
            lines = output.split('\n')
            if lines[0] == 'success':
                events = []
                for line in lines[1:]:
                    if line:
                        fields = line.strip().split(';')
                        if len(fields) == 3:
                            title, start_time, end_time = fields
                            is_transit = "이동시간" in title  # 이동시간 여부 확인
                            events.append({'title': title, 'start_time': start_time, 'end_time': end_time, 'is_transit': is_transit})
                logging.info(f"로드된 이벤트 수: {len(events)}")
                return jsonify({'status': 'success', 'events': events})
            else:
                logging.error("이벤트 로드 실패: C 프로그램에서 'success' 응답을 받지 못했습니다.")
                return jsonify({'status': 'fail', 'message': '이벤트 로드에 실패했습니다.'})
        else:
            error_output = result.stderr.strip() or result.stdout.strip()
            logging.error(f"이벤트 로드 실패: {error_output}")
            return jsonify({'status': 'fail', 'message': f'이벤트 로드에 실패했습니다: {error_output}'})
    except Exception as e:
        logging.error(f"이벤트 로드 중 예외 발생: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'이벤트 로드 중 오류가 발생했습니다: {str(e)}'})

# 진단용 라우트 추가: 바이너리 존재 여부 및 권한 확인
@app.route('/diagnose')
def diagnose():
    diagnostics = {}
    diagnostics['db_manager_exists'] = os.path.isfile(db_manager_path)
    diagnostics['db_manager_executable'] = os.access(db_manager_path, os.X_OK) if diagnostics['db_manager_exists'] else False
    diagnostics['get_coordinates_exists'] = os.path.isfile(get_coordinates_path)
    diagnostics['get_coordinates_executable'] = os.access(get_coordinates_path, os.X_OK) if diagnostics['get_coordinates_exists'] else False
    diagnostics['get_route_info_exists'] = os.path.isfile(get_route_info_path)
    diagnostics['get_route_info_executable'] = os.access(get_route_info_path, os.X_OK) if diagnostics['get_route_info_exists'] else False

    try:
        # 파일 권한 및 소유자 정보 확인 (ls -l 사용)
        db_manager_info = subprocess.check_output(['ls', '-l', db_manager_path], text=True).strip() if diagnostics['db_manager_exists'] else 'Not Found'
        get_coordinates_info = subprocess.check_output(['ls', '-l', get_coordinates_path], text=True).strip() if diagnostics['get_coordinates_exists'] else 'Not Found'
        get_route_info_info = subprocess.check_output(['ls', '-l', get_route_info_path], text=True).strip() if diagnostics['get_route_info_exists'] else 'Not Found'

        diagnostics['db_manager_info'] = db_manager_info
        diagnostics['get_coordinates_info'] = get_coordinates_info
        diagnostics['get_route_info_info'] = get_route_info_info
    except subprocess.CalledProcessError as e:
        diagnostics['error'] = f"ls 명령어 실행 중 오류: {e.output.strip()}"
    except Exception as e:
        diagnostics['error'] = str(e)

    return jsonify(diagnostics)

# 애플리케이션 실행
if __name__ == '__main__':
    logging.info("Flask 애플리케이션 시작")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # Render에서 설정한 PORT 사용
