from flask_cors import CORS
from flask import Flask, request, jsonify
import regex
import os
import sys
import random
from utils import Logger
from spark.SparkApi import SparkLLM
from img_2_words.img_2_words import img_2_words_run
from .Ifasr_app import audio2txt_Api
import json5
from App import app

# with open('./config.json', encoding='utf-8') as f:
#     config = json5.load(f)
# appid = config['appid']
# api_secret = config['api_secret']
# api_key = config['api_key']
appid = 'e76d7d8f'
api_secret = 'Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl'
api_key = '990e2770b030441fbcc126c691daf5cd'

domain = "generalv3.5"    # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

# 创建服务器
# app = Flask(__name__)
# CORS(app)

# 创建SparkLLM对象
llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain, False)

@app.route('/get_chatanswer', methods=['POST'])
def get_chatanswer_handler():
    content = request.json
    question = str(content)
    print(question)
    ans = llm.query(question)
    print(ans)
    return ans

@app.route('/get_imagechatanswer', methods=['POST'])
def get_imagechatanswer_handler():
    # 获取文本消息
    message = request.form.get('message')
    # 获取上传的图片文件
    image = request.files.get('image')
    
    if image:
        # 保存图片文件
        filename = image.filename
        image_temp_path = os.path.join('img_2_words','image')
        delete_dir(image_temp_path)
        os.makedirs(image_temp_path, exist_ok=True)
        image_path = os.path.join(image_temp_path, filename)
        image.save(image_path)
        # 图像识别
        image_content = img_2_words_run()
        print("get_imagechatanswer_content:",image_content)

        filepath = os.path.join('img_2_words','image', filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"File {filepath} has been deleted.")
        else:
            print(f"File {filepath} does not exist.")
    
    print("get_imagechatanswer_content:",image_content)
    print("get_imagechatanswer_message:",message)

    question =  "我提出的问题是：" + message + "\n上传图片的内容如下:\n" + image_content
    print("question:",question)
    ans = llm.query(question)
    print('ans',ans)

    # 返回question和ans
    response = {
        'question': message,
        'answer': ans,
        'imagecontent': image_content,
    }
    return jsonify(response)

def delete_dir(save_dir):
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

@app.route('/get_chatvoiceanswer', methods=['POST'])
def get_chatvoiceanswer_handler():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    audio_file = request.files['audio']

    # Ensure the question_audio directory exists
    save_dir = os.path.join('aiqa','question_audio')
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
    save_path = os.path.join(save_dir, 'tmp_question.wav')

    # Save the audio file
    audio_file.save(save_path)

    # 配置信息
    appid = 'e76d7d8f'
    secret_key = '3d354554a40d73e05331347dda9380c0'
    audio2txt = audio2txt_Api(appid, secret_key, save_path, "bot_ans")
    question = audio2txt.get_result(op=2)
    question = remove_duplicate_content(question)
    print('question',question)
    ans = llm.query(question)
    print('ans',ans)
    # 返回question和ans
    response = {
        'question': question,
        'answer': ans
    }
    return jsonify(response)

@app.route('/get_classaudio', methods=['POST'])
def get_classaudio_handler():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    audio_file = request.files['audio']

    # Ensure the question_audio directory exists
    save_dir = os.path.join('aiqa','class_audio')
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
    save_path = os.path.join(save_dir, 'tmp_classaudio.wav')
    audio_file.save(save_path)

    # 配置信息
    appid = 'e76d7d8f'
    secret_key = '3d354554a40d73e05331347dda9380c0'
    audio2txt = audio2txt_Api(appid, secret_key, save_path, "bot_ans")
    classtext = audio2txt.get_result(op=2)
    classtext = remove_duplicate_content(classtext)
    print('classtext', classtext)
    question = '请用100字总结下述这段文字：'+classtext
    print('question',question)
    ans = llm.query(question)
    print('ans',ans)

    response = {
        'classtext': ans,
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

@app.route('/get_texttranslation', methods=['POST'])
def get_texttranslation_handler():
    content = request.json
    print('content',content)
    print(content.get('text'))
    word = str(content['text'])
    targettype = content['target_language']
    print('word',word)
    print('targettype',targettype)
    if targettype == 'en':
        targetlanguage = '英文'
    elif targettype == 'zh' :
        targetlanguage = '中文'
    else :
        targetlanguage = '英文'
    question = word + '的' + targetlanguage + '翻译结果是什么？只返回'+word+'的翻译结果即可'
    print(question)
    ans = llm.query(question)
    print(ans)
    return ans

@app.route('/get_imagetranslation', methods=['POST'])
def get_imagetranslation_handler():
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
        filename = file.filename
        file.save(os.path.join('img_2_words','image', filename))
        content = img_2_words_run()
        # filename2 = "imageresult.txt"
        # filepath = os.path.join('img_2_words','image2wordresult',filename2)
        # with open(filepath, 'rb') as f:  # 使用二进制模式读取文件
        #     content = f.read().decode('utf-8')  # 解码为字符串
        print('content:',content)
        # if os.path.exists(filepath):
            # os.remove(filepath)
            # print(f"File {filepath} has been deleted.")
        # else:
            # print(f"File {filepath} does not exist.")
        filepath = os.path.join('img_2_words','image', filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"File {filepath} has been deleted.")
        else:
            print(f"File {filepath} does not exist.")
        return jsonify({"word": content})

@app.route('/get_audiotranslation', methods=['POST'])
def get_audiotranslation_handler():
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
    # 返回question和ans
    response = {
        'word': word
    }
    return jsonify(response)

@app.route('/get_speechtranslation', methods=['POST'])
def get_speechtranslation_handler():
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

        # Return the result as a JSON response
        response = {'word': word}
        return jsonify(response), 200

    except Exception as e:
        print(f"Error processing audio file: {e}")
        return jsonify({'error': 'Failed to process audio file'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
