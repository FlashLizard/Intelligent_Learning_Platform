import json5
from flask_cors import CORS
import requests
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
from img_2_words import img_2_words_run
from src.spark.SparkApi import SparkLLM

# 创建服务器
app = Flask(__name__)
CORS(app)

# 定义文件上传的目录
UPLOAD_FOLDER = 'img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 加载配置文件
with open('../../config.json', encoding='utf-8') as f:
    config = json5.load(f)

# 配置信息
appid = config['appid']
api_secret = config['api_secret']
api_key = config['api_key']
secret_key = config['secret_key']
audio_folder = "audio_to_txt/audio"
audio_tmp_folder = "audio_to_txt/tmp_audio"
context_folder = "./context"

# Spark API 设置
domain = "generalv3.5"  # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

# 定义路由，用于文件上传
@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    # 检查是否有文件在请求内
    if 'file' not in request.files:
        return 'No file part in the request'

    file = request.files['file']

    # 如果用户没有选择文件，浏览器也会提交一个空的文件无文件名
    if file.filename == '':
        return 'No selected file'

    if file:
        # 安全地获取文件名，并保存到服务器的 UPLOAD_FOLDER 目录下
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_2_words_run()
        filename = "./result/result.txt"
        with open(filename, "r") as f:
            content = f.read()
        # TODO 前端询问，是否进行下一步操作：(将图片识别出的文字转化为ppt & 进行AI提炼 & 转化为音频)
        opt = request.json.get('option')
        opt = int(opt)
        if opt == 1:   # 转化为 ppt
            # TODO   前端跳转到生成ppt界面，并默认输入文件是filename文件
            pass
        elif opt == 2:   # 进行AI提炼
            words = "请提炼这段文字中的有效信息：" + content
            llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain)
            ans = llm.query(words)  # 注意，这里是阻塞的
            print(ans)
            return jsonify({"valid_message": ans})
        elif opt == 3:   # 转化为音频
            # TODO   前端跳转到生成转音频界面，并默认输入文件是filename文件
            pass

        return jsonify({"content": content})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
