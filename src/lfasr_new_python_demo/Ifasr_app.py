# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, redirect, url_for
import base64
import hashlib
import hmac
import json
import os
import time
import requests
import urllib
import random
import os
import Levenshtein

app = Flask(__name__)
UPLOAD_ANS = 'uploads'  # 上传作为答案的文件
UPLOAD_AUDIO = 'audio'
AUDIO2CONTEXT = 'res_context'
app.config['UPLOAD_ANS'] = UPLOAD_ANS
app.config['UPLOAD_AUDIO'] = UPLOAD_AUDIO
app.config['AUDIO2CONTEXT'] = AUDIO2CONTEXT

lfasr_host = 'https://raasr.xfyun.cn/v2/api'
# 请求的接口名
api_upload = '/upload'
api_get_result = '/getResult'


@app.route('/')
def upload_file():
    return render_template('upload.html')


@app.route('/api/run_the_assistant', methods=['POST'])
def run_the_assistant():
    """
    完成一个背诵检查助手完整的流程
    1.读取音频区（audio)的所有文件
    2.调用语音转写API
    3.得到每个音频文件的文字版，放在res_context
    4.读取答案区（uploads）的某个被选中文件
    5.依次将每个文件进行打分，打分结果写入结果区的结果文件（result/result.txt)
    :return:
    """
    appid = "e76d7d8f"
    secret_key = "3d354554a40d73e05331347dda9380c0"
    audio_folder = app.config['UPLOAD_AUDIO']

    # 检查文件夹是否为空
    if not os.listdir(audio_folder):
        # 如果为空，直接返回错误
        return jsonify({'error': '音频暂存区中没有文件，请上传音频文件后再试。'}), 400

    # 若文件夹不为空，则继续处理
    results = []  # 改动：用于存储多个文件的处理结果
    for eachname in os.listdir(audio_folder):  # 遍历所有需要检查的音频文件
        to_judge_file_path = os.path.join(audio_folder, eachname)
        # 为每个文件创建 RequestApi 实例
        api = RequestApi(appid=appid, secret_key=secret_key, upload_file_path=to_judge_file_path, eachname=eachname)
        # 获取结果
        result = api.get_result()
        os.remove(to_judge_file_path)  # 每次调用后删除上传的文件，避免服务器上文件堆积

        results.append(result)  # 改动：将每个文件的结果添加到结果列表中

    # 返回所有处理后的结果

    inputans = InputAns()

    ans_response = inputans.get_file_name()
    # TODO 前端将这个被选择的答案文件发到后端，把inputans.ans_file_name替换成用户选择的答案文件，然后删掉这个get_file_name方法

    if "错误：" in ans_response:
        # 发生错误，返回错误信息
        return jsonify({'error': ans_response}), 400
    else:
        # 文件存在，开始计算准确率并写入结果文件
        accuracy_response = inputans.compare_with_answer()
        if "错误：" in accuracy_response:
            return jsonify({'error': accuracy_response}), 400

    return results


@app.route('/api/run_the_assistant_send_context_to_starfire', methods=['POST'])
def run_the_assistant_send_context_to_starfire():
    """
    完成一个课堂内容生成的部分流程
    1.读取音频区（audio)的文件（这里必须规定只有一个文件）
    2.调用语音转写API
    3.得到音频文件的文字版放在res_context
    TODO: 星火大模型API部分需要拿走res_context中的文件再处理，
    在星火大模型部分调用这个方法。
    :return:
    """

    appid = "e76d7d8f"
    secret_key = "3d354554a40d73e05331347dda9380c0"
    audio_folder = app.config['UPLOAD_AUDIO']

    # 检查文件夹中文件数量
    audio_files = os.listdir(audio_folder)
    if len(audio_files) != 1:
        # 如果不止一个文件或无文件，直接返回错误
        return jsonify({'error': '音频暂存区内必须仅有一个文件。请确保上传了一个并且只有一个音频文件。'}), 400

    audio_file = audio_files[0]
    audio_file_path = os.path.join(audio_folder, audio_file)

    # 创建 RequestApi 实例
    api = RequestApi(appid=appid, secret_key=secret_key, upload_file_path=audio_file_path)

    # 获取结果
    result = api.get_result()
    os.remove(audio_file_path)  # 删除上传的文件，避免服务器上文件堆积

    # 直接返回处理后的结果
    return jsonify(result), 200



def remove_backslashes(input_string):
    # 使用 replace() 函数移除所有的反斜杠 "\"
    return input_string.replace("\\", "")


