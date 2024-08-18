from flask_cors import CORS
from flask import Flask, request, jsonify
from .Database import create_test,get_user_tests,get_user_tests_analysis,get_test_by_id,get_user_id,get_user_password,get_user_voiceurl,get_user_imageurl,create_user,create_voice_user,create_face_user,delete_test
from utils import Logger
from spark.SparkApi import SparkLLM
from voiceLoad.voiceLoad import voiceAdd,voiceVerify,voiceStackBuild
from faceCompareLoad.faceCompare import runFaceCompare
from faceCompareLoad.livingbodyTest import livingbodyTest
import os
from io import BytesIO
import json5
import time
from pydub import AudioSegment
import shutil
from datetime import datetime
from App import app

appid = 'e76d7d8f'
api_secret = 'Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl'
api_key = '990e2770b030441fbcc126c691daf5cd'

domain = "generalv3.5"    # v3.0版本
Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

# 创建SparkLLM对象
llm = SparkLLM(appid, api_key, api_secret, Spark_url, domain, False)

# 定义自定义序列化函数
def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # 将 datetime 对象转换为 ISO 格式的字符串
    raise TypeError(f"Type {type(obj)} not serializable")

@app.route('/save_test', methods=['POST'])
def save_test_handler():
    content = request.json
    #获取当前系统时间
    test_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    test_id = create_test(content['user_name'], content['test_name'], test_time,
                content['problems'],content['answers'], content['evaluation'], content['test_score'], content['test_subjects'])
    return {
        "status": "success",
        "test_id": test_id
    }

@app.route('/get_user_tests', methods=['POST'])
def get_user_tests_handler():
    tests = get_user_tests(request.json['user_name'])
    return {
        "status": "success",
        "tests":tests
    }

@app.route('/get_user_tests_analysis', methods=['POST'])
def get_user_tests_analysis_handler():
    tests_data = get_user_tests_analysis(request.json['user_name'])
    print('tests_data:',tests_data)
    tests_analysis_prompt1 = '''我以以下格式:[
        {'test_name': '生物', 'test_time': datetime.datetime(2024, 7, 19, 5, 32, 16), 'id': 9, 'test_score': 65, 'test_subjects': '"生态学, 分子生物学"'}, {'test_name': '生物', 'test_time': datetime.datetime(2024, 8, 12, 23, 51, 12), 'id': 10, 'test_score': 83, 'test_subjects': '"细胞生物学"'}
    ]给你提供学生测试历史情况。请你根据里面的信息以我指定的格式:{
        "evaluation": "理科思维较强，逻辑清晰。感性分析能力和知识记忆能力相对偏弱。" /*对用户总体测试情况的描述, 此处只是个请你依据实际情况描述, 不要少于15字*/,
        "knowledge_radar": {
            "dimension": ["理性思维","感性思维","分析能力","记忆能力","基础掌握","难度拔高"], /*雷达图的维度, 你需要根据题目的json分析出应该包含哪些维度(6维), 而不是和此处的示例*/
            "score": [100,80,30,10,10,40] /*依次对你给出的维度进行打分*/
        },
        "shortcoming": "给出你的分析出的缺点" /*缺点*/,
        "suggestion": "给出你分析出的意见" /*意见*/
    }返回对用户历史学习情况的解析json。学生测试历史情况如下:'''
    tests_analysis_prompt2 = "。请直接返回解析json, 不要添加任何其他描述"
    question = tests_analysis_prompt1+ str(tests_data) + tests_analysis_prompt2
    print("question:",question)
    tests_analysis = llm.query(question)
    print("tests_analysis:",tests_analysis)
    return {
        "status": "success",
        "tests_analysis":tests_analysis
    }

@app.route('/get_test', methods=['POST'])
def get_test_handler():
    content = request.json
    result = get_test_by_id(content['test_id'])
    print(result,type(result))
    if result is None:
        return jsonify({
            "status": "failed",
            "msg": "test not exists"
        })
    
    response = {
        "status": "success",
        "id": result['id'],
        "user_name": result['user_name'],
        "test_name": result['test_name'],
        "test_time": result['test_time'].isoformat(),
        "test_questions": json5.loads(result['test_questions']),
        "test_score": result['test_score'],
        "test_subjects": result['test_subjects'],
        "user_answers": result['user_answers'],
        "test_result_analysis": result['test_result_analysis']
    }
    return jsonify(response)

@app.route('/delete_test', methods=['POST'])
def delete_test_handler():
    content = request.json
    delete_test(content['test_id'])
    return {
        "status":"success"
    }

