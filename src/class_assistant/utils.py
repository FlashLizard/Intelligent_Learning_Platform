from flask import request
import random
import json5
import os
import sounddevice as sd
import numpy as np
import threading


with open('../config.json', encoding='utf-8') as f:
    config = json5.load(f)
appid = config['appid']
api_secret = config['api_secret']
api_key = config['api_key']
secret_key = config['secret_key']
audio_folder = "audio_to_txt/audio"
audio_tmp_folder = "audio_to_txt/tmp_audio"
context_folder = "./context"

domain = "generalv3.5"  # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址


def select_from_database(name):
    pass


def save_to_database(name, data):
    pass  # 添加具体的数据库保存


# 全局变量，用于控制录音状态
qa_recording = True
is_recording = True
pause_recording = False


# 假设的录音函数,需要返回保存的文件路径
def record_audio(filename='tmp_question.wav', sample_rate=44100, channels=2):
    """
    开始录音，并在接收到停止指令时结束录音。

    参数:
    filename : str, optional
        存储录音的文件名（默认为output.wav）。
    sample_rate : int, optional
        每秒采样率（默认44100）。
    channels : int, optional
        录音通道数（默认2，即立体声）。
    """
    global qa_recording
    qa_recording = True

    global pause_recording
    pause_recording = True

    def recording_thread():
        global qa_recording
        print("开始录音…")
        # 使用sounddevice的InputStream实现实时录音
        with sd.InputStream(samplerate=sample_rate, channels=channels) as stream:
            audio_frames = []
            while qa_recording:
                frame, overflowed = stream.read(sample_rate)  # 每次读1秒的音频帧
                if overflowed:
                    print("警告: 音频缓冲区溢出")
                audio_frames.append(frame)
            # 归一化并保存音频文件
            # audio_dir_path = Path(__file__).parent.parent / 'audio_to_txt/audio'
            audio_dir_path = audio_tmp_folder
            os.makedirs(audio_dir_path, exist_ok=True)
            audio_file_path = audio_dir_path / filename
            audio_data = np.concatenate(audio_frames, axis=0).tobytes()
            with open(audio_file_path, 'wb') as audio_file:
                audio_file.write(audio_data)
            print(f"录音已停止，保存在：{audio_dir_path}/{filename}")

    # 创建录音线程
    thread = threading.Thread(target=recording_thread)
    thread.start()

    # 在主线程中等待用户输入停止指令
    while True:
        command = input()
        if command.lower() == 'stop':
            qa_recording = False
            break

    # 等待录音线程结束
    thread.join()
    pause_recording = False  # 可以结束对课堂录音的暂停


def random_call(class_name,course_name):

    students = []  #TODO 这里需要写一个从数据库中根据班级和课堂数据选择学生集合的函数
    selected_student = random.choice(students)
    print(f"点到的学生是：{selected_student}")
    record_audio()  # 开始录音

def random_call_record(class_name, course_name, student_name):
    data = request.json
    valid = data.get('if_valid')  # 回答是否有效
    if valid:
        score = input(f"给{student_name}的回答输入一个0-5的分数: ")
        save_to_database('class_records',
                         {'class_name': class_name, 'student': student_name, 'course_name': course_name,
                          'score': score})




