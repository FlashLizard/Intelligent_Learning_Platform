<template>
  <div class="container">
    <div class="header">
      <h1 class="title"><i class="fas fa-book-open"></i> AI教育辅导</h1>
      <div class="back-button" @click="goBack"><i class="fas fa-arrow-left"></i></div>
    </div>
    <div class="content">
      <div class="chat-box" ref="chatBox">
        <div v-for="(message, index) in messages" :key="index" :class="{ 'message': true, 'user-message': message.isUser }">
          <p>
            <span v-if="message.isUser">
              <!-- User message with user icon -->
              <i class="fas fa-user"></i> {{ message.text }}
            </span>
            <span v-else>
              <!-- AI message with robot icon -->
              <i class="fas fa-robot"></i> {{ message.text }}
            </span>
          </p>
        </div>
        <div v-if="thinking" class="message ai-thinking">
          <p>AI正在思考...</p>
        </div>
      </div>
      <div class="sidebar">
        <div class="sidebar-content">
          <h2 class="sidebar-title">历史问题</h2>
          <div v-for="(question, index) in questions" :key="index" class="question-item" @click="showQuestionDialog(index)">
            <p>{{ question }}</p>
          </div>
        </div>
      </div>
    </div>
    <div class="input-container">
      <i class="fas fa-comment fa-lg"></i>
      <input class="input-box" type="text" v-model="inputValue" @keypress.enter="sendMessage" placeholder="输入消息..." />
      <button class="send-button" @click="sendMessage">发送</button>
      <button v-if="!isRecording" class="voice-button" @click="startVoiceRecognition">🎤 开始录音</button>
      <button v-else class="voice-button" @click="stopVoiceRecognition">🛑 结束录音</button>
    </div>

    <div v-if="dialogVisible" class="dialog-overlay">
      <div class="dialog-box">
        <button @click="dialogVisible = false" class="close-button">
          <i class="fas fa-times-circle"></i>
        </button>
        <h3 class="dialog-title"><i class="fas fa-question-circle"></i> 问题详情</h3>
        <div class="scrollable-content">
          <p><i class="fas fa-comments"></i> <strong>问题:</strong></p>
          <div class="scroll-box">
            <p>{{ selectedQuestion }}</p>
          </div>
          <p><i class="fas fa-reply"></i> <strong>答案:</strong></p>
          <div class="scroll-box">
            <p>{{ selectedAnswer }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      messages: [
        { text: '您好，我是教育辅导AI小助手，有什么我可以帮忙的吗？', isUser: false }
      ],
      questions: [],
      answers: [],
      inputValue: '',
      thinking: false,
      mediaRecorder: null,
      stream:null,
      audioChunks: [],
      isRecording: false,
      dialogVisible: false, // 控制弹窗显示
      selectedQuestion: '', // 当前选中的问题
      selectedAnswer: '', // 当前选中的答案
    };
  },
  methods: {
    sendMessage() {
      if (this.inputValue.trim() === '') return;
      this.messages.push({ text: this.inputValue, isUser: true });
      const userMessage = this.inputValue;

      // Display thinking message
      this.thinking = true;
      // 向后端发送请求
      axios.post('/get_chatanswer', {
        message: userMessage
      })
      .then((res) => {
        this.thinking = false;
        this.messages.push({ text: res.data, isUser: false });
        this.answers.push(res.data)
        this.questions.push(this.inputValue);
        this.inputValue = '';
      })
      .catch((err) => {
        this.thinking = false;
        console.error(err);
      });
    },
    startVoiceRecognition() {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('您的浏览器不支持语音识别功能。');
        return;
      }

      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          this.mediaRecorder = new MediaRecorder(stream);
          this.mediaRecorder.start();
          this.stream = stream;
          this.isRecording = true;

          this.mediaRecorder.ondataavailable = event => {
            this.audioChunks.push(event.data);
          };

          this.mediaRecorder.onstop = () => {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            this.audioChunks = [];
            const formData = new FormData();
            formData.append('audio', audioBlob, 'voice.wav');

            // Display thinking message
            this.thinking = true;

            // 向后端发送请求
            axios.post('/get_chatvoiceanswer', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })
            .then((res) => {
              this.thinking = false;
              this.messages.push({ text: res.data['question'], isUser: true });
              this.messages.push({ text: res.data['answer'], isUser: false });
              this.questions.push(res.data['question']);
              this.answers.push(res.data['answer'])
            })
            .catch((err) => {
              this.thinking = false;
              console.error(err);
            });
          };
        })
        .catch(error => {
          console.error('getUserMedia error:', error);
        });
    },
    stopVoiceRecognition() {
      if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.stop();
        this.mediaRecorder = null;
        this.isRecording = false;

        if (this.stream) {
          this.stream.getTracks().forEach(track => track.stop());
          this.stream = null;
        }
      }
    },
    showQuestionDialog(index) {
      // 获取对应的问题和答案
      const question = this.questions[index];
      const answer = this.answers[index] || '答案不可用';

      // 设置选中的问题和答案
      this.selectedQuestion = question;
      this.selectedAnswer = answer;

      // 显示弹窗
      this.dialogVisible = true;
    },
    goBack() {
      this.$router.back();
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  background-image: url("https://bpic.588ku.com/back_pic/19/03/25/e99eca2587d8c5c78feddad37168cb01.jpg");
  background-repeat: no-repeat;
  background-size: cover;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.header {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  padding: 10px;
  background-color: #aaffff;
  border-bottom: 1px solid #ccc;
  position: relative;
  margin-top: 0px; /* 调整标题距离顶部的距离 */
  background-image: url('../../../assets/10.png'); /* 背景图片的路径 */
  background-size: cover; /* 让背景图片充满容器 */
  background-position: center; /* 居中显示背景图片 */
  background-repeat: no-repeat; /* 禁止背景图片重复 */
}

.title {
  font-size: 30px;
  font-weight: bold;
  color: #0026ff;
}

.back-button {
  font-weight: bold;
  position: absolute;
  right: 30px;
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #f2f2f3;
  padding: 8px 12px; /* 添加内边距 */
  border: 1px solid #0474de; /* 添加边框 */
  border-radius: 5px; /* 添加圆角 */
  background-color:  #007bff;
  transition: all 0.3s ease;
}

.back-button:hover {
  background-color: #0056b3;
  color: #fff;
}

.content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.chat-box {
  flex: 3;
  padding: 10px;
  overflow-y: scroll;
  background-image: url('../../../assets/blackboard.jpg'); /* 背景图片的路径 */
  //background-size: cover; /* 让背景图片充满容器 */
  background-size: 110% 100%; /* 背景高度适应容器，宽度按比例缩放 */
  background-position: center; /* 居中显示背景图片 */
  background-repeat: no-repeat; /* 禁止背景图片重复 */
}

.sidebar {
  flex: 1;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.8);
  overflow-y: hidden;
}

