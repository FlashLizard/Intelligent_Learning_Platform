<template>
  <!-- PPT生成弹窗 -->
  <div class="modal" v-show="isUploadModalVisible">
    <div class="modal-content">
      <button class="close-button" @click="isUploadModalVisible=false">
        <i class="fas fa-times"></i> 
      </button>
      <h3>选择课件类型</h3>
      <div class="button-group">
        <button @click="selectFile('txt')">上传txt课件</button>
        <button @click="selectFile('image')">上传课件图片</button>
        <button @click="selectFile('audio')">上传课件音频</button>
      </div>
    </div>
  </div>

  <!-- 弹窗 -->
  <div class="modal" v-show="isModalVisible">
    <div class="modal-content">
      <!-- 关闭按钮 -->
      <button class="close-button" @click="isModalVisible=false">
        <i class="fas fa-times"></i> <!-- 使用 Font Awesome 的关闭图标 -->
      </button>

      <!-- 设置题目要求 -->
      <h3>设置题目要求</h3>
      <div class="input-group">
        <label>学科：</label>
        <input type="text" v-model="questionRequirements.subject" />
      </div>
      <div class="input-group">
        <label>知识点：</label>
        <input type="text" v-model="questionRequirements.topic" />
      </div>
      <div class="input-group">
        <label>其他要求：</label>
        <input type="text" v-model="questionRequirements.other" />
      </div>
      <div class="input-group">
        <label>是否依据课件生成题目：</label>
        <div>
          <button @click="selectOption(true)" :class="{ selected: questionRequirements.useClassContent === true }">是</button>
          <button @click="selectOption(false)" :class="{ selected: questionRequirements.useClassContent === false }">否</button>
        </div>
      </div>
      <button @click="getDownloadProblems">下载试卷</button>
    </div>
  </div>

  <!-- 加载中弹窗 -->
  <div v-if="loading" class="loading-dialog">
    <div class="loading-content">
      <h2>AI思考中...</h2>
    </div>
  </div>

  <div class="container">
    <div class="header">
      <h1 class="title">备课助手</h1>
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
          <h2 class="sidebar-title">课件分析</h2>
          <input type="file" ref="fileInput" style="display: none" @change="handleFileUpload" />
          <div class="button-group">
            <button @click="isUploadModalVisible=true">上传课件</button>
            <button @click="generatePPT">课件转PPT</button>
          </div>
          <div class="file-analysis">
            <h3>课件预览:</h3>
            <textarea v-if="fileContent" class="file-result" v-model="fileContent" readonly></textarea>
            <textarea v-else class="file-result" placeholder="课件预览" readonly></textarea>
          </div>
          <div class="file-analysis">
            <h3>课件总结:</h3>
            <textarea v-if="fileSummary" class="file-result" v-model="fileSummary" readonly></textarea>
            <textarea v-else class="file-result" placeholder="课件总结" readonly></textarea>
          </div>
        </div>
        <div class="sidebar-content">
          <h2 class="sidebar-title">智能出题</h2>
          <div class="button-group small-button">
            <button @click="isModalVisible=true">AI生成题目</button>
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
      isUploadModalVisible: false,
      messages: [
        { text: '您好，我是教师备课AI小助手，有什么我可以帮忙的吗？', isUser: false }
      ],
      questions: [],
      inputValue: '',
      thinking: false,
      mediaRecorder: null,
      audioChunks: [],
      isRecording: false,
      fileType: '',
      fileContent: '',
      fileSummary: '',
      isModalVisible: false,
      questionRequirements: {
        subject: '',
        topic: '',
        other: '无',
        useClassContent: false
      },
      loading: false, // 增加loading控制生成题目弹窗
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
      axios.post('/get_chatanswer', {
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
            axios.post('/get_chatvoiceanswer', formData, {
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
    },
    selectFile(type) {
      this.fileType = type;
      this.$refs.fileInput.click();
      this.isUploadModalVisible=false;
    },
    handleFileUpload(event) {
      this.loading = true;
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      let url = '';
      if (this.fileType === 'txt') {
        url = '/get_fileppt';
      } else if (this.fileType === 'image') {
        url = '/get_imageppt';
      } else if (this.fileType === 'audio') {
        url = '/get_audioppt';
      }

      axios.post(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      .then((res) => {
        this.fileContent = res.data.word.slice(0, 15) + '……';
        this.fileSummary = res.data.ans;
        this.loading = false;
      })
      .catch((err) => {
        this.loading = false;
        console.error(err);
      });
    },
    async getDownloadProblems() {
        const formData = {
          subjects: [
            this.questionRequirements.subject || '',
            this.questionRequirements.topic || this.questionRequirements.subject
          ],
          time: 10, // Example time in minutes
          min_difficulty: 3,
          max_difficulty: 8,
          type: ["single_choice", "judgement",'fillin'],
          others: this.questionRequirements.other || '无'
        };
        console.log(formData)
        try {
          this.loading = true;

          // 发送 POST 请求到后端获取试题文本
          const response = await axios.post('/get_downloadproblems', formData, {
            responseType: 'blob' // 响应类型为 Blob
          });

          // 从响应中获取 Blob 数据
          const blob = new Blob([response.data], { type: 'text/plain' });

          // 创建一个 URL 对象，用于创建下载链接
          const url = window.URL.createObjectURL(blob);

          // 创建一个 <a> 标签，设置下载链接并自动触发下载
          const a = document.createElement('a');
          a.href = url;
          a.download = 'problems.txt';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);

          // 清理 URL 对象
          window.URL.revokeObjectURL(url);

          // 完成下载后，隐藏加载动画
          this.loading = false;
        } catch (error) {
          console.error('Error:', error);
          // 处理错误情况
          this.loading = false;
        }
      },
      async generatePPT() {
        if(this.fileSummary==''){
          alert("请先上传课件")
        }else{
        // 设置 loading 为 true，显示加载弹窗
        this.loading = true;

        // 构建请求数据
        const requestData = {
          text: this.fileSummary,
          theme: 'auto',
          isCardNote: 1
        };

        try {
          // 发送请求
          const response = await axios.post('/downloadppt', requestData, {
            responseType: 'blob' // 设置响应类型为 Blob
          });

          // 处理响应，打开下载链接
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', 'generated_ppt.ppt');
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);

          // 下载完毕，设置 loading 为 false，隐藏加载弹窗
          this.loading = false;
        } catch (error) {
          console.error('Error generating PPT:', error);
          this.loading = false;
        }}
      },
  }
};
</script>