def extract_w_values(input_string):
    result = ''
    index = 0
    # 循环遍历字符串查找"w"属性
    while index < len(input_string):
        index = input_string.find('"w":"', index)
        if index == -1:  # 如果没有找到，结束循环
            break
        start = index + 5  # "w":"的结束位置即是我们需要的值的开始位置
        end = input_string.find('"', start)  # 查找值的结束位置
        result += input_string[start:end] + ' '  # 将找到的值加到结果字符串中
        index = end + 1
    return result.rstrip()  # 返回结果字符串，并移除末尾的空格


class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path, eachname):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.eachname = eachname
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()

    def get_signa(self):
        appid = self.appid
        secret_key = self.secret_key
        m2 = hashlib.md5()
        m2.update((appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        return signa

    def upload(self):
        print("上传部分：")
        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict["fileSize"] = file_len
        param_dict["fileName"] = file_name
        param_dict["duration"] = "200"
        print("upload参数：", param_dict)
        data = open(upload_file_path, 'rb').read(file_len)

        response = requests.post(url=lfasr_host + api_upload + "?" + urllib.parse.urlencode(param_dict),
                                 headers={"Content-type": "application/json"}, data=data)
        print("upload_url:", response.request.url)
        result = json.loads(response.text)
        print("upload resp:", result)
        return result

    def get_result(self):
        uploadresp = self.upload()
        orderId = uploadresp['content']['orderId']
        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict['orderId'] = orderId
        param_dict['resultType'] = "transfer,predict"
        print("")
        print("查询部分：")
        print("get result参数：", param_dict)
        status = 3
        # 建议使用回调的方式查询结果，查询接口有请求频率限制
        while status == 3:
            response = requests.post(url=lfasr_host + api_get_result + "?" + urllib.parse.urlencode(param_dict),
                                     headers={"Content-type": "application/json"})
            # print("get_result_url:",response.request.url)
            result = json.loads(response.text)
            print(result)
            status = result['content']['orderInfo']['status']
            context = result['content']['orderResult']  # 返回的文本结果
            context = remove_backslashes(context)

            print("status=", status)
            if status == 4:
                break
            time.sleep(5)
        print("get_result resp:", result)
        result_context = extract_w_values(context)
        result_context = result_context.replace(" ", "")

        print("res:", result_context)
        directory = app.config['AUDIO2CONTEXT']
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 为用户提供提示并获取输入的文件名
        file_name = self.eachname

        # 用.txt扩展名完善文件名
        file_name_with_extension = file_name + '.txt'

        # 保存字符串到指定文件
        string_to_save = result_context
        with open(os.path.join(directory, file_name_with_extension), 'w') as file:
            file.write(string_to_save)

        print(f"文件已保存在 {directory}{file_name_with_extension}")
        return result


class InputAns(object):
    def __init__(self):
        self.ans_file_name = ""
        self.result = "./result/result.txt"

    def get_file_name(self):
        # TODO: 这是个错误的方法, 这一步需要前端完成

        self.ans_file_name = input("请输入答案的文件名（不包括.txt扩展名）：")
        filename = os.path.join(app.config['UPLOAD_ANS'], self.ans_file_name)
        if not os.path.exists(f"{filename}.txt"):
            # 文件不存在
            return "错误：文件不存在。"
        else:
            # 更新文件名
            self.ans_file_name = f"{filename}.txt"
            return f"文件 {self.ans_file_name} 存在，已更新。"

    def calculate_accuracy(self, answer_file, compare_file):

        with open(answer_file, 'r') as file:
            answer_content = file.read()
        with open(compare_file, 'r') as file:
            compare_content = file.read()
        distance = Levenshtein.distance(answer_content, compare_content)
        similarity = 1 - distance / max(len(answer_content), len(compare_content))
        return similarity

    def compare_with_answer(self):
        if not self.ans_file_name:
            return "错误：没有指定答案文件。"

        with open(self.result, 'w') as result_file:
            # 遍历 res_context 目录下所有 txt 文件
            for filename in os.listdir(app.config('AUDIO2CONTEXT')):
                if filename.endswith('.txt'):
                    # 计算每个文件与答案的准确率
                    accuracy = self.calculate_accuracy(self.ans_file_name, os.path.join(app.config['AUDIO2CONTEXT'],
                                                                                        filename))
                    # 写入准确率到结果文件
                    result_file.write(f"{filename}: 准确率: {accuracy}\n")
