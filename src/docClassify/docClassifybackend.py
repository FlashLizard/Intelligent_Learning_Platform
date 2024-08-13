from flask_cors import CORS

from docClassify import docClassify

from flask import Flask, request, send_file, jsonify
import os
import shutil
import zipfile

app = Flask(__name__)
CORS(app)

allowed_extensions = {'doc', 'docx', 'ppt', 'pptx', 'txt'}
default_folder = './default'
temp_folder = './temp'


# 路由：处理文件上传
@app.route('/docClassify', methods=['POST'])
def docClassify():
    data = request.json
    folder_list = data.get('folders', [])

    # 创建大文件夹 'default'

    if os.path.exists(default_folder):
        shutil.rmtree(default_folder)
    os.makedirs(default_folder)

    for folder_name in folder_list:
        os.makedirs(os.path.join(default_folder, folder_name))

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    files = request.files.getlist('files')   # 前端往这里传输文件


    # 保存上传的文件到 'temp' 文件夹
    for file in files:
        if file.filename.split('.')[-1] in allowed_extensions:
            file.save(os.path.join(temp_folder, file.filename))
        else:
            return jsonify({"error": "Invalid file type"}), 400

    # 处理文件并根据返回的数字复制到相应的文件夹
    for file_name in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, file_name)
        folder_index = docClassify(file_path, 2000, folder_list)  # 调用SPARK大模型分类函数

        destination_folder = os.path.join('./default', request.json['folders'][folder_index - 1])
        shutil.copy(file_path, destination_folder)

    # 清空 'temp' 文件夹
    shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    # 将 'default' 文件夹压缩为 zip 文件
    zip_file_path = './default.zip'
    shutil.make_archive('./default', 'zip', './default')

    return send_file(zip_file_path, as_attachment=True)   # 将压缩后的文件夹传到前端


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