<style lang="scss" scoped>
.container {
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
  height: 100vh;
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
  margin-top: 10px;
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
  padding: 8px 12px;
  border: 1px solid #080b0d;
  border-radius: 5px;
  background-color: transparent;
  transition: all 0.3s ease;
}

.back-button:hover {
  background-color: #080b0d;
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
}

.sidebar {
  flex: 1;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.9);
  overflow-y: auto;
}

.sidebar-content {
  margin-bottom: 30px;
}

.sidebar-title {
  font-weight: bold;
  margin-bottom: 10px;
}

.button-group {
  display: flex;
  justify-content: space-between;
}

.button-group.small-button {
  justify-content: flex-start;
}

.button-group button {
  flex: 1;
  padding: 10px;
  margin-right: 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  background-color: #1890ff;
  color: #fff;
  transition: background-color 0.3s ease;
}

.button-group button:last-child {
  margin-right: 0;
}

.button-group button:hover {
  background-color: #0056b3;
}

.file-analysis {
  margin-top: 20px;
}

.file-analysis h3 {
  margin-bottom: 5px;
  font-size: 0.8em;
}

.file-result {
  width: 90%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #fff;
  resize: none;
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

.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 5px;
  width: 400px;
  max-width: 90%;
  text-align: center;
  position: relative;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 0.5rem 1rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.input-group {
  margin-bottom: 1rem;
}

.input-group label {
  margin-right: 10px;
}

.input-group input {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.input-group div {
  margin-top: 0.5rem;
}

.selected {
  background-color: #007bff;
  color: #fff;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.ppt-button {
  margin-left: 10px;
  padding: 8px 12px;
  background-color: #1890ff;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.ppt-button:hover {
  background-color: #0056b3;
}

.button-group {
  display: flex;
  justify-content: space-between;
}

.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 5px;
  width: 400px;
  max-width: 90%;
  text-align: center;
  position: relative;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 0.5rem 1rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.button-group button {
  flex: 1;
  padding: 10px;
  margin-right: 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  background-color: #1890ff;
  color: #fff;
  transition: background-color 0.3s ease;
}

.button-group button:last-child {
  margin-right: 0;
}

.button-group button:hover {
  background-color: #0056b3;
}
</style>
