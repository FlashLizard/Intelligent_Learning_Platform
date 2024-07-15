# -*- coding:utf-8 -*-
import hashlib
import hmac
import base64
import json
import os
import time
import requests

class AIPPT():

    def __init__(self, APPId, APISecret, Text):
        self.APPid = APPId
        self.APISecret = APISecret
        self.text = Text
        self.header = {}

    # 获取签名
    def get_signature(self, ts):
        try:
            # 对app_id和时间戳进行MD5加密
            auth = self.md5(self.APPid + str(ts))
            # 使用HMAC-SHA1算法对加密后的字符串进行加密
            return self.hmac_sha1_encrypt(auth, self.APISecret)
        except Exception as e:
            print(e)
            return None

    def hmac_sha1_encrypt(self, encrypt_text, encrypt_key):
        # 使用HMAC-SHA1算法对文本进行加密，并将结果转换为Base64编码
        return base64.b64encode(
            hmac.new(encrypt_key.encode('utf-8'), encrypt_text.encode('utf-8'), hashlib.sha1).digest()).decode('utf-8')

    def md5(self, text):
        # 对文本进行MD5加密，并返回加密后的十六进制字符串
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    # 创建PPT生成任务
    def create_task(self,theme,is_card_note):
        url = 'https://zwapi.xfyun.cn/api/aippt/create'
        timestamp = int(time.time())
        signature = self.get_signature(timestamp)
        body = self.getbody(self.text, theme, is_card_note)

        headers = {
            "appId": self.APPid,
            "timestamp": str(timestamp),
            "signature": signature,
            "Content-Type": "application/json; charset=utf-8"
        }
        self.header = headers
        response = requests.request("POST", url=url, data=json.dumps(body), headers=headers).text
        resp = json.loads(response)
        if (0 == resp['code']):
            return resp['data']['sid']
        else:
            print('创建PPT任务成功')
            return None

    # 构建请求body体
    def getbody(self, text, theme, is_card_note):
        body = {
            "query": text,
            "theme": theme,
            "is_card_note": is_card_note
        }
        return body

    # 轮询任务进度，返回完整响应信息
    def get_process(self, sid):
        print("sid:" + sid)
        if (None != sid):
            response = requests.request("GET", url=f"https://zwapi.xfyun.cn/api/aippt/progress?sid={sid}",
                                        headers=self.header).text
            print(response)
            return response
        else:
            return None

    # 读取用户选择的文件并连接文本
    def get_text_content(self, user_text, selected_file_path):
        try:
            with open(selected_file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            complete_text = user_text + ':' + file_content
            if len(complete_text) >= 8000:
                return None
            else:
                return complete_text
        except Exception as e:
            print(e)
            return None


    def get_result(self, theme='auto', is_card_note=0, selected_file_name=''):
        # 基于用户输入和文件内容组合文本
        self.text = self.get_text_content(self.text, os.path.join('generate_ppt','\pre_text', selected_file_name))
        if self.text is None:
            print("Error: The combined text length exceeds 8000 characters.")
            return None

        # 创建 PPT 生成任务
        task_id = self.create_task(theme=theme, is_card_note=is_card_note)
        # 轮询任务进度
        while True:
            response = self.get_process(task_id)
            resp = json.loads(response)
            process = resp['data']['process']
            if process == 100:
                PPTurl = resp['data']['pptUrl']
                self.download_file(PPTurl, selected_file_name)
                break

    def download_file(self, url, file_name):
        response = requests.get(url)
        if response.status_code == 200:
            output_folder = os.path.join('generate_ppt','generate_ppt')
            # 确保输出文件夹存在
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # 修改后缀名为ppt
            file_name1, _ = os.path.splitext(file_name)
            ppt_file_name = file_name1 + '.ppt'
            file_path = os.path.join(output_folder, ppt_file_name)

            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded successfully: {file_path}")
        else:
            print("Failed to download file.")
