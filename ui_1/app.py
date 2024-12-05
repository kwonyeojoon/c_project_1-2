from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
load_dotenv()

import sqlite3
import subprocess
import os


app = Flask(__name__)


# 데이터베이스 연결 함수 및 테이블 생성 함수
def get_db_connection():
    # SQLite 데이터베이스 파일 users.db에 연결
    conn = sqlite3.connect('data/users.db')
    conn.row_factory = sqlite3.Row
    # users 테이블이 존재하지 않으면 생성
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')  # 정상 
  
    return conn

# 홈 페이지 라우트: 조원이 만든 login.html(로그인 페이지)와 연결하는 코드
@app.route('/')
def home():
    return render_template('login.html')

# 로그인 처리 라우트 (/login URL로 POST 요청을 받으면 실행되는 로그인 처리 함수)
@app.route('/login', methods=['POST'])
def login():
    # 클라이언트에서 전달된 JSON 데이터를 가져옴
    data = request.get_json()
    # JSON 데이터에서 사용자 이름과 비밀번호 추출
    username = data['username']
    password = data['password']
    
    # 데이터베이스 연결
    conn = get_db_connection()
    # users 테이블에서 해당 사용자 정보를 조회
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()

    # 로그인 성공 여부에 따라 JSON 응답 생성
    if user:
        return jsonify({'status': 'success', 'redirect': url_for('calendar')})
    else:
        return jsonify({'status': 'fail', 'message': '아이디 또는 비밀번호가 잘못되었습니다.'})

# 회원가입 처리 라우트 (/register URL로 POST 요청을 받으면 실행되는 회원가입 처리 함수)
@app.route('/register', methods=['POST'])
def register():
    # 클라이언트에서 전달된 JSON 데이터를 가져옴
    data = request.get_json()
    username = data['username']
    password = data['password']
    
    conn = get_db_connection()
    try:
        # users 테이블에 새 사용자 추가
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        response = {'status': 'success', 'message': '회원가입이 완료되었습니다!'}
    except sqlite3.IntegrityError:
        # 중복 아이디가 있을 경우 예외 처리
        response = {'status': 'fail', 'message': '이미 존재하는 아이디입니다.'}
    finally:
        conn.close()
        
    # JSON 형식으로 결과 반환
    return jsonify(response)

# 달력 페이지 라우트: calendar.html와 연결하는 코드 (/calendar URL로 접속 시 실행되는 함수로, 달력 페이지로 이동)
@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

# @app.route('/cal.html')
@app.route('/cal')
def cal():
    selected_date = request.args.get('date')
    return render_template('cal.html', date=selected_date)

# 컴파일 및 실행 함수
def compile_and_execute_c_program(departure, destination, hour, minute):
    # C 파일 경로 및 실행 파일 이름
    c_file_path = os.path.join(os.getcwd(), 'transit', 'geo_crawling_with_python.c')
    executable_path = os.path.join(os.getcwd(), 'transit', 'geo_crawling_with_python')

    compile_command = [
        'gcc',
        '-o', executable_path,
        c_file_path,
        '$(pkg-config --cflags --libs libcurl)',
        '-lcjson',
        '-Wl,-rpath,/opt/homebrew/lib'
    ]
    try:
        subprocess.run(' '.join(compile_command), shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return {'success': False, 'error': f"컴파일 실패: {e}"}

    # 컴파일된 프로그램 실행
    execute_command = [
        executable_path,
        departure,
        destination,
        hour,
        minute
    ]
    try:
        result = subprocess.check_output(execute_command, text=True)
        return {'success': True, 'output': result.strip()}
    except subprocess.CalledProcessError as e:
        return {'success': False, 'error': f"C 프로그램 실행 실패: {e}"}

# 경로 시간 API
@app.route('/get-route-time', methods=['POST'])
def get_route_time():
    data = request.json
    departure = data.get('departure', '').strip()
    destination = data.get('destination', '').strip()
    hour = data.get('hour', '').strip()
    minute = data.get('minute', '').strip()

    if not departure or not destination or not hour or not minute:
        return jsonify({'success': False, 'error': '모든 입력값을 제공해야 합니다.'})

    result = compile_and_execute_c_program(departure, destination, hour, minute)
    if result['success']:
        return jsonify({'success': True, 'time': result['output']})
    else:
        return jsonify({'success': False, 'error': result['error']})
    

"""     
@app.route('/saveTimeline', methods=['POST'])
def saveTimeline():
    # 클라이언트에서 전달된 JSON 데이터를 가져옴
    data = request.get_json()
    title = data['title']
    sDate = data['selectedDate']
    sTime = data['startTime']
    eTime = data['endTime']

    conn = get_db_connection()
    try:
        # users 테이블에 새 사용자 추가
        conn.execute('INSERT INTO Timeline (selected_date, title, start_time, end_time) VALUES (?, ?, ?, ?)', (sDate, title, sTime, eTime))
        conn.commit()
        response = {'status': 'success', 'message': '완료되었습니다!'}
    except sqlite3.IntegrityError:
        # 중복 아이디가 있을 경우 예외 처리
        response = {'status': 'fail', 'message': '실패했습니다.'}
    finally:
        conn.close()
        
    # JSON 형식으로 결과 반환
    return jsonify(response)

@app.route('/loadTimeline', methods=['POST'])
def saveTimeline():
    # 클라이언트에서 전달된 JSON 데이터를 가져옴
    data = request.get_json()
    sDate = data['sDate']
    conn = get_db_connection()
    try:
        list = conn.execute('SELECT * FROM Timeline WHERE selected_date = ?', (sDate)).fetchall()
        response = {'status': 'success', 'message': '완료되었습니다!', 'd': list}
    except sqlite3.IntegrityError:
        response = {'status': 'fail', 'message': '실패했습니다.'}
    finally:
        conn.close()
        
    # JSON 형식으로 결과 반환
    return jsonify(response)

 """
 # 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True)
