from AIPPT_app import app
import os

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_ANS'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    app.run(debug=True)

