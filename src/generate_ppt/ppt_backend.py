from flask_cors import CORS
import requests
from flask import Flask, request, render_template,send_file,jsonify
from werkzeug.utils import secure_filename
from spark.SparkApi import SparkLLM
from img_2_words.img_2_words import img_2_words_run
from aiqa.Ifasr_app import audio2txt_Api
# from pptx import Presentation
import os
import io
import docx
from .run_generate_app import generate_ppt
from App import app
# 创建服务器
# app = Flask(__name__)
# CORS(app)

# 定义文件上传的目录
# UPLOAD_FOLDER = 'pre_text'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 定义路由，用于文件上传
# @app.route('/uploadppt', methods=['POST', 'GET'])
# def upload_requestfile():
#     # 检查是否有文件在请求内
#     if 'file' not in request.files:
#         return 'No file part in the request'
#     file = request.files['file']
#     theme = request.form['theme']
#     is_card_note = request.form['is_card_note']
#     is_card_note = int(is_card_note)

#     # 如果用户没有选择文件，浏览器也会提交一个空的文件无文件名
#     if file.filename == '':
#         return 'No selected file'

#     if file:
#         filename = secure_filename(file.filename)
#         upload_folder = os.path.join('generate_ppt', 'pre_text')
#         print(os.path.join(upload_folder, filename))
#         if not os.path.exists(upload_folder):
#             os.makedirs(upload_folder)
#         file.save(os.path.join(upload_folder, filename))
#         print("saved")
#         generate_ppt(filename, theme, is_card_note)
#         print("PPT generated")

#         ppt_file_name = os.path.splitext(filename)[0] + '.ppt'
#         ppt_file_path = os.path.join('generate_ppt', 'generate_ppt',ppt_file_name)
#         if os.path.exists(ppt_file_path):
#             return send_file(ppt_file_path, as_attachment=True)
#         else:
#             return 'Generated PPT file not found', 404
appid = 'e76d7d8f'
api_secret = 'Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl'
api_key = '990e2770b030441fbcc126c691daf5cd'

domain = "generalv3.5"    # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址
llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain, False)

@app.route('/conclude_text', methods=['POST'])
def conclude_text():
    # 接收 JSON 数据
    data = request.json
    text_to_process = data.get('text')

    # 在这里执行相应的处理逻辑，这里简单地返回一个包含翻译结果的 JSON 对
    question = text_to_process + '的100字以内总结是什么？只返回即可总结结果。'
    print(question)
    ans = llm.query(question)
    print(ans)
    # 准备要返回给前端的数据
    response_data = {
        'translation': ans
    }

    # 返回 JSON 数据
    return jsonify(response_data)

@app.route('/downloadppt', methods=['POST'])
def download_ppt():
    # 接收数据
    data = request.json
    text = data.get('text')
    theme = data.get('theme')
    is_card_note = data.get('isCardNote')
    # 保存文件（这部分你需要根据具体需求来调整）
    upload_folder = os.path.join('generate_ppt', 'pre_text')
    text_file_path = os.path.join(upload_folder, 'ppttmp.txt')
    with open(text_file_path, 'w', encoding='utf-8') as text_file:
        text_file.write(text)

    # 生成PPT（假设有一个 generate_ppt 函数来生成PPT）
    filename = 'ppttmp.txt'
    generate_ppt(filename, theme, is_card_note)

    # 返回生成的PPT文件
    ppt_file_path = os.path.join('generate_ppt','generate_ppt', 'ppttmp.ppt')
    if os.path.exists(ppt_file_path):
        return send_file(ppt_file_path, as_attachment=True)
    else:
        return 'Generated PPT file not found', 404

@app.route('/get_allfileppt', methods=['POST', 'GET'])
def get_all_fileppt():
    # 检查是否有文件在请求内
    if 'file' not in request.files:
        return 'No file part in the request'
    
    file = request.files['file']
    filename = file.filename
    if filename.endswith('.txt'):
        # 处理 txt 文件
        file_content = file.stream.read().decode('utf-8')
    elif filename.endswith('.docx'):
        # 处理 docx 文件
        file_content = read_docx(file.stream)
    else:
        return 'Unsupported file format'

    question = file_content + '的100字以内总结是什么？只返回即可总结结果。'
    print(question)
    ans = llm.query(question)
    print(ans)
    # 返回文件内容给前端
    return jsonify({'word': file_content,'ans':ans})

@app.route('/get_txtfileppt', methods=['POST', 'GET'])
def get_txt_fileppt():
    # 检查是否有文件在请求内
    if 'file' not in request.files:
        return 'No file part in the request'
    
    file = request.files['file']
    # 直接读取文件内容
    file_content = file.stream.read().decode('utf-8')

    question = file_content + '的100字以内总结是什么？只返回即可总结结果。'
    print(question)
    ans = llm.query(question)
    print(ans)
    # 返回文件内容给前端
    return jsonify({'word': file_content,'ans':ans})

