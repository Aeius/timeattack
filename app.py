from ast import Not
from flask import Flask, render_template, request, jsonify, redirect, url_for
import hashlib
import jwt
import datetime

app = Flask(__name__)

# DB 연결 코드
from pymongo import MongoClient

client = MongoClient(
    '')
db = client.luckyseven

SECRET_KEY = ""


# 최초 접속 시 연결되는 홈 페이지 지정
@app.route('/')
def home():
    # 현재 컴퓨터에 저장 된 쿠키 중 'mytoken'인 쿠키 가져 와 변수에 저장
    token_receive = request.cookies.get('mytoken')
    try:
        # 암호화되어있는 token의 값을 우리가 사용할 수 있도록 디코딩(암호화 풀기)해줍니다!
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.timeattack.find_one({"_id": payload['_id']})  # id, num, nickname, feed_images, content, like, reply
        feed_info = db.timeattack_board.find_one({"_id": payload['_id']})  # id, num, nickname, feed_images, content, like, reply

        # print(user_info)
        return render_template('/index.html',
                               feeds=feed_info, users=user_info)
        # 만약 해당 token의 로그인 시간이 만료되었다면, 아래와 같은 코드를 실행합니다.
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login"))
    except jwt.exceptions.DecodeError:
        # 만약 해당 token이 올바르게 디코딩되지 않는다면, 아래와 같은 코드를 실행합니다.
        return redirect(url_for("login"))


@app.route('/login')
def login():
    return render_template('/signup.html')



# 회원가입 입력받은 값을 받아 DB에 추가하기
@app.route("/api/signup", methods=["POST"])
def api_signup():
    email_receive = request.form['email_give']
    pwd_receive = request.form['pwd_give']
    # 입력받은 패스워드 값 해싱하여 암호화

    hashed_pw = hashlib.sha256(pwd_receive.encode('utf-8')).hexdigest()

    doc = {
        'email': email_receive,
        'pwd': hashed_pw,
    }
    db.timeattack.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '회원 가입 완료'})

# 게시글 정보값을 받아 DB에 추가하기
@app.route("/api/signup", methods=["POST"])
def api_signup():
    title_receive = request.form['title_give']
    content_receive = request.form['content_give']

    board_num = db.timeattack_board({'num'})
    date = datetime.datetime.now()
    doc = {
        'num' : board_num,
        'title': title_receive,
        'content': content_receive,
        'date' : date
    }
    db.timeattack.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '회원 가입 완료'})


@app.route("/api/login", methods=["POST"])
def api_login():
    email_receive = request.form['email_give']
    pwd_receive = request.form['pwd_give']
    # 입력받은 패스워드 값 해싱하여 암호화
    hashed_pw = hashlib.sha256(pwd_receive.encode('utf-8')).hexdigest()

    user = db.timeattack.find_one({'email': email_receive}, {'pwd': hashed_pw})

    if user is not None:

        hashed_id = hashlib.sha256(email_receive.encode('utf-8')).hexdigest()

        payload = {
            '_id': hashed_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1800)
        }
        # 토큰 생성 payload의 값 인코딩, 암호키 필수 유출금지!, 암호화형태 지정
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token, 'msg' : '로그인 성공'})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)  # 기본포트값 5000으로 설정
