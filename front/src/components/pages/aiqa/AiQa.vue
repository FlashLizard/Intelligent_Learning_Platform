<template>
  <div class="container">
    <div class="header">
      <h1 class="title">AI教育辅导</h1>
      <div class="back-button" @click="goBack">返回</div>
    </div>
    <div class="content">
      <div class="chat-box" ref="chatBox">
        <div v-for="(message, index) in messages" :key="index" :class="{ 'message': true, 'user-message': message.isUser }">
          <p>{{ message.text }}</p>
        </div>
        <div v-if="thinking" class="message ai-thinking">
          <p>AI正在思考...</p>
        </div>
      </div>
      <div class="sidebar">
        <div class="sidebar-content">
          <h2 class="sidebar-title">历史问题</h2>
          <div v-for="(question, index) in questions" :key="index" class="question-item">
            <p>{{ question }}</p>
          </div>
        </div>
      </div>
    </div>
    <div class="input-container">
      <input class="input-box" type="text" v-model="inputValue" @keypress.enter="sendMessage" placeholder="输入消息..." />
      <button class="send-button" @click="sendMessage">发送</button>
      <button v-if="!isRecording" class="voice-button" @click="startVoiceRecognition">🎤 开始录音</button>
      <button v-else class="voice-button" @click="stopVoiceRecognition">🛑 结束录音</button>
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
      inputValue: '',
      thinking: false,
      mediaRecorder: null,
      audioChunks: [],
      isRecording: false,
    };
  },
  methods: {
    sendMessage() {
      if (this.inputValue.trim() === '') return;
      this.messages.push({ text: this.inputValue, isUser: true });
      this.questions.push(this.inputValue);
      const userMessage = this.inputValue;
      this.inputValue = '';

      // Display thinking message
      this.thinking = true;

      // 向后端发送请求
      axios.post('http://localhost:5000/get_chatanswer', {
        message: userMessage
      })
      .then((res) => {
        this.thinking = false;
        this.messages.push({ text: res.data, isUser: false });
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
            axios.post('http://localhost:5000/get_chatvoiceanswer', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            })
            .then((res) => {
              this.thinking = false;
              this.messages.push({ text: res.data['question'], isUser: true });
              this.messages.push({ text: res.data['answer'], isUser: false });
              this.questions.push(res.data.question);
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
        this.isRecording = false;

        // Stop all tracks from the media stream
        if (this.stream) {
          this.stream.getTracks().forEach(track => track.stop());
        }
      }
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
  height: 50px;
  padding: 10px;
  background-color: #aaffff;
  border-bottom: 1px solid #ccc;
  position: relative;
  margin-top: 10px; /* 调整标题距离顶部的距离 */
}

.title {
  font-size: 26px;
  font-weight: bold;
}

.back-button {
  font-weight: bold;
  position: absolute;
  right: 30px;
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #080b0d;
  padding: 8px 12px; /* 添加内边距 */
  border: 1px solid #080b0d; /* 添加边框 */
  border-radius: 5px; /* 添加圆角 */
  background-color: transparent; /* 使背景透明 */
  transition: all 0.3s ease; /* 添加过渡效果 */
}

.back-button:hover {
  background-color: #080b0d; /* 鼠标悬停时改变背景颜色 */
  color: #fff; /* 鼠标悬停时改变文字颜色 */
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
}

.sidebar {
  flex: 1;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.8);
  overflow-y: hidden;
}

.sidebar-content {
  text-align: center;
}

.sidebar-title {
  font-weight: bold;
  margin-bottom: 10px;
}

.question-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f0f0f0;
  border-radius: 5px;
}

.message {
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 5px;
  background-color: #fff;
  max-width: 70%;
}

.user-message {
  align-self: flex-end;
  background-color: #d1f0d1;
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
</style>
