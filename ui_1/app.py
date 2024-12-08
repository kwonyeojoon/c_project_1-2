import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from dotenv import load_dotenv
import subprocess
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')  # 환경 변수로 SECRET_KEY 설정

# 프로젝트 루트 디렉토리 설정
current_directory = os.getcwd()
PROJECT_ROOT = current_directory
TRANSIT_DIR = os.path.join(PROJECT_ROOT, "ui_1", "transit")
DB_DIR = os.path.join(PROJECT_ROOT, "ui_1", "db_manager")

# C 프로그램 경로 설정
db_manager_path = os.path.abspath(os.path.join(DB_DIR, "db_manager"))
get_coordinates_path = os.path.abspath(os.path.join(TRANSIT_DIR, "get_coordinates"))
get_route_info_path = os.path.abspath(os.path.join(TRANSIT_DIR, "get_route_info"))

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

        # C 프로그램 실행 전 환경 변수 확인
        logging.info(f"C 바이너리 실행 준비: {db_manager_path}, 사용자명='{username}', 비밀번호='{password}'")

        # C 프로그램 실행
        result = subprocess.check_output([db_manager_path, 'register', username, password], text=True).strip()
        logging.info(f"회원가입 결과: {result}")

        if result == 'success':
            return jsonify({'status': 'success', 'message': '회원가입이 완료되었습니다!'})
        else:
            return jsonify({'status': 'fail', 'message': '이미 존재하는 아이디입니다.'})

    except subprocess.CalledProcessError as e:
        logging.error(f"회원가입 중 C 프로그램 오류: {e.output}")
        return jsonify({'status': 'fail', 'message': f'회원가입 중 오류가 발생했습니다: {e.output}'})
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

        # C 프로그램 실행 전 환경 변수 확인
        logging.info(f"C 바이너리 실행 준비: {db_manager_path}, 사용자명='{username}', 비밀번호='{password}'")

        # C 프로그램 실행
        result = subprocess.check_output([db_manager_path, 'login', username, password], text=True).strip()
        logging.info(f"로그인 결과: {result}")

        if result == 'success':
            session['username'] = username
            return jsonify({'status': 'success', 'redirect': url_for('calendar')})
        else:
            return jsonify({'status': 'fail', 'message': '아이디 또는 비밀번호가 잘못되었습니다.'})

    except subprocess.CalledProcessError as e:
        logging.error(f"로그인 중 C 프로그램 오류: {e.output}")
        return jsonify({'status': 'fail', 'message': f'로그인 중 오류가 발생했습니다: {e.output}'})
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
                return jsonify({'status': 'success', 'events': events})
            else:
                return jsonify({'status': 'fail', 'message': '이벤트 로드에 실패했습니다.'})
        else:
            error_output = result.stderr.strip() or result.stdout.strip()
            return jsonify({'status': 'fail', 'message': f'이벤트 로드에 실패했습니다: {error_output}'})

    except Exception as e:
        logging.error(f"이벤트 로드 중 예외 발생: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'이벤트 로드 중 오류가 발생했습니다: {str(e)}'})

def get_coordinates(departure, destination):
    os.chdir(TRANSIT_DIR)
    try:
        result = subprocess.check_output(['./get_coordinates', departure, destination], text=True)
        lines = result.strip().splitlines()
        if len(lines) < 2:
            raise ValueError("C 프로그램 출력이 예상보다 적습니다.")
        return {'success': True, 'start_coords': lines[0], 'end_coords': lines[1]}
    except subprocess.CalledProcessError as e:
        logging.error(f"get_coordinates 실행 중 오류: {e}")
        return {'success': False, 'error': f"C 프로그램 실행 실패: {e}"}
    except ValueError as ve:
        logging.error(f"get_coordinates 실행 결과 오류: {ve}")
        return {'success': False, 'error': str(ve)}

# 대중교통 시간 가져오기
def get_transit_time(start_coords, end_coords, hour, minute):
    try:
        result = subprocess.check_output(['python3', 'get_transit_time.py', start_coords, end_coords, hour, minute], text=True)
        logging.info(f"get_transit_time 결과: {result.strip()}")
        return {'success': True, 'time': result.strip()}
    except subprocess.CalledProcessError as e:
        logging.error(f"get_transit_time 실행 중 오류: {e}")
        return {'success': False, 'error': str(e)}

# 자가용 시간 가져오기
def get_car_duration(start_coords, end_coords):
    try:
        result = subprocess.check_output(['./get_route_info', start_coords, end_coords], text=True)
        logging.info(f"get_car_duration 결과: {result.strip()}")
        return {'success': True, 'time': result.strip()}
    except subprocess.CalledProcessError as e:
        logging.error(f"get_route_info 실행 중 오류: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/get-route-time', methods=['POST'])
def get_route_time():
    data = request.json
    departure = data.get('departure', '').strip()
    destination = data.get('destination', '').strip()
    hour = data.get('hour', '').strip()
    minute = data.get('minute', '').strip()
    transport_mode = data.get('transport_mode', '').strip()

    logging.info(f"경로 시간 요청: 출발='{departure}', 도착='{destination}', 시간='{hour}:{minute}', 교통수단='{transport_mode}'")

    if not departure or not destination or not hour or not minute:
        logging.warning("get-route-time 요청 시 누락된 입력값")
        return jsonify({'success': False, 'error': '모든 입력값을 제공해야 합니다.'})

    coords = get_coordinates(departure, destination)
    if not coords['success']:
        logging.error(f"get_coordinates 실패: {coords['error']}")
        return jsonify({'success': False, 'error': coords['error']})

    start_coords = coords['start_coords']
    end_coords = coords['end_coords']

    if transport_mode == 'public':
        transit_result = get_transit_time(start_coords, end_coords, hour, minute)
        if transit_result['success']:
            return jsonify({'success': True, 'time': transit_result['time']})
        logging.error(f"get_transit_time 실패: {transit_result['error']}")
        return jsonify({'success': False, 'error': transit_result['error']})
    else:
        car_result = get_car_duration(start_coords, end_coords)
        if car_result['success']:
            return jsonify({'success': True, 'time': car_result['time']})
        logging.error(f"get_car_duration 실패: {car_result['error']}")
        return jsonify({'success': False, 'error': car_result['error']})

# 애플리케이션 실행
if __name__ == '__main__':
    logging.info("Flask 애플리케이션 시작")
    app.run(debug=False)  # 프로덕션 환경에서는 debug=False
