from flask import Flask
import subprocess

#TODO 目前这个页面没办法正常运行
app = Flask(__name__)

@app.route('/')
def run_scripts():
    try:
        subprocess.run(["python", "reptile/from_coursera.py"], check=True)
        subprocess.run(["python", "reptile/from_edx.py"], check=True)
        return "执行成功！"
    except subprocess.CalledProcessError as e:
        return f"执行脚本时出错: {e}"

if __name__ == '__main__':
    app.run(debug=True)