import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from dotenv import load_dotenv
import subprocess
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')  # 환경 변수로 SECRET_KEY 설정

current_directory = os.getcwd()
PROJECT_ROOT = current_directory
TRANSIT_DIR = os.path.join(PROJECT_ROOT, "ui_1", "transit")
DB_DIR = os.path.join(PROJECT_ROOT, "ui_1", "db_manager")

# 홈 페이지 라우트
@app.route('/')
def home():
    return render_template('login.html')

# C 프로그램 경로 설정
db_manager_path = os.path.abspath(os.path.join(DB_DIR, "db_manager"))

# 회원가입 처리 라우트
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username'].strip()
    password = data['password'].strip()
    logging.info(f"Register attempt for user: {username}")

    try:
        result = subprocess.check_output([db_manager_path, 'register', username, password], text=True).strip()
        logging.info(f"Register result: {result}")
        if result == 'success':
            return jsonify({'status': 'success', 'message': '회원가입이 완료되었습니다!'})
        else:
            return jsonify({'status': 'fail', 'message': '이미 존재하는 아이디입니다.'})
    except subprocess.CalledProcessError as e:
        logging.error(f"Register subprocess error: {e.output}")
        return jsonify({'status': 'fail', 'message': f'회원가입 중 오류가 발생했습니다: {e.output}'})

# 로그인 처리 라우트
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username'].strip()
    password = data['password'].strip()
    logging.info(f"Login attempt for user: {username}")

    try:
        result = subprocess.check_output([db_manager_path, 'login', username, password], text=True).strip()
        logging.info(f"Login result: {result}")
        if result == 'success':
            session['username'] = username
            return jsonify({'status': 'success', 'redirect': url_for('calendar')})
        else:
            return jsonify({'status': 'fail', 'message': '아이디 또는 비밀번호가 잘못되었습니다.'})
    except subprocess.CalledProcessError as e:
        logging.error(f"Login subprocess error: {e.output}")
        return jsonify({'status': 'fail', 'message': f'로그인 중 오류가 발생했습니다: {e.output}'})

# 달력 페이지 라우트
@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/cal')
def cal():
    selected_date = request.args.get('date')
    return render_template('cal.html', date=selected_date)

# 타임라인 이벤트 저장 라우트
@app.route('/saveTimeline', methods=['POST'])
def save_timeline():
    if 'username' not in session:
        return jsonify({'status': 'fail', 'message': '로그인이 필요합니다.'}), 401

    username = session['username']
    data = request.get_json()
    title = str(data.get('title', ''))
    date = str(data.get('date', ''))
    start_time = str(data.get('startTime', ''))
    end_time = str(data.get('endTime', ''))
    trans_time = str(data.get('transTime', ''))

    logging.info(f"Saving timeline event: {title} on {date}")

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

        logging.info(f"Save event result: {result}")

        if result.returncode == 0 and result.stdout.strip() == 'success':
            return jsonify({'status': 'success'})
        else:
            error_output = result.stderr.strip() or result.stdout.strip()
            return jsonify({'status': 'fail', 'message': f'이벤트 저장에 실패했습니다: {error_output}'})
    except Exception as e:
        logging.error(f"Save timeline exception: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'이벤트 저장 중 오류가 발생했습니다: {str(e)}'})

# 타임라인 이벤트 로드 라우트
@app.route('/loadTimeline', methods=['POST'])
def load_timeline():
    if 'username' not in session:
        return jsonify({'status': 'fail', 'message': '로그인이 필요합니다.'}), 401

    username = session['username']
    data = request.get_json()
    date = str(data.get('sDate', ''))

    logging.info(f"Loading timeline events for user: {username} on {date}")

    try:
        cmd = [db_manager_path, 'load_events', username, date]
        result = subprocess.run(cmd, capture_output=True, text=True)

        logging.info(f"Load events result: {result}")

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
                            is_transit = "이동시간" in title
                            events.append({'title': title, 'start_time': start_time, 'end_time': end_time, 'is_transit': is_transit})
                return jsonify({'status': 'success', 'events': events})
            else:
                return jsonify({'status': 'fail', 'message': '이벤트 로드에 실패했습니다.'})
        else:
            error_output = result.stderr.strip() or result.stdout.strip()
            return jsonify({'status': 'fail', 'message': f'이벤트 로드에 실패했습니다: {error_output}'})
    except Exception as e:
        logging.error(f"Load timeline exception: {str(e)}")
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
        return {'success': False, 'error': f"C 프로그램 실행 실패: {e}"}
    except ValueError as ve:
        return {'success': False, 'error': str(ve)}

# 대중교통 시간 가져오기
def get_transit_time(start_coords, end_coords, hour, minute):
    try:
        result = subprocess.check_output(['python3', 'get_transit_time.py', start_coords, end_coords, hour, minute], text=True)
        return {'success': True, 'time': result.strip()}
    except subprocess.CalledProcessError as e:
        return {'success': False, 'error': str(e)}

# 자가용 시간 가져오기
def get_car_duration(start_coords, end_coords):
    try:
        result = subprocess.check_output(['./get_route_info', start_coords, end_coords], text=True)
        return {'success': True, 'time': result.strip()}
    except subprocess.CalledProcessError as e:
        return {'success': False, 'error': str(e)}

@app.route('/get-route-time', methods=['POST'])
def get_route_time():
    data = request.json
    departure = data.get('departure')
    destination = data.get('destination')
    hour = data.get('hour')
    minute = data.get('minute')
    transport_mode = data.get('transport_mode')

    if not departure or not destination or not hour or not minute:
        return jsonify({'success': False, 'error': '모든 입력값을 제공해야 합니다.'})

    coords = get_coordinates(departure, destination)
    if not coords['success']:
        return jsonify({'success': False, 'error': coords['error']})

    start_coords = coords['start_coords']
    end_coords = coords['end_coords']

    if transport_mode == 'public':
        transit_result = get_transit_time(start_coords, end_coords, hour, minute)
        if transit_result['success']:
            return jsonify({'success': True, 'time': transit_result['time']})
        return jsonify({'success': False, 'error': transit_result['error']})
    else:
        car_result = get_car_duration(start_coords, end_coords)
        if car_result['success']:
            return jsonify({'success': True, 'time': car_result['time']})
        return jsonify({'success': False, 'error': car_result['error']})

# 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=False)  # 프로덕션 환경에서는 debug=False