.sidebar-content {
  overflow-y: scroll;
  height: 96%;
  text-align: center;
  padding:10px;
  border: 4px solid transparent;
  border-radius: 5px !important;
  animation: border-rotation 3s linear infinite; 
}
@keyframes border-rotation {
  0% {
    border-image: linear-gradient(0deg, #2389d7, #add8e6, #3f62ee) 1;
  }
  25% {
    border-image: linear-gradient(90deg, #2389d7, #add8e6, #3f62ee) 1;
  }
  50% {
    border-image: linear-gradient(180deg, #2389d7, #add8e6, #3f62ee) 1;
  }
  75% {
    border-image: linear-gradient(270deg, #2389d7, #add8e6, #3f62ee) 1;
  }
  100% {
    border-image: linear-gradient(360deg, #2389d7, #add8e6, #3f62ee) 1;
  }
}

.sidebar-title {
  font-weight: bold;
  margin-bottom: 10px;
  color:#0026ff;
  border-bottom: 2.2px solid #007bff;
  margin-top: -5px;
}

.question-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #8ac4fa;
  border-radius: 5px;
}
.question-item:hover {
  background-color: #5fa9ed;
}

.message {
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 5px;
  // background-color: #9be08f;
  background-color: rgba(155, 224, 143, 0.8);
  max-width: 70%;
}

.user-message {
  align-self: flex-end;
  // background-color: #d1f0d1;
  background-color: rgba(209, 240, 209, 0.8);
  font-weight: bold;
}

.ai-thinking p {
  animation: blink 1s infinite;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.input-container {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: #fff;
  border-top: 1px solid #ccc;
}

.input-box {
  margin-left: 2px;
  flex: 1;
  height: 40px;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 5px;
}

.send-button {
  margin-left: 10px;
  padding: 10px;
  background-color: #1890ff;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.voice-button {
  margin-left: 10px;
  padding: 10px;
  background-color: #ff5733;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-box {
  background-color: #e0f7fa; /* 浅蓝色背景 */
  padding: 20px;
  border-radius: 10px;
  width: 400px;
  max-width: 90%;
  font-family: 'Arial', sans-serif; /* 自定义字体 */
  color: #004d40; /* 深绿色字体 */
}

.dialog-title {
  font-size: 1.5em;
  margin-top: -20px;
  margin-bottom: 10px;
  color: #00796b; /* 标题颜色 */
}

.scrollable-content {
  margin-bottom: 20px;
}

.scroll-box {
  background-color: #b2ebf2; /* 浅蓝色背景 */
  padding: 10px;
  max-height: 150px;
  overflow-y: auto; /* 启用纵向滚动 */
  border-radius: 5px;
  border: 1px solid #00796b;
  font-size: 1em;
  color: #004d40;
}

.close-button {
  position: relative;
  top: 10px;
  left: 370px;
  background: none;
  border: none;
  color: #004d40;
  font-size: 1.5em;
  cursor: pointer;
}

.close-button i {
  pointer-events: none; /* 防止点击仅作用于图标而不作用于整个按钮 */
}

.close-button:hover {
  color: #00796b;
}

</style>
