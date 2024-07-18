import json5
from flask_cors import CORS
import requests
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
from .img_2_words import img_2_words_run
from spark.SparkApi import SparkLLM
from App import app
# 创建服务器
# app = Flask(__name__)
# CORS(app)

# 定义文件上传的目录
# UPLOAD_FOLDER = 'img'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# 加载配置文件
# with open('../../config.json', encoding='utf-8') as f:
#     config = json5.load(f)

# 配置信息
# appid = config['appid']
# api_secret = config['api_secret']
# api_key = config['api_key']
# secret_key = config['secret_key']
appid =  "e76d7d8f",
api_secret = "Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl",
api_key = "990e2770b030441fbcc126c691daf5cd",
secret_key = "3d354554a40d73e05331347dda9380c0"

# audio_folder = "audio_to_txt/audio"
# audio_tmp_folder = "audio_to_txt/tmp_audio"
# context_folder = "./context"

# Spark API 设置
domain = "generalv3.5"  # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

# 定义路由，用于文件上传
@app.route('/uploadimage', methods=['POST', 'GET'])
def upload_imagefile():
    print('upload_imagefile')
    # 检查是否有文件在请求内
    if 'file' not in request.files:
        return 'No file part in the request'

    file = request.files['file']
    print('上传的文件名：',file.filename)
    # 如果用户没有选择文件，浏览器也会提交一个空的文件无文件名
    if file.filename == '':
        return 'No selected file'

    if file:
        # 安全地获取文件名，并保存到服务器的 UPLOAD_FOLDER 目录下
        filename = secure_filename(file.filename)
        save_dir = os.path.join('img_2_words','image')
        # 确保目录存在
        if os.path.exists(save_dir):
            # 遍历目录中的所有文件和子目录
            for filename in os.listdir(save_dir):
                print('待删除文件名',filename)
                file_path = os.path.join(save_dir, filename)
                try:
                    # 如果是文件，则删除文件
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    # 如果是目录，则删除目录及其内容
                    elif os.path.isdir(file_path):
                        os.rmdir(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
        os.makedirs(save_dir, exist_ok=True)
        file.save(os.path.join('img_2_words','image', filename))
        img_2_words_run()
        filename2 = "imageresult.txt"
        txtdir = os.path.join('img_2_words','image2wordresult')
        filepath = os.path.join(txtdir,filename2)
        with open(filepath, "r") as f:
            content = f.read()
        print('content:',content)
        return jsonify({"content": content})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
