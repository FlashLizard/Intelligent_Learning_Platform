import os

from Ifasr_app import app

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_ANS'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_AUDIO'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    app.run()





