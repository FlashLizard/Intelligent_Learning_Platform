from flask_cors import CORS

from docClassify.docClassify import doc_Classify

from flask import Flask, request, send_file, jsonify
import os
import shutil
import zipfile
from App import app

allowed_extensions = {'doc', 'docx', 'ppt', 'pptx', 'txt'}
default_folder = './docClassify/default'
temp_folder = './docClassify/temp'

# 路由：处理文件上传
# @app.route('/docclassify_zrc', methods=['POST'])
# def docClassify_handler():
#     print("docClassify_handler")
#     data = request.json
#     print("data:",data)
#     folder_list = data.get('folders', [])
#     print("folder_list:",folder_list)

#     # 创建大文件夹 'default'
#     if os.path.exists(default_folder):
#         shutil.rmtree(default_folder)
#     os.makedirs(default_folder)

#     for folder_name in folder_list:
#         os.makedirs(os.path.join(default_folder, folder_name))

#     if not os.path.exists(temp_folder):
#         os.makedirs(temp_folder)

#     files = request.files.getlist('files')   # 前端往这里传输文件

#     # 保存上传的文件到 'temp' 文件夹
#     for file in files:
#         if file.filename.split('.')[-1] in allowed_extensions:
#             file.save(os.path.join(temp_folder, file.filename))
#         else:
#             return jsonify({"error": "Invalid file type"}), 400

#     # 处理文件并根据返回的数字复制到相应的文件夹
#     for file_name in os.listdir(temp_folder):
#         file_path = os.path.join(temp_folder, file_name)
#         folder_index = doc_Classify(file_path, 2000, folder_list)  # 调用SPARK大模型分类函数

#         destination_folder = os.path.join('./docClassify/default', request.json['folders'][folder_index - 1])
#         shutil.copy(file_path, destination_folder)

#     # 清空 'temp' 文件夹
#     shutil.rmtree(temp_folder)
#     os.makedirs(temp_folder)

#     # 将 'default' 文件夹压缩为 zip 文件
#     zip_file_path = './docClassify/default.zip'
#     shutil.make_archive('./docClassify/default', 'zip', './docClassify/default')

#     return send_file(zip_file_path, as_attachment=True)   # 将压缩后的文件夹传到前端


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/docclassify', methods=['POST'])
def doc_classify_handler():
    folder_list = request.form.get('categories')
    if folder_list:
        folder_list = eval(folder_list)  # 将字符串转换为列表
    if isinstance(folder_list, list):
        if "其他" not in folder_list and "其它" not in folder_list:  # 检查 "其他" 是否已经存在
            folder_list.append("其他")

    if os.path.exists(default_folder):
        shutil.rmtree(default_folder)
    os.makedirs(default_folder)

    for folder_name in folder_list:
        os.makedirs(os.path.join(default_folder, folder_name))

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    files = request.files.getlist('files')

    for file in files:
        if allowed_file(file.filename):
            file.save(os.path.join(temp_folder, file.filename))
        else:
            return jsonify({"error": "Invalid file type"}), 400
    
    file_classification = {}  # 记录文件分类结果的字典
    # 处理文件并根据返回的数字复制到相应的文件夹
    for file_name in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, file_name)
        folder_index = doc_Classify(file_path, 2000, folder_list)  # 调用SPARK大模型分类函数
        print("folder_index:",folder_index)

        destination_folder = os.path.join('./docClassify/default', folder_list[folder_index - 1])
        shutil.copy(file_path, destination_folder)
        file_classification[file_name] = folder_list[folder_index - 1]  # 记录文件和目标文件夹的映射关系
    
    shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

    zip_file_path = './static/default.zip'
    shutil.make_archive('./static/default', 'zip', './docClassify/default')

    # 返回分类结果和压缩文件
    response = {
        "classification": file_classification,
        "zip_file": zip_file_path
    }
    return jsonify(response)