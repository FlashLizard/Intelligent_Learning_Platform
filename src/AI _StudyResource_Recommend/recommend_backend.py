from flask_cors import CORS
from flask import Flask, request, jsonify
import os
from spark_ai_recommend import ai_recommend  # 确保这个函数能够处理传入的文本和主题
from reptile.from_coursera import reptile_from_coursera

# 创建服务器
app = Flask(__name__)
CORS(app)


@app.route('/recommand', methods=['POST'])
def generate_from_text():
    # 获取POST请求中的文本
    data = request.get_json()
    course = data['course']
    limit = data['limit']  # TODO 前端传回两个量，表示课程名称（必须是一个英文单词）和查询要求（一段中文）
    print(course,limit)
    # if not data or 'first_string' not in data or 'second_string' not in data:
    #     return 'Missing first_string or second_string in the request', 400

    # 使用第一个字符串调用reptile_from_coursera函数
    course_data = reptile_from_coursera(course)  # 返回一个查找的列表

    # 使用第二个字符串调用ai_recommend函数
    recommend_result = ai_recommend(limit, course_data)
    print(recommend_result)

    return recommend_result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
