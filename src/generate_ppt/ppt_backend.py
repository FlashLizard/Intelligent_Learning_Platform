from flask_cors import CORS
import requests
from flask import Flask, request, render_template,send_file
from werkzeug.utils import secure_filename
# from pptx import Presentation
import os
from .run_generate_app import generate_ppt
from App import app
# 创建服务器
# app = Flask(__name__)
# CORS(app)

# 定义文件上传的目录
# UPLOAD_FOLDER = 'pre_text'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 定义路由，用于文件上传
@app.route('/uploadppt', methods=['POST', 'GET'])
def upload_requestfile():
    # 检查是否有文件在请求内
    if 'file' not in request.files:
        return 'No file part in the request'
    file = request.files['file']
    theme = request.form['theme']
    is_card_note = request.form['is_card_note']
    is_card_note = int(is_card_note)

    # 如果用户没有选择文件，浏览器也会提交一个空的文件无文件名
    if file.filename == '':
        return 'No selected file'

    if file:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join('generate_ppt', 'pre_text')
        print(os.path.join(upload_folder, filename))
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        file.save(os.path.join(upload_folder, filename))
        print("saved")
        generate_ppt(filename, theme, is_card_note)
        print("PPT generated")

        ppt_file_name = os.path.splitext(filename)[0] + '.ppt'
        ppt_file_path = os.path.join('generate_ppt', 'generate_ppt',ppt_file_name)
        if os.path.exists(ppt_file_path):
            return send_file(ppt_file_path, as_attachment=True)
        else:
            return 'Generated PPT file not found', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
