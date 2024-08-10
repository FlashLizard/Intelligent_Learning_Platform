import json5
from flask import Flask, request, jsonify
from flask_cors import CORS

from faceCompare import runFaceCompare


appid = "e76d7d8f"
apisecret = "Y2Y2ODc2OGQyOWFjMWZhY2JkOTllMDVl"
apikey = "990e2770b030441fbcc126c691daf5cd"


app = Flask(__name__)
CORS(app)

@app.route('/faceload', methods=['POST'])
def faceload():
    data = request.json
    img_1 = data['img1']
    img_2 = data['img2']
    # TODO 这里前端需要实现（注册时存储照片，登录时保存照片）
    # TODO  填充用户上传的照片路径img1
    # TODO  填充用户报存的照片路径img2

    score = runFaceCompare(
        appid=appid,
        apisecret=apisecret,
        apikey=apikey,
        img1_path=img_1,
        img2_path=img_2
    )

    return jsonify({
        "score": score
    })   # 分数是一个0-1的浮点数，大于0.99？ 可以视为同一个人


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

