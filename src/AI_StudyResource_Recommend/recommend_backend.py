from flask_cors import CORS
from flask import Flask, request, jsonify
import os
import re
from .spark_ai_recommend import ai_recommend  # 确保这个函数能够处理传入的文本和主题
from .reptile.from_coursera import reptile_from_coursera
from spark.SparkApi import SparkLLM
from App import app
# app = Flask(__name__)
# CORS(app)

def remove_non_english_characters(en_course):
    # 使用正则表达式匹配所有非英文字符，并将它们替换为空字符串
    cleaned_course = re.sub(r'[^a-zA-Z\s]', '', en_course)
    return cleaned_course
@app.route('/recommand', methods=['POST'])
def generate_from_text():
    # 获取POST请求中的文本
    data = request.get_json()
    course = data['course']
    limit = data['limit']  # TODO 前端传回两个量，表示课程名称（必须是一个英文单词）和查询要求（一段中文）
    print(course,limit)
    appid = 'e76d7d8f'
    api_secret = 'Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl'
    api_key = '990e2770b030441fbcc126c691daf5cd'
    domain = "generalv3.5"  # v3.0版本
    Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址
    llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain)
    en_course = llm.query(
        "如果" + course + "不是英文，请返回"+course+"的英文（返回结果只有一个英文单词）。")
    print(en_course)
    cleaned_course = remove_non_english_characters(en_course)
    print(cleaned_course)

    # 使用第一个字符串调用reptile_from_coursera函数
    course_data = reptile_from_coursera(cleaned_course)  # 返回一个查找的列表

    # 使用第二个字符串调用ai_recommend函数
    recommend_result = ai_recommend(limit, course_data)
    print(recommend_result)

    return recommend_result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