@app.route('/get_user_id', methods=['POST'])
def get_user_id_handler():
    content = request.json
    Logger.info(request)
    result = get_user_id(content['username'])
    if(result is None):
        return {
            "status": "failed",
            "msg": "user not exists"
        }
    return {
        "status": "success",
        "user_id": result
    }

@app.route('/password_login', methods=['POST'])
def password_login_handler():
    content = request.json
    Logger.info(request)
    result = get_user_id(content['username'])
    password = get_user_password(content['username'])
    if(result is None):
        return {
            "status": "failed",
            "msg": "用户不存在，请先注册"
        }
    if(result and password is None):
        return {
            "status": "failed",
            "msg": "请先进行密码注册"
        }
    if(result and password != content['password']):
        return {
            "status": "failed",
            "msg": "密码错误"
        }
    return {
        "status": "success",
        "user_id": result
    }

@app.route('/create_user', methods=['POST'])
def password_register():
    content = request.json
    print(request)
    # user_id = create_user(content['username'])
    user_id = create_user(content['username'], content['password'], None, None)
    if user_id is None:
        return {
            "status": "failed",
            "msg": "注册失败"
        }
    return {
        "status": "success",
        "user_id": user_id
    }

@app.route('/save_user_voice', methods=['POST'])
def save_user_voice():
    username = request.form['username']
    print('username:',username)
    voice_file = request.files['voice_file']

    user_directory = './voiceLoad/uservoice_database'
    os.makedirs(user_directory, exist_ok=True)

    # 清空用户目录中的所有文件
    for filename in os.listdir(user_directory):
        file_path = os.path.join(user_directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)  # 删除文件或符号链接
            elif os.path.isdir(file_path):
                # 删除目录及其内容
                for sub_filename in os.listdir(file_path):
                    sub_file_path = os.path.join(file_path, sub_filename)
                    if os.path.isfile(sub_file_path) or os.path.islink(sub_file_path):
                        os.remove(sub_file_path)
                    elif os.path.isdir(sub_file_path):
                        for sub_sub_filename in os.listdir(sub_file_path):
                            sub_sub_file_path = os.path.join(sub_file_path, sub_sub_filename)
                            if os.path.isfile(sub_sub_file_path) or os.path.islink(sub_sub_file_path):
                                os.remove(sub_sub_file_path)
                            elif os.path.isdir(sub_sub_file_path):
                                os.rmdir(sub_sub_file_path)
                        os.rmdir(sub_file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

    wav_path = os.path.join(user_directory, 'voice.wav')
    voice_file.save(wav_path)

    # 用pydub加载文件
    audio = AudioSegment.from_file(wav_path)

    # 设置音频属性
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    # 保存为MP3格式
    mp3_path = os.path.join(user_directory, 'voice.mp3')
    audio.export(mp3_path, format='mp3')

    return jsonify({
        "status": "success",
        "file_path": mp3_path
    })

@app.route('/voiceregister', methods=['POST'])
def voice_register():
    data = request.json
    username = data['username']
    UPLOAD_FOLDER = './voiceLoad/uservoice_database'
    file_path = os.path.join(UPLOAD_FOLDER, "voice.mp3")

    # Step 1: 创建库
    group_name, group_id, group_info = voiceStackBuild(file_path, "1", "xunfeizhijiao", "try")
    featureId = username  # 使用用户名作为特征 ID
    featureinfo = username
    # Step 2: 创建条目
    feature_id = voiceAdd(file_path, group_id, featureId, featureinfo)
    print("feature_id:",feature_id)

    user_id = create_voice_user(username, None, UPLOAD_FOLDER, None)
    print("voice_register_user_id:",user_id)

    return jsonify({
        "group_name": group_name,
        "group_id": group_id,
        "group_info": group_info,
        "feature_id": feature_id
    })

@app.route('/voicelogin', methods=['POST'])
def voice_login():
    content = request.json
    username = content['username']
    print('username:',username)
    user_id = get_user_id(username)
    user_voice_url = get_user_voiceurl(username)
    if user_id == None :
        return {
            "status": "failed",
            "msg": "用户不存在，请先注册"
        }
    if user_id and user_voice_url == None:
        return {
            "status": "failed",
            "msg": "用户声纹未注册，请先注册"
        }
    # Step 1: 验证条目
    score, feature_info, feature_id = voiceVerify('./voiceLoad/uservoice_database/voice.mp3', "1", username)
    print('score:',score)
    print('feature_info:',feature_info)
    print('feature_id:',feature_id)
    # 假设分数大于某个阈值表示成功
    if score > 0.7:  # 阈值可以根据需要调整
        return jsonify({
            "status": "success",
            "score": score,
            "user_id": feature_info
        })
    else:
        return jsonify({
            "status": "failure",
            "score": score,
            "user_id": feature_info,
            "msg": "用户声纹错误，请重试",
        })

@app.route('/save_user_face', methods=['POST'])
def save_user_face():
    username = request.form.get('username')
    photo = request.files.get('photo')
    print(username,photo)

    if not username or not photo:
        return jsonify({'status': 'fail', 'msg': '用户名或照片缺失'}), 400

    # 保存照片
    filename = photo.filename
    photo_directory = "./faceCompareLoad/photos"
    os.makedirs(photo_directory, exist_ok=True)
    clear_directory(photo_directory)
    file_path = os.path.join("./faceCompareLoad/photos", filename)

    photo.save(file_path)

    return jsonify({'status': 'success', 'msg': '人脸上传成功'})

@app.route('/faceregister', methods=['POST'])
def face_register():
    try:
        data = request.json
        username = data['username']
        face_database_path = './database/user_face_database'
        os.makedirs(face_database_path, exist_ok=True)
        user_face_database_path = os.path.join(face_database_path, username)
        os.makedirs(user_face_database_path, exist_ok=True)
        # 源文件路径
        source_file_path = './faceCompareLoad/photos/photo.png'
        # 目标文件路径
        destination_file_path = os.path.join(user_face_database_path, 'photo.png')
        print("destination_file_path: ",destination_file_path)
        # 复制文件
        shutil.copy(source_file_path, destination_file_path)
        
        user_id = create_face_user(username, None, None, destination_file_path)
        print("voice_register_user_id:",user_id)

        return jsonify({
            "status" : "success", "user_id" : user_id, "msg": "人脸注册成功"
        })
    
    except Exception as e:
        print("人脸注册失败:",str(e))
        return jsonify({
            "status" : "failed",
            "msg": "人脸注册失败",
            "error": str(e)  # 将异常信息返回，方便调试
        }), 500  # 返回 HTTP 500 状态码表示服务器错误

@app.route('/facelogin', methods=['POST'])
def face_login():
    content = request.json
    username = content['username']
    print('username:',username)
    user_id = get_user_id(username)
    user_image_url = get_user_imageurl(username)
    if user_id == None :
        return {
            "status": "failed",
            "msg": "用户不存在，请先注册"
        }
    if user_id and user_image_url == None:
        return {
            "status": "failed",
            "msg": "用户未进行过人脸注册"
        }
    # 登陆中人脸图片路径
    ToBeChecked_file_path = './faceCompareLoad/photos/photo.png'
    # 数据库人脸文件路径
    face_database_path = './database/user_face_database'
    user_face_database_path = os.path.join(face_database_path, username)
    database_file_path = os.path.join(user_face_database_path, 'photo.png')

    appid = "e76d7d8f"
    apisecret = "Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl"
    apikey = "990e2770b030441fbcc126c691daf5cd"
    score = runFaceCompare(
        appid=appid,
        apisecret=apisecret,
        apikey=apikey,
        img1_path=ToBeChecked_file_path,
        img2_path=database_file_path,
    )
    living = livingbodyTest(
        appid=appid,
        apisecret=apisecret,
        apikey=apikey,
        img_path=ToBeChecked_file_path,
    )
    print("score,living: ",score, living)
    # score是一个0-1的浮点数，大于0.99？ 可以视为同一个人
    # living为一个布尔变量，false表示未能通过活体检测（用户可能使用照片欺骗人像识别）


    if score > 0.9:  # 阈值可以根据需要调整
        return jsonify({
            "status": "success",
            "score": score,
            "user_id": user_id,
        })
    else:
        return jsonify({
            "status": "failed",
            "score": score,
            "user_id": user_id,
            "msg": "人脸识别失败，请重试",
        })

def clear_directory(directory_path):
        # 清空用户目录中的所有文件
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)  # 删除文件或符号链接
            elif os.path.isdir(file_path):
                # 删除目录及其内容
                for sub_filename in os.listdir(file_path):
                    sub_file_path = os.path.join(file_path, sub_filename)
                    if os.path.isfile(sub_file_path) or os.path.islink(sub_file_path):
                        os.remove(sub_file_path)
                    elif os.path.isdir(sub_file_path):
                        for sub_sub_filename in os.listdir(sub_file_path):
                            sub_sub_file_path = os.path.join(sub_file_path, sub_sub_filename)
                            if os.path.isfile(sub_sub_file_path) or os.path.islink(sub_sub_file_path):
                                os.remove(sub_sub_file_path)
                            elif os.path.isdir(sub_sub_file_path):
                                os.rmdir(sub_sub_file_path)
                        os.rmdir(sub_file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
