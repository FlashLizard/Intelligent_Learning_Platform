from flask_cors import CORS
from flask import Flask, request, jsonify
from .Database import create_test,get_user_tests,get_user_tests_analysis,get_test_by_id,get_user_id,create_user,delete_test
from utils import Logger
from spark.SparkApi import SparkLLM
import json5
import time
from datetime import datetime
from App import app

appid = 'e76d7d8f'
api_secret = 'Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl'
api_key = '990e2770b030441fbcc126c691daf5cd'

domain = "generalv3.5"    # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

# 创建SparkLLM对象
llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain, False)

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

@app.route('/get_user_tests_analysis', methods=['POST'])
def get_user_tests_analysis_handler():
    tests_data = get_user_tests_analysis(request.json['user_id'])
    print('tests_data:',tests_data)
    tests_analysis_prompt1 = '''我以以下格式:[
        {'test_name': '生物', 'test_time': datetime.datetime(2024, 7, 19, 5, 32, 16), 'id': 9, 'test_score': 65, 'test_subjects': '"生态学, 分子生物学"'}, {'test_name': '生物', 'test_time': datetime.datetime(2024, 8, 12, 23, 51, 12), 'id': 10, 'test_score': 83, 'test_subjects': '"细胞生物学"'}
    ]给你提供学生测试历史情况。请你根据里面的信息以我指定的格式:{
        "evaluation": "理科思维较强，逻辑清晰。感性分析能力和知识记忆能力相对偏弱。" /*对用户总体测试情况的描述, 此处只是个请你依据实际情况描述, 不要少于15字*/,
        "knowledge_radar": {
            "dimension": ["维度一","维度二","维度三","维度四","维度五","维度六"], /*雷达图的维度, 你需要根据题目的json分析出应该包含哪些维度(6维), 而不是和此处的示例*/
            "score": [100,80,30,10,10,40] /*依次对你给出的维度进行打分*/
        },
        "shortcoming": "给出你的分析出的缺点" /*缺点*/,
        "suggestion": "给出你分析出的意见" /*意见*/
    }返回对用户历史学习情况的解析json。学生测试历史情况如下:'''
    tests_analysis_prompt2 = "。请直接返回解析json, 不要添加任何其他描述"
    question = tests_analysis_prompt1+ str(tests_data) + tests_analysis_prompt2
    print("question:",question)
    tests_analysis = llm.query(question)
    print("tests_analysis:",tests_analysis)
    return {
        "status": "success",
        "tests_analysis":tests_analysis
    }

@app.route('/get_test', methods=['POST'])
def get_test_handler():
    content = request.json
    result = get_test_by_id(content['test_id'])
    print(result,type(result))
    if result is None:
        return jsonify({
            "status": "failed",
            "msg": "test not exists"
        })
    
    response = {
        "status": "success",
        "id": result['id'],
        "user_id": result['user_id'],
        "test_name": result['test_name'],
        "test_time": result['test_time'].isoformat(),
        "test_questions": json5.loads(result['test_questions']),
        "test_score": result['test_score'],
        "test_subjects": result['test_subjects'],
        "user_answers": result['user_answers'],
        "test_result_analysis": result['test_result_analysis']
    }
    return jsonify(response)

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
    print(request)
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
