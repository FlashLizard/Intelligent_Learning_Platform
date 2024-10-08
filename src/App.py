from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.json.ensure_ascii = False
CORS(app)


if __name__ == '__main__':
    from ai_test_system.ATS_backend import *
    from ai_test_system.TestDownload import *
    from AI_StudyResource_Recommend.recommend_backend import *
    from audio_to_txt.audio_to_txt_backend import *
    from generate_ppt.ppt_backend import *
    from aiqa.AIQA_backend import *
    from database.Database_backend import *
    from docClassify.docClassifybackend import *
    app.run(host='0.0.0.0', port=5000)