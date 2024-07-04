import json5
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from threading import Thread, Event
import os
import re
import time
import sounddevice as sd
import numpy as np
from ..spark.SparkApi import SparkLLM
from ..audio_to_txt.Ifasr_app import audio2txt_Api
from utils import random_call,random_call_record,record_audio

# 加载配置文件
with open('../config.json', encoding='utf-8') as f:
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
socketio = SocketIO(app)

# 全局变量初始化
is_recording = False
if_record = False
countdown_seconds = 0
countdown_event = Event()
course_name = ""
class_name = ""
end_time_minutes = 0


@app.route('/start_class', methods=['POST'])
def start_class():
    global if_record, countdown_seconds, course_name, class_name, end_time_minutes
    data = request.json
    course_name = data.get('course_name')
    class_name = data.get('class_name')
    end_time_minutes = int(data.get('end_time'))  # end_time 单位是分钟
    if_record = data.get('if_record', False)

    if if_record:
        filename = data.get('filename')
        start_recording_thread(filename)

    # 计算倒计时时间
    countdown_seconds = end_time_minutes * 60

    # 启动倒计时线程
    countdown_event.clear()
    countdown_thread = Thread(target=send_countdown)
    countdown_thread.start()

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
    global is_recording, pause_recording

    def recording_thread():
        nonlocal is_recording, pause_recording
        print("开始录音…")
        # 使用sounddevice的InputStream实现实时录音
        with sd.InputStream(samplerate=sample_rate, channels=channels) as stream:
            audio_frames = []
            while is_recording:
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


def send_countdown():
    global countdown_seconds, countdown_event
    while countdown_seconds > 0 and not countdown_event.is_set():
        time.sleep(1)
        countdown_seconds -= 1
        socketio.emit('countdown', {'countdown_seconds': countdown_seconds})
    if countdown_seconds <= 0:
        end_class(True)


@socketio.on('command')
def handle_command(data):
    global is_recording, countdown_seconds, class_name,course_name

    command = data.get('command')
    if command == "1":    # 随机点名
        student = random_call(class_name, course_name)
        emit('response', {"status": "Random call executed", "student": student})
        # 将点到学生通过student参数返回到了前端
        random_call_record(class_name, course_name, student)
    elif command == "2":    # AI 回答
        audio = record_audio()
        llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain)
        audio2txt = audio2txt_Api(appid, secret_key, os.path.join(audio_tmp_folder, "tmp_question.wav"), "bot_ans")
        question = audio2txt.get_result(op=2)
        ans = llm.query(question)
        emit('response', {"status": "AI answered", "answer": ans})
    elif command == "3":   # 提前结束课堂
        end_class()
    elif command == "4":
        # AI课堂小测？ 可以结合学生端出题功能
        pass
    elif command == "5":   # 结束录音
        if is_recording:
            check = data.get('check')
            if check:
                is_recording = False
                time.sleep(1)
            else:
                emit('response', {"status": "Recording ongoing, not stopped"})
                return
        else:
            time.sleep(1)
        is_recording = True
        filename = data.get('filename')
        start_recording_thread(filename)


@app.route('/end_class', methods=['POST'])
def end_class_route():
    end_class(False)
    return jsonify({"status": "Class ended"})


def end_class(from_timer=False):
    global if_record, countdown_seconds, countdown_event
    if_record = False
    countdown_seconds = 0
    countdown_event.set()

    if if_record:  # 只要在本堂课内至少启动一次录音就可以
        if_save_content = True if from_timer else request.json.get('if_save_content', False)
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

            if from_timer:
                socketio.emit('response', {"status": "Class content saved", "content": whole_class_content})
            else:
                emit('response', {"status": "Class content saved", "content": whole_class_content})

    if from_timer:
        socketio.emit('response', {"status": "Class ended due to timer"})
    else:
        emit('response', {"status": "Class ended"})


if __name__ == '__main__':
    socketio.run(app, debug=True)
