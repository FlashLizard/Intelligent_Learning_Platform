from ..spark.SparkApi import SparkLLM
from ..audio_to_txt.Ifasr_app import audio2txt_Api

import random
from threading import Timer
import json5
import os
import sounddevice as sd
import numpy as np
import threading
from pathlib import Path

with open('../config.json', encoding='utf-8') as f:
    config = json5.load(f)
appid = config['appid']
api_secret = config['api_secret']
api_key = config['api_key']
secret_key = config['secret_key']
audio_folder = "audio_to_txt/audio"

domain = "generalv3.5"    # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址


def select_from_database(name):
    pass

def save_to_database(name, data):
    pass  # 添加具体的数据库保存

# 全局变量，用于控制录音状态
is_recording = True
# 假设的录音函数,需要返回保存的文件路径
def record_audio(filename='output.wav', sample_rate=44100, channels=2):
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
    global is_recording

    def recording_thread():
        global is_recording
        print("开始录音…")
        # 使用sounddevice的InputStream实现实时录音
        with sd.InputStream(samplerate=sample_rate, channels=channels) as stream:
            audio_frames = []
            while is_recording:
                frame, overflowed = stream.read(sample_rate) # 每次读1秒的音频帧
                if overflowed:
                    print("警告: 音频缓冲区溢出")
                audio_frames.append(frame)
            # 归一化并保存音频文件
            audio_dir_path = Path(__file__).parent.parent / 'audio_to_txt/audio'
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
            is_recording = False
            break

    # 等待录音线程结束
    thread.join()

def random_call_and_record(class_name, course_name):
    students = []  # 这里需要写一个从数据库中选择数据的函数
    selected_student = random.choice(students)
    print(f"点到的学生是：{selected_student}")
    record_audio()  # 开始录音
    valid = input("是否是有效回答？")
    if valid:
        score = input(f"给{selected_student}的回答输入一个0-5的分数: ")
        save_to_database('class_records',
                     {'class_name': class_name, 'student': selected_student, 'course_name': course_name,
                      'score': score})


def start_class():
    course_name = input("请输入本节课程名: ")
    class_name = input("请输入班级名: ")  # 从数据库中选择班级
    end_time = input("请输入下课时间（例如15:30）: ")

    # 这里设置一个倒计时，到点结束课堂
    countdown_timer = Timer(60 * 60, end_class)  # 具体时间需要根据end_time计算
    countdown_timer.start()  # 启动倒计时

    while 1:
        command = input("等待指令（1-随机点名；2-AI回答；3-结束课堂): ")  # TODO 前端点击选择
        if command == "1":
            random_call_and_record(class_name, course_name)
        elif command == "2":
            audio = record_audio()  # 针对问题开始录音
            print("录音已经保存到临时文件夹。")
            llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain)
            audio2txt = audio2txt_Api(appid, secret_key, upload_file_path, "bot_ans")
            question = audio2txt.get_result(op=2)
            ans = llm.query(question)
            print(ans)  #TODO 这个答案需要显示在前端
        elif command == "3":
            break
        elif command == "4":
            # AI课堂小测？ 可以结合 1 出题
            pass

    end_class()


def end_class():
    # 这里处理课堂结束的逻辑，比如关闭倒计时，保存课堂记录等
    print("课堂已经结束。")

if __name__ == '__main__':
    start_class()