from flask import Flask, request, jsonify, send_from_directory
import os
import shutil  # 用于清空文件夹

app = Flask(__name__)

# 设置文件上传的目标文件夹
UPLOAD_ANS = 'uploads'
UPLOAD_AUDIO = 'audio'
RESULT_FOLDER = 'result'
app.config['UPLOAD_ANS'] = UPLOAD_ANS
app.config['UPLOAD_AUDIO'] = UPLOAD_AUDIO
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {
    UPLOAD_ANS: {'txt'},
    UPLOAD_AUDIO: {'mp3', 'wav', 'pcm', 'aac', 'opus', 'flac', 'ogg', 'm4a', 'amr', 'speex',
                   'lyb', 'ac3', 'aac', 'ape', 'm4r', 'mp4', 'acc', 'wma'}
}


def allowed_file(filename, folder):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS'][folder]


@app.route('/upload', methods=['POST'])
def upload_file():
    folder = request.args.get('folder')
    if folder not in [UPLOAD_ANS, UPLOAD_AUDIO]:
        return jsonify({'error': '无效的上传目录！'}), 400

    if 'file' not in request.files:
        return jsonify({'error': '没有文件部分！'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件！'}), 400

    if file and allowed_file(file.filename, folder):
        filename = os.path.join(app.config[folder], file.filename)
        file.save(filename)
        return jsonify({'message': f'文件 {file.filename} 上传成功到 {folder}！'}), 200
    else:
        return jsonify({'error': '文件类型不匹配或不支持的文件扩展名！'}), 400


@app.route('/delete', methods=['POST'])
def delete_file():
    folder = request.args.get('folder')
    filename = request.args.get('filename')

    if folder not in [UPLOAD_ANS, UPLOAD_AUDIO]:
        return jsonify({'error': '无效的目录！'}), 400

    file_path = os.path.join(app.config[folder], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': f'文件 {filename} 已从 {folder} 中删除！'}), 200
    else:
        return jsonify({'error': '文件不存在！'}), 400


@app.route('/clear', methods=['POST'])
def clear_folder():
    folder = request.args.get('folder')

    if folder not in [UPLOAD_ANS, UPLOAD_AUDIO]:
        return jsonify({'error': '无效的目录！'}), 400

    folder_path = app.config[folder]
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    return jsonify({'message': f'{folder} 文件夹已清空！'}), 200


@app.route('/result', methods=['GET'])
def get_result():
    try:
        # 读取结果文件的内容
        with open(os.path.join(RESULT_FOLDER, app.config['RESULT_FILE']), 'r', encoding='utf-8') as file:
            result_data = file.read()
    except FileNotFoundError:
        return jsonify({'error': '结果文件未找到！'}), 404

    # 返回结果文件的内容
    return jsonify({'message': '成功获取结果文件内容！', 'data': result_data}), 200


@app.route('/download-result', methods=['GET'])
def download_result():
    # 检查结果文件是否存在
    if os.path.exists(os.path.join(RESULT_FOLDER, app.config['RESULT_FILE'])):
        return send_from_directory(RESULT_FOLDER, app.config['RESULT_FILE'], as_attachment=True)


if __name__ == '__main__':
    # 确保uploads和audio目录存在
    os.makedirs(app.config['UPLOAD_ANS'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_AUDIO'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    app.run(debug=True)
