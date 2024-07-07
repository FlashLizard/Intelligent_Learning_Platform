from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.json.ensure_ascii = False
CORS(app)


if __name__ == '__main__':
    from ai_test_system.ATS_backend import *
    from database.Database_backend import *
    app.run(host='0.0.0.0', port=5000)