from flask_cors import CORS
import requests
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
from audio_to_txt import run_the_assistant
import shutil

# 创建服务器
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'audio'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'pcm', 'aac', 'opus', 'flac', 'ogg', 'm4a',
                      'amr', 'speex', 'lyb', 'ac3', 'aac', 'ape', 'm4r', 'mp4',
                      'acc', 'wma'}

# 定义文件上传的目录
UPLOAD_FOLDER = 'pre_text'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    # 处理TXT答案文件
    answer_file = request.files['answer']
    if answer_file and answer_file.filename.endswith('.txt'):
        answer_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'ans.txt'))
    else:
        return 'Answer file is missing or not a .txt file', 400

    # 清空音频文件夹
    if os.path.exists(app.config['AUDIO_FOLDER']):
        shutil.rmtree(app.config['AUDIO_FOLDER'])
    os.makedirs(app.config['AUDIO_FOLDER'])

    # 处理音频文件
    audio_files = request.files.getlist('audio_files')
    for file in audio_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['AUDIO_FOLDER'], filename))
    if not audio_files:
        return 'No audio files uploaded', 400

    run_the_assistant(inputans1=os.path.join(app.config['UPLOAD_FOLDER'], 'ans.txt'))

    result_json_path = os.path.join('res_context', 'result.json')
    if os.path.exists(result_json_path):
        with open(result_json_path, 'r', encoding='utf-8') as file:
            result_data = file.read()
            return jsonify(result_data)
    else:
        return 'Result JSON file does not exist', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
