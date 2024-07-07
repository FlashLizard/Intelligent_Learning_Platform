import json5
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread, Event
import os
import re
import time
import sounddevice as sd
import numpy as np
from src.spark.SparkApi import SparkLLM
from src.audio_to_txt.Ifasr_app import audio2txt_Api
from utils1 import random_call, random_call_record, record_audio

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

# Flask 应用和 SocketIO 设置
app = Flask(__name__)
CORS(app)

# 全局变量初始化
is_recording = False
if_record = False
countdown_seconds = 0
countdown_event = Event()
course_name = ""
class_name = ""
class_material = ""
end_time_minutes = 0


@app.route('/start_class', methods=['POST'])
def handle_start_class():
    global if_record, countdown_seconds, course_name, class_name, end_time_minutes
    data = request.json
    course_name = data.get('course_name')
    class_name = data.get('class_name')
    end_time_minutes = int(data.get('end_time'))  # end_time 单位是分钟
    class_material = data.get('class_material')  # 选择课件内容
    if_record = data.get('if_record', False)

    if if_record:
        filename = data.get('filename')
        start_recording_thread(filename)

    # 计算倒计时时间
    countdown_seconds = end_time_minutes * 60

    # 启动倒计时线程   改由前端实现
    # countdown_event.clear()
    # countdown_thread = Thread(target=send_countdown)
    # countdown_thread.start()

    return jsonify({
        "status": "Class started",
        "course_name": course_name,
        "class_name": class_name,
        "countdown_seconds": countdown_seconds
    })


def start_recording_thread(filename):
    global is_recording
    is_recording = True
    thread = Thread(target=record_audio_for_whole_class, args=(filename,))
    thread.start()


def record_audio_for_whole_class(filename='output.wav', sample_rate=44100, channels=2):
    """
    用于在点击开始（无论是开始上课时还是上课途中）录音后，为整堂课进行录音
    """
    global is_recording, pause_recording

    def recording_thread():
       # nonlocal is_recording, pause_recording  # 存疑，nonlocal还是global
        print("开始录音…")
        # 使用sounddevice的InputStream实现实时录音
        with sd.InputStream(samplerate=sample_rate, channels=channels) as stream:
            audio_frames = []
            while is_recording:  # 以is_recording作为是否继续录音的标志
                if pause_recording:
                    continue
                frame, overflowed = stream.read(sample_rate)  # 每次读1秒的音频帧
                if overflowed:
                    print("警告: 音频缓冲区溢出")
                audio_frames.append(frame)
            # 归一化并保存音频文件
            audio_dir_path = audio_folder
            os.makedirs(audio_dir_path, exist_ok=True)
            audio_file_path = os.path.join(audio_dir_path, filename)
            audio_data = np.concatenate(audio_frames, axis=0).tobytes()
            with open(audio_file_path, 'wb') as audio_file:
                audio_file.write(audio_data)
            print(f"录音已停止，保存在：{audio_dir_path}/{filename}")

    # 创建录音线程
    thread = Thread(target=recording_thread)
    thread.start()

    # 等待录音线程结束
    thread.join()


# def send_countdown():
#     """
#     向前端返回两个量：
#     countdown_seconds: 在前端显示课堂倒计时时长
#     is_recording: 后端是否在录音，如果是，前端显示“开始录音”，否则显示结束录音
#     """
#     global countdown_seconds, countdown_event, is_recording
#     while countdown_seconds > 0 and not countdown_event.is_set():
#         time.sleep(1)
#         countdown_seconds -= 1
#         socketio.emit('countdown', {
#             'countdown_seconds': countdown_seconds,
#             'is_recording': is_recording
#         })
#     if countdown_seconds <= 0:
#         end_class(True)

@app.route('/random_call', methods=['POST'])
def random_call_route():
    """
    随机点名
    """

    student = random_call(class_name, course_name)
    random_call_record(class_name, course_name, student)
    return jsonify({"status": "Random call executed", "student": student})


@app.route('/ai_answer', methods=['POST'])
def ai_answer_route():
    """
    AI回答学生问题
    """
    data = request.json
    audio = record_audio()
    llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain)
    audio2txt = audio2txt_Api(appid, secret_key, os.path.join(audio_tmp_folder, "tmp_question.wav"), "bot_ans")
    question = audio2txt.get_result(op=2)
    ans = llm.query(question)
    return jsonify({"status": "AI answered", "answer": ans})


@app.route('/ai_quiz', methods=['POST'])
def ai_quiz_route():
    """
    AI 课堂测
    这里需要使用到class_material
    """
    # Implement the AI quiz logic here
    pass
    #return jsonify({"status": "AI quiz triggered"})


@app.route('/toggle_recording', methods=['POST'])
def toggle_recording_route():
    """
    修改录音状态
    """
    global is_recording
    data = request.json
    if is_recording:
        check = data.get('check')
        if check:
            is_recording = False
            time.sleep(1)
        else:
            return jsonify({"status": "Recording ongoing, not stopped"})
    else:
        is_recording = True
        time.sleep(1)
        filename = data.get('filename')
        start_recording_thread(filename)
    return jsonify({"status": "Recording toggled"})


@app.route('/end_class', methods=['POST'])
def end_class_route():
    end_class()
    return jsonify({"status": "Class ended"})


def end_class():
    global if_record, countdown_seconds, countdown_event
    if_record = False
    countdown_seconds = 0
    countdown_event.set()

    if if_record:  # 只要在本堂课内至少启动一次录音就可以
        if_save_content = True
        if if_save_content:
            cnt = 1
            for foldername, filenames in os.walk(audio_folder):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    audio2txt = audio2txt_Api(appid, secret_key, file_path, f"whole_class_part{cnt}")
                    cnt += 1

            audio_dir = '../audio_to_txt/res_context'
            file_list = [
                f for f in os.listdir(audio_dir)
                if re.match(r'whole_class_part(\d+)\.txt', f)
            ]
            file_list.sort(key=lambda x: int(re.findall(r'(\d+)', x)[0]))

            whole_class_content = ''
            for file_name in file_list:
                part_number = re.findall(r'(\d+)', file_name)[0]
                with open(os.path.join(audio_dir, file_name), 'r') as file:
                    content = file.read()
                    whole_class_content += f"第{part_number}部分：\n{content}\n"
                os.remove(os.path.join(audio_dir, file_name))

            with open('../audio_to_txt/whole_class.txt', 'w') as file:
                file.write(whole_class_content)

    # 将本堂课的录音内容保存到../audio_to_txt/whole_class.txt

    return


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
