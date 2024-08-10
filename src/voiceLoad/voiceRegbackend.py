import json5
from flask import Flask, request, jsonify
from flask_cors import CORS

from voiceCompare import voiceAdd,voiceVerify,voiceStackBuild

app = Flask(__name__)
CORS(app)

@app.route('/voiceload', methods=['POST'])
def voiceload():
    data = request.json
    file_path = data['file_path']

    # Step 1: 创建库
    group_name, group_id, group_info = voiceStackBuild(file_path, "1", "xunfeizhijiao", "try")

    featureId = "一个递增的量"
    featureinfo = "用户名"
    # 这里需要用户在注册时输入用户名
    # Step 2: 创建条目
    feature_id = voiceAdd(file_path, group_id, featureId, featureinfo)

    # Step 3: 验证条目
    # 这里需要用户在登陆时输入用户名
    score, feature_info, feature_id = voiceVerify(file_path, group_id, feature_id)

    return jsonify({
        "group_name": group_name,
        "group_id": group_id,
        "group_info": group_info,
        "feature_id": feature_id,
        "score": score,
        "feature_info": feature_info
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