def read_docx(file_stream):
    """读取 .docx 文件内容并返回文本"""
    # 将文件内容转换为字节流
    file_bytes = io.BytesIO(file_stream.read())
    doc = docx.Document(file_bytes)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

@app.route('/get_docxfileppt', methods=['POST', 'GET'])
def get_docx_fileppt():
    # 检查是否有文件在请求内
    if 'file' not in request.files:
        return 'No file part in the request'
    
    file = request.files['file']

    if file.filename.endswith('.docx'):
        # 处理 .docx 文件
        file_content = read_docx(file.stream)
    else:
        # 处理其他文本文件
        file_content = file.stream.read().decode('utf-8')

    question = file_content + '的100字以内总结是什么？只返回即可总结结果。'
    print(question)
    ans = llm.query(question)
    print(ans)
    # 返回文件内容给前端
    return jsonify({'word': file_content, 'ans': ans})
      

@app.route('/get_imageppt', methods=['POST'])
def get_imageppt_handler():
    if 'file' not in request.files:
        return 'No file part in the request'

    file = request.files['file']

    # 如果用户没有选择文件，浏览器也会提交一个空的文件无文件名
    if file.filename == '':
        return 'No selected file'

    if file:
        # 安全地获取文件名，并保存到服务器的 UPLOAD_FOLDER 目录下
        save_dir = os.path.join('img_2_words','image')
        # 确保目录存在
        if os.path.exists(save_dir):
            # 遍历目录中的所有文件和子目录
            for filename in os.listdir(save_dir):
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
        filename = file.filename
        file.save(os.path.join('img_2_words','image', filename))
        content = img_2_words_run()
        print("In ppt_backend/get_imageppt content:",content)
        # filename2 = "imageresult.txt"
        # filepath = os.path.join('img_2_words','image2wordresult',filename2)
        # with open(filepath, 'rb') as f:  # 使用二进制模式读取文件
            # content = f.read().decode('utf-8')  # 解码为字符串
        print('content:',content)
        # if os.path.exists(filepath):
        #     os.remove(filepath)
        #     print(f"File {filepath} has been deleted.")
        # else:
        #     print(f"File {filepath} does not exist.")
        filepath = os.path.join('img_2_words','image', filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"File {filepath} has been deleted.")
        else:
            print(f"File {filepath} does not exist.")
        question = content + '的100字以内总结是什么？只返回即可总结结果。'
        print(question)
        ans = llm.query(question)
        print(ans)
        return jsonify({"word": content,'ans':ans})

@app.route('/get_audioppt', methods=['POST'])
def get_audioppt_handler():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    save_dir = os.path.join('aiqa','question_audio')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'audiotranslation.wav')
    file.save(save_path)

    appid = 'e76d7d8f'
    secret_key = '3d354554a40d73e05331347dda9380c0'
    audio2txt = audio2txt_Api(appid, secret_key, save_path, "bot_ans")
    word = audio2txt.get_result(op=2)
    word = remove_duplicate_content(word)
    print('word',word)
    question = word + '的100字以内总结是什么？只返回即可总结结果。'
    print(question)
    ans = llm.query(question)
    print(ans)
    # 返回question和ans
    response = {
        'word': word,'ans':ans
    }
    return jsonify(response)
def remove_duplicate_content(result_context):
    """
    Remove duplicate content from result_context if it consists of two identical parts.
    """
    half_length = len(result_context) // 2
    first_half = result_context[:half_length]
    second_half = result_context[half_length:]

    if first_half == second_half:
        return first_half
    else:
        return result_context
    
@app.route('/get_speechppt', methods=['POST'])
def get_speechppt_handler():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the uploaded audio file
    save_dir = os.path.join('aiqa','question_audio')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, 'audiotranslation.wav')
    file.save(save_path)

    # Initialize your custom audio to text API
    appid = 'e76d7d8f'
    secret_key = '3d354554a40d73e05331347dda9380c0'
    audio2txt = audio2txt_Api(appid, secret_key, save_path, "bot_ans")

    # Get the result from the API
    try:
        word = audio2txt.get_result(op=2)
        word = remove_duplicate_content(word)
        print('word', word)
        question = word + '的100字以内总结是什么？只返回即可总结结果。'
        print(question)
        ans = llm.query(question)
        print(ans)
        # Return the result as a JSON response
        response = {'word': word,'ans':ans}
        return jsonify(response), 200

    except Exception as e:
        print(f"Error processing audio file: {e}")
        return jsonify({'error': 'Failed to process audio file'}), 500
