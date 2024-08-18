<template>
  
  <div v-if="loading" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-spinner fa-spin"></i> 课件分析中...</h2>
    </div>
  </div>
  <div v-if="pptloading" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-spinner fa-spin"></i> PPT生成中...</h2>
    </div>
  </div>
  <div v-if="quesloading" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-spinner fa-spin"></i> 题目生成中...</h2>
    </div>
  </div>
  <!-- PPT生成弹窗 -->
  <div class="modal" v-show="isUploadModalVisible">
    <div class="modal-content">
      <button class="close-button" @click="isUploadModalVisible=false">
        <i class="fas fa-times"></i> 
      </button>
      <h3><i class="fas fa-file"></i> 选择课件类型</h3>
      <div class="button-group">
        <button @click="selectFile('txt')"><i class="fas fa-file-alt"></i> 上传txt课件</button>
        <button @click="selectFile('docx')"><i class="fas fa-file-word"></i> 上传docx课件</button>
        <button @click="selectFile('image')"><i class="fas fa-image"></i> 上传图片课件</button>
        <button @click="selectFile('audio')"><i class="fas fa-volume-up"></i>  上传音频课件</button>
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
      <h3><i class="fas fa-book-open"></i> 设置题目要求</h3>
      <div class="input-group">
        <label><i class="fas fa-chalkboard-teacher"></i> 学科：</label>
        <input type="text" v-model="questionRequirements.subject" />
      </div>
      <div class="input-group">
        <label><i class="fas fa-book"></i> 知识点：</label>
        <input type="text" v-model="questionRequirements.topic" />
      </div>
      <div class="input-group">
        <label><i class="fas fa-cogs"></i> 其他要求：</label>
        <input type="text" v-model="questionRequirements.other" />
      </div>
      <div class="button-group">
        <button @click="getDownloadProblems_txt"><i class="fas fa-file-alt"></i> 下载TXT格式</button>
        <button @click="getDownloadProblems_docx"><i class="fas fa-file-word"></i> 下载DOCX格式</button>
      </div>
    </div>
  </div>

  <div class="container">
    <div class="header">
      <h1 class="title"><i class="fas fa-chalkboard-teacher"></i>  备课助手</h1>
      <div class="back-button" @click="goBack"> <i class="fas fa-arrow-left"></i></div>
    </div>
    <div class="content">
      <div class="chat-box" ref="chatBox">
        <div v-for="(message, index) in messages" :key="index" :class="{ 'message': true, 'user-message': message.isUser }">
          <p><span v-if="message.isUser">
              <!-- User message with user icon -->
              <i class="fas fa-user"></i> {{ message.text }}
            </span>
            <span v-else>
              <!-- AI message with robot icon -->
              <i class="fas fa-robot"></i> {{ message.text }}
            </span></p>
        </div>
        <div v-if="thinking" class="message ai-thinking">
          <p>AI正在思考...</p>
        </div>
      </div>
      <div class="sidebar">
        <div class="sidebar-content">
          <h2 class="sidebar-title"><i class="fas fa-chalkboard-teacher"></i> 课件分析</h2>
          <input type="file" ref="fileInput" style="display: none" @change="handleFileUpload" />
          <div class="button-group">
            <button @click="isUploadModalVisible=true"><i class="fas fa-upload"></i>上传课件</button>
            <button @click="generatePPT"><i class="fas fa-file-powerpoint"></i>课件转PPT</button>
          </div>
          <div class="file-analysis">
            <h3><i class="fas fa-book-open"></i> 课件预览:</h3>
            <textarea v-if="fileContent" class="file-result" v-model="fileContent" readonly></textarea>
            <textarea v-else class="file-result" placeholder="课件预览" readonly></textarea>
          </div>
          <div class="file-analysis">
            <h3><i class="fas fa-book-open"></i> 课件总结:</h3>
            <textarea v-if="fileSummary" class="file-result" v-model="fileSummary" readonly></textarea>
            <textarea v-else class="file-result" placeholder="课件总结" readonly></textarea>
          </div>
        </div>
        <div class="sidebar-content">
          <h2 class="sidebar-title"><i class="fas fa-question-circle"></i> 智能出题</h2>
          <div class="button-group small-button">
            <button @click="isModalVisible=true"><i class="fas fa-lightbulb"></i> AI生成题目</button>
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
      stream:null,
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
      quesloading:false,
      pptloading:false,
    };
  },
  methods: {
    selectOption(kejian) {
      if(kejian == true){
        if(this.fileSummary==''){
          alert('请在“课件分析”中先上传课件');
        }else{
          this.questionRequirements.other = this.fileSummary;
        }
      }
    },
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
          this.stream = stream; 
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
        url = '/get_txtfileppt';
      } else if (this.fileType === 'docx') {
        url = '/get_docxfileppt';
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
    async getDownloadProblems_txt() {
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
          this.quesloading = true;
          
          // 发送 POST 请求到后端获取试题文本
          const response = await axios.post('/get_downloadproblems_txt', formData, {
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
          this.quesloading = false;
        } catch (error) {
          console.error('Error:', error);
          // 处理错误情况
          this.quesloading = false;
        }
      },
      async getDownloadProblems_docx() {
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
          this.quesloading = true;
          
          // 发送 POST 请求到后端获取试题文本
          const response = await axios.post('/get_downloadproblems_docx', formData, {
            responseType: 'blob' // 响应类型为 Blob
          });

          // Create a Blob object for the .docx file
          const blob = new Blob([response.data], {
            type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
          });

          // Create a URL for the Blob object
          const url = window.URL.createObjectURL(blob);

          // Create an <a> element and trigger download
          const a = document.createElement('a');
          a.href = url;
          a.download = 'problems.docx'; // Use .docx extension for Word document
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);

          // Clean up the URL object
          window.URL.revokeObjectURL(url);

          // 完成下载后，隐藏加载动画
          this.quesloading = false;
        } catch (error) {
          console.error('Error:', error);
          // 处理错误情况
          this.quesloading = false;
        }
      },
      async generatePPT() {
        if(this.fileSummary==''){
          alert("请先上传课件")
        }else{
        // 设置 loading 为 true，显示加载弹窗
        this.pptloading = true;

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
          this.pptloading = false;
        } catch (error) {
          console.error('Error generating PPT:', error);
          this.pptloading = false;
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
  height: 80px;
  padding: 10px;
  background-color: #f6f8f8;
  border-bottom: 1px solid #ccc;
  position: relative;
  margin-top: 10px;
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
  padding: 8px 12px;
  border: 1px solid #1980c5;
  border-radius: 5px;
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
  // background: linear-gradient(45deg, #A1CFFF, #B3E5FF, #CDEFFF, #D1F5FF);
  // background-size: 400% 400%;
  // animation: gradientAnimation 4s ease infinite;
  background-image: url('../../../assets/blackboard.jpg'); /* 背景图片的路径 */
  //background-size: cover; /* 让背景图片充满容器 */
  background-size: 110% 100%; /* 背景高度适应容器，宽度按比例缩放 */
  background-position: center; /* 居中显示背景图片 */
  background-repeat: no-repeat; /* 禁止背景图片重复 */
}
@keyframes gradientAnimation {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.sidebar {
  flex: 1;
  padding: 5px;
  background: linear-gradient(-45deg, #A1CFFF, #B3E5FF, #CDEFFF, #D1F5FF);
  background-size: 100% 100%;
  animation: gradientAnimation 3s ease infinite;
  overflow-y: auto;
}
@keyframes gradientAnimation {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.sidebar-content {
  min-height: 130px;
  margin-bottom:5px;
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
  color: #0026ff;
}

.button-group {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
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
  margin-top: 0px;
}

.file-analysis h3 {
  color: #0026ff;
  margin-bottom: 5px;
  font-size: 0.9em;
  font-weight: bold;
}

.file-result {
  width: 90%;
  height: 70px;
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
  flex: 1;
  height: 40px;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 5px;
  margin-left: 2px;
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
  padding: 20px;
  border-radius: 5px;
  width: 520px;
  max-width: 90%;
  text-align: center;
  position: relative;
  background: linear-gradient(-45deg, #A1CFFF, #B3E5FF, #CDEFFF, #D1F5FF);
  background-size: 300% 300%;
  animation: gradientAnimation 6s ease infinite;

  h3{
    color:#0026ff;
    font-size: 1.7em;
    font-weight: bold;
    margin-top: -9px;
  }

  .button-group {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
  }

  .button-group button {
    flex: 1;
    margin: 0 10px;
    padding: 10px;
    background-color: #4862f8;
    color: #fff;
    border: none;
    border-radius: 5px;
    font-size: 1em;
    cursor: pointer;
  }

  .button-group button i {
    margin-right: 8px;
  }

  .button-group button:hover {
    background-color: #374abd;
  }

}
@keyframes gradientAnimation {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
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
  color:#0026ff;
  font-size: 1.3em;
  font-weight: bold;
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
  z-index: 2000;
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
