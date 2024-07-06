from flask_cors import CORS
from flask import Flask, request, jsonify
from .Database import create_test,get_user_tests,get_test_by_id,get_user_id,create_user,delete_test
from utils import Logger
import json5
import time
from datetime import datetime
from App import app

# 定义自定义序列化函数
def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # 将 datetime 对象转换为 ISO 格式的字符串
    raise TypeError(f"Type {type(obj)} not serializable")

# # 创建服务器
# app = Flask(__name__)

# app.json.ensure_ascii = False
# CORS(app)

@app.route('/save_test', methods=['POST'])
def save_test_handler():
    content = request.json
    #获取当前系统时间
    test_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    test_id = create_test(content['user_id'], content['test_name'], test_time,
                content['problems'],content['answers'], content['evaluation'], content['test_score'], content['test_subjects'])
    return {
        "status": "success",
        "test_id": test_id
    }

@app.route('/get_user_tests', methods=['POST'])
def get_user_tests_handler():
    tests = get_user_tests(request.json['user_id'])
    return {
        "status": "success",
        "tests":tests
    }

@app.route('/get_test', methods=['POST'])
def get_test_handler():
    content = request.json
    result = get_test_by_id(content['test_id'])
    if result is None:
        return {
            "status": "failed",
            "msg": "test not exists"
        }
    t = {
        "status":"success",    
        "test": result
    }
    return json5.dumps(t, ensure_ascii=False, default=datetime_serializer)

@app.route('/delete_test', methods=['POST'])
def delete_test_handler():
    content = request.json
    delete_test(content['test_id'])
    return {
        "status":"success"
    }

@app.route('/get_user_id', methods=['POST'])
def get_user_id_handler():
    content = request.json
    Logger.info(request)
    result = get_user_id(content['username'])
    if(result is None):
        return {
            "status": "failed",
            "msg": "user not exists"
        }
    return {
        "status": "success",
        "user_id": result
    }

@app.route('/create_user', methods=['POST'])
def create_user_handler():
    content = request.json
    Logger.info(request)
    user_id = create_user(content['username'])
    if user_id is None:
        return {
            "status": "failed",
            "msg": "user already exists"
        }
    return {
        "status": "success",
        "user_id": user_id
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
