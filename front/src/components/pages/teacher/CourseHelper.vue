<template>
  <div class="container">
    <!-- 加载中弹窗 -->
    <div v-if="recordloading" class="loading-dialog">
      <div class="loading-content">
        <h2><i class="fas fa-spinner fa-spin"></i> 课堂总结生成中...</h2>
      </div>
    </div>
    <div v-if="classtext" class="class-dialog">
      <div class="class-content summary-container">
        <button class="close-button" @click="closeClassSummary">
          <i class="fas fa-times"></i>
        </button>
        <h3>课堂概述</h3>
        <div class="summary-content">
          <p v-for="line in classtext.split('\n')" :key="line">{{ line }}</p>
        </div>
      </div>
    </div>
    <!-- 头部 -->
    <header class="header">
      <h1>随堂助手</h1>
      <button class="back-button" @click="goBack">返回</button>
    </header>

    <!-- 主内容 -->
    <div class="content">
      <div class="main-content">
        <div class="left">
          <!-- 课堂控制 -->
          <div class="classroom-controls">
            <button @click="classStarted ? endClass() : startClass()">
              {{ classStarted ? '结束课堂' : '开始课堂' }}
            </button>
            <span>{{ formatCountdownTime }}</span>
          </div>
          
          <!-- 视频画布 -->
          <canvas :class="{ 'video-canvas': !isLoading, 'hide-canvas': isLoading }" ref="canvas"></canvas>

          <!-- 加载动画 -->
          <div v-if="isLoading" class="loading-spinner"></div>

        </div>
        
        <div class="right">
          <!-- 右侧上部 -->
          <div class="top">
            <div class="section">
              <h2>点答器</h2>
              <div class="button-container">
                <button @click="selectUploadFile">上传学生名单</button>
                <button @click="randomSelectStudent">随机抽取学生</button>
              </div>
              
              <!-- 隐藏的文件输入框 -->
              <input type="file" ref="fileInput" @change="handleDDFileUpload" style="display: none" />
              
              <!-- 显示学生名字的模态框 -->
              <div v-if="showDDModal" class="DDmodal">
                <div class="DDmodal-content">
                  <span class="DDclose" @click="closeDDModal">
                    <i class="fas fa-times"></i>
                  </span>
                  <h2>学生名单</h2>
                  <ul class="student-list">
                    <li v-for="(student, index) in students" :key="index" :class="{ selected: index === selectedStudentIndex }">{{ student }}</li>
                  </ul>
                  <button @click="startSelection">抽取学生</button>
                </div>
              </div>
              <!-- 警告模态框 -->
              <div v-if="showDDAlertModal" class="alert-modal">
                <div class="alert-modal-content">
                  <span class="alert-close" @click="closeDDAlertModal">
                    <i class="fas fa-times"></i>
                  </span>
                  <p>学生名单为空，请先上传学生名单。</p>
                  <button @click="closeDDAlertModal">确定</button>
                </div>
              </div>
            </div>

            <div class="section">
              <h2>随堂测试</h2>
              <div class="button-container">
                <button @click="openModal">AI生成题目</button>
              </div>
            </div>
          </div>
          
          <!-- 右侧下部 -->
          <div class="bottom">
            <h2>AI教育辅导</h2>
            <div class="chat-box" ref="chatBox">
              <div v-for="(message, index) in messages" :key="index" :class="{ 'message': true, 'user-message': message.isUser }">
                <p :class="{'user-message-bubble': message.isUser, 'assistant-message-bubble': !message.isUser}">{{ message.text }}</p>
              </div>
            </div>
            <div class="input-container">
              <input class="input-box" type="text" v-model="inputValue" @keypress.enter="sendMessage" placeholder="输入消息..." />
              <button class="voice-button" @click="toggleVoiceInput">{{ isaskRecording ? '🛑' : '🎤' }}</button>
              <button class="send-button" @click="sendMessage">发送</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 弹窗 -->
    <div class="modal" v-show="isModalVisible">
      <div class="modal-content">
        <!-- 关闭按钮 -->
        <button class="close-button" @click="closeModal">
          <i class="fas fa-times"></i> <!-- 使用 Font Awesome 的关闭图标 -->
        </button>
        
        <!-- 设置题目要求 -->
        <h3>设置测试要求</h3>
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
        <button @click="generateQuestions">生成测试</button>
      </div>
    </div>
    <!-- 加载中弹窗 -->
    <div v-if="loading" class="loading-dialog">
      <div class="loading-content">
        <h2>题目生成中...</h2>
      </div>
    </div>
  </div>
  <!-- 开始课堂 -->
  <div class="modal" v-show="isStartClassModalVisible">
    <div class="modal-content">
      <button class="close-button" @click="closeStartClassModal">
        <i class="fas fa-times"></i> <!-- 使用 Font Awesome 的关闭图标 -->
      </button>
      <h3>课堂信息</h3>
      <div class="input-group">
        <label>学科：</label>
        <input type="text" v-model="questionRequirements.subject" />
      </div>
      <div class="input-group">
        <label>课堂时间：</label>
        <div class="time-options">
          <button @click="selectTime(1)" :class="{ selected: questionRequirements.classTime === 30 }">30分钟</button>
          <button @click="selectTime(45)" :class="{ selected: questionRequirements.classTime === 45 }">45分钟</button>
          <button @click="selectTime(60)" :class="{ selected: questionRequirements.classTime === 60 }">60分钟</button>
          <button @click="selectTime(120)" :class="{ selected: questionRequirements.classTime === 120 }">120分钟</button>
        </div>
      </div>
      <div class="input-group">
        <label>是否录音以生成课堂总结</label>
        <div>
          <button @click="selectOption(true)" :class="{ selected: questionRequirements.useClassContent === true }">是</button>
          <button @click="selectOption(false)" :class="{ selected: questionRequirements.useClassContent === false }">否</button>
        </div>
      </div>
      <button @click="confirmstartClass">开始上课</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { openDB } from 'idb';

export default {
  data() {
    return {
      isLoading: false,
      isRecording: false,
      mediaRecorder: null,
      videoChunks: [],
      audioChunks: [],
      classStarted: false,
      startTime: 0,
      elapsed: 0,
      timer: null,
      messages: [
        { text: '您好，我是教育辅导AI小助手，有什么我可以帮忙的吗？', isUser: false }
      ],
      inputValue: '',
      isStartClassModalVisible: false,
      isModalVisible: false,
      questionRequirements: {
        subject: '',
        topic: '',
        other: '无',
        useClassContent: false
      },
      loading: false, // 增加loading控制生成题目弹窗
      isaskRecording: false,
      recognition: null,
      classTime:0,
      countdownTime: 0, // 倒计时时间，单位秒
      countdownTimer: null, // 倒计时定时器
      questions: [],
      students: [], // 存储学生名字的数组
      showDDModal: false, // 控制点答模态框显示
      selectedStudentIndex: 0,
      showDDAlertModal: false, // 控制警告模态框显示
      classtext: null,
      recordloading:false,
    };
  },
  computed: {
    progress() {
      if (!this.classStarted) return 0;
      let elapsedSeconds = Math.floor((Date.now() - this.startTime) / 1000);
      let totalTime = this.classTime; // Total class time in seconds

      // Calculate progress percentage
      let progressPercentage = (elapsedSeconds * 100 / totalTime);
      console.log(elapsedSeconds,totalTime,progressPercentage)
      // Clamp the progress between 0 and 100
      return Math.min(100, progressPercentage);
    },
    progressText() {
      const elapsedSeconds = Math.floor((Date.now() - this.startTime) / 1000);
      const hours = Math.floor(elapsedSeconds / 3600);
      const minutes = Math.floor((elapsedSeconds % 3600) / 60);
      const seconds = elapsedSeconds % 60;

      // Calculate total elapsed time in seconds
      const totalElapsedSeconds = hours * 3600 + minutes * 60 + seconds;

      // Calculate remaining time in seconds
      const remainingSeconds = this.countdownTime - totalElapsedSeconds;

      // Convert remaining seconds to HH:mm:ss format
      const countdownHours = Math.floor(remainingSeconds / 3600);
      const countdownMinutes = Math.floor((remainingSeconds % 3600) / 60);
      const countdownSeconds = remainingSeconds % 60;

      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')} / ${countdownHours.toString().padStart(2, '0')}:${countdownMinutes.toString().padStart(2, '0')}:${countdownSeconds.toString().padStart(2, '0')}`;
    },
    formatCountdownTime() {
      let hours = Math.floor(this.countdownTime / 3600); // 小时数
      let minutes = Math.floor((this.countdownTime % 3600) / 60); // 分钟数
      let seconds = this.countdownTime % 60; // 秒数

      // 使用 padStart 方法确保显示两位数的格式
      hours = hours.toString().padStart(2, '0');
      minutes = minutes.toString().padStart(2, '0');
      seconds = seconds.toString().padStart(2, '0');

      return `${hours}:${minutes}:${seconds}`;
    },
  },
  methods: {
    startClass() {
      this.isStartClassModalVisible = true;
    },
    async confirmstartClass() {
      this.isStartClassModalVisible = false;
      this.classStarted = true;
      this.startTime = Date.now();
      this.countdownTime = this.countdownTime * 60; // 将分钟转换为秒
      this.classTime = this.countdownTime;
      this.countdownTimer = setInterval(() => {
        this.countdownTime--;
        if (this.countdownTime <= 0) {
          this.endClass(); // 倒计时结束时自动结束课堂
        }
      }, 1000);
      await this.startRecording();
    },
    async endClass() {
      this.classStarted = false;
      clearInterval(this.countdownTimer); // 清除倒计时定时器
      await this.stopRecording();
    },
    async startRecording() {
      this.isLoading = true;
      this.videoChunks = [];
      this.audioChunks = [];

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        this.mediaRecorder = new MediaRecorder(stream);
        
        this.mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            console.log('this.audioChunks.push(e.data);')
            this.audioChunks.push(e.data);
            console.log(this.audioChunks)
            this.saveAudioToServer();
            // if (e.data.type.includes('video')) {
            //   this.videoChunks.push(e.data);
            // } else {
            //   this.audioChunks.push(e.data);
            // }
          }
        };
        this.mediaRecorder.onstop = this.saveAudioToServer;
        this.mediaRecorder.start();

        const videoElement = document.createElement('video');
        videoElement.srcObject = stream;
        videoElement.play();

        videoElement.addEventListener('loadedmetadata', () => {
          this.isLoading = false;
          this.drawVideoFrame(videoElement);
        });

      } catch (err) {
        console.error("Error accessing the camera or microphone", err);
        this.isLoading = false;
      }
    },
    async stopRecording() {
      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop();

        const stream = this.mediaRecorder.stream;
        if (stream) {
          stream.getTracks().forEach(track => {
            track.stop();
          });
        }
        this.mediaRecorder.onstop = null; // Reset onstop handler
        this.mediaRecorder = null; // Reset MediaRecorder object
      }
    },
    async saveAudioToServer() {
      console.log(this.audioChunks)
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
      this.audioChunks = [];

      const formData = new FormData();
      formData.append('audio', audioBlob, 'class_audio.wav');
      this.recordloading = true;
      try {
        const response = await axios.post('http://localhost:5000/get_classaudio', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        this.recordloading = false;
        if (response.status === 200) {
          // 处理保存成功后的逻辑
          this.classtext = response.data.classtext;
          console.log(this.classtext)
          console.log('音频保存成功');
        } else {
          // 处理保存失败的逻辑
          console.error('保存音频时出现错误');
        }
      } catch (error) {
        console.error('保存音频时出现错误', error);
      }
    },
    drawVideoFrame(videoElement) {
      const canvas = this.$refs.canvas;
      const context = canvas.getContext('2d');
      canvas.width = videoElement.videoWidth;
      canvas.height = videoElement.videoHeight;

      const draw = () => {
        if (!this.classStarted) return;

        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        requestAnimationFrame(draw);
      };
      draw();
    },
    selectTime(time) {
      this.countdownTime = time;
    },
    toggleVoiceInput() {
      if (this.isaskRecording) {
        this.stopVoiceRecognition();
      } else {
        this.startVoiceRecognition();
      }
    },
    sendMessage() {
      if (this.inputValue.trim() === '') return;
      console.log("this.inputValue",this.inputValue)
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
          this.isaskRecording = true;

          this.mediaRecorder.ondataavailable = event => {
            this.audioChunks.push(event.data);
          };
        })
        .catch(error => {
          console.error('getUserMedia error:', error);
        });
    },
    stopVoiceRecognition() {
      if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.stop();
        this.isaskRecording = false;

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
          })
          .catch((err) => {
            this.thinking = false;
            console.error(err);
          });
        };
      }
    },
    openModal() {
      this.isModalVisible = true;
    },
    closeStartClassModal() {
      this.isStartClassModalVisible = false;
    },
    closeModal() {
      this.isModalVisible = false;
    },
    selectOption(option) {
      this.questionRequirements.useClassContent = option;
    },
    generateQuestions() {
      this.loading = true;
      // Prepare data to send to backend
      const requestData = {
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
      console.log("requestData:",requestData);
      axios.post('http://localhost:5000/get_ClassTestProblems', requestData)
        .then((res) => {
          console.log("res.data['problems']:",(res.data)['problems']);
          // Save the received questions to IndexedDB
          this.saveQuestionsToIndexedDB((res.data)['problems']);
          this.closeModal(); // Close modal after successful operation
        })
        .catch((err) => {
          console.error('Error generating questions:', err);
          // Optionally handle error display or logging
        });
    },
    async saveQuestionsToIndexedDB(problems) {
      const db = await openDB('ClassTestProblems', 1, {
        upgrade(db) {
          console.log('upgrade')
          if (!db.objectStoreNames.contains('single_choice')) {
            console.log("no single_choice")
            db.createObjectStore('single_choice', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('judgement')) {
            console.log("no judgement")
            db.createObjectStore('judgement', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('fillin')) {
            console.log("no fillin")
            db.createObjectStore('fillin', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('evaluation')) {
            console.log("no evaluation")
            db.createObjectStore('evaluation', { keyPath: 'id', autoIncrement: true });
          }
          console.log('evaluation')
          if (!db.objectStoreNames.contains('dimension')) {
            db.createObjectStore('dimension', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('score')) {
            db.createObjectStore('score', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('shortcoming')) {
            db.createObjectStore('shortcoming', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('suggestion')) {
            db.createObjectStore('suggestion', { keyPath: 'id', autoIncrement: true });
          }
        },
    });

    // Start a new transaction to clear existing data
    const tx = db.transaction(['single_choice', 'judgement', 'fillin'], 'readwrite');
    await Promise.all([
      tx.objectStore('single_choice').clear(),
      tx.objectStore('judgement').clear(),
      tx.objectStore('fillin').clear(),
    ]);
    await tx.done;

    // Start a new transaction to store new problems
    const txNew = db.transaction(['single_choice', 'judgement', 'fillin'], 'readwrite');
    let singleChoiceId = 1;
    let judgementId = 1;
    let fillinId = 1;

    problems.forEach((problem) => {
      const problemWithDoneAnswer = { ...problem, doneanswer: '' };
      if (problem.type === 'single_choice') {
        txNew.objectStore('single_choice').put({ ...problemWithDoneAnswer, id: singleChoiceId++ });
      } else if (problem.type === 'judgement') {
        txNew.objectStore('judgement').put({ ...problemWithDoneAnswer, id: judgementId++ });
      } else if (problem.type === 'fillin') {
        txNew.objectStore('fillin').put({ ...problemWithDoneAnswer, id: fillinId++ });
      }
    });
    await txNew.done;
    console.log('随堂测试题目存储完毕');
    this.loading = false;
    this.$router.push('/classtest');
    },
    goBack() {
      this.$router.back();
    },
    selectUploadFile() {
      // 触发文件输入框点击事件
      this.$refs.fileInput.click();
    },
    handleDDFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        // 使用FileReader读取文件内容
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target.result;
          // 解析CSV文件内容
          this.parseCSV(content);
        };
        reader.readAsText(file);
      }
    },
    parseCSV(content) {
      // 按行拆分CSV内容
      const rows = content.split('\n');
      // 提取每行的学生名字
      this.students = rows.map(row => row.trim()).filter(row => row);
      // 显示模态框
      console.log("this.students",this.students)
      this.showDDModal = true;
    },
    randomSelectStudent() {
      if (this.students.length === 0) {
        console.log(111)
        this.showDDAlertModal = true;
      } else {
        console.log(222)
        this.showDDModal = true;
        this.startSelection();
      }
    },
    startSelection() {
      if (this.selectionInterval) {
        clearInterval(this.selectionInterval);
      }

      let counter = 0;
      this.selectionInterval = setInterval(() => {
        this.selectedStudentIndex = Math.floor(Math.random() * this.students.length);
        counter++;
        if (counter >= 30) { // 控制循环次数来模拟动画效果
          clearInterval(this.selectionInterval);
        }
      }, 100); // 每100毫秒切换一次
    },
    closeDDModal() {
      this.showDDModal = false;
    },
    closeDDAlertModal() {
      this.showDDAlertModal = false;
    },
    closeClassSummary() {
        this.classtext = null;
    },
  },
  mounted() {
    this.startTime = Date.now();
  },
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer);
    }
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }
  }
};
</script>

<style scoped>
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
.container {
  display: flex;
  flex-direction: column;
  height: 97vh;
}

.header {
  text-align: center;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f5f5f5;
  border-bottom: 1px solid #ddd;

  h1 {
    text-align: center;
    margin: 0;
  }

  .back-button {
    padding: 0.5rem 1rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
}

.content {
  display: flex;
  flex: 1;
}

.classroom-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: #ffffff;
  border-bottom: 1px solid #ffffff;

  button {
    padding: 0.5rem 1rem;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  span {
    font-size: 1.2rem;
    font-weight: bold;
  }
}

.main-content {
  display: flex;
  flex: 1;
}

.left {
  flex: 3;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  border-right: 1px solid #ddd;
  border: 2px solid black;
  margin: 10px;
  padding: 10px;
  position: relative;

  .loading-spinner {
    width: 50px;
    height: 50px;
    border: 5px solid #f3f3f3;
    border-top: 5px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  canvas.video-canvas {
    width: 70%;
    height: 80%;
    border: 1px solid #000;
    display: block;
    z-index: 0;
    margin-top: 10px;
  }
  .hide-canvas {
    display: none;
  }

  .progress-container {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 10px;
}

.progress-text {
    margin-right: 10px;
    font-size: 14px;
    white-space: nowrap;
}

.progress-bar {
    position: relative;
    flex-grow: 1;
    height: 10px;
    background-color: #ddd;
    border-radius: 5px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: blue;
    position: relative;
    transition: width 0.3s ease;
}

.playhead {
    position: absolute;
    top: -3px;
    width: 16px;
    height: 16px;
    background-color: white;
    border: 2px solid blue;
    border-radius: 50%;
    transform: translateX(-50%);
    transition: left 0.3s ease;
}


}

.right {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;

  .top {
    display: flex;
    flex-direction: column;
    gap: 1rem;

    .section {
      display: flex;
      flex-direction: column;
      align-items: flex-start;

      h2 {
        margin: 0 0 1rem 0;
      }

      .button-container {
        display: flex;
        gap: 1rem;

        button {
          padding: 0.5rem 1rem;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
      }
    }
  }

  .bottom {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    flex: 1;
    border: 2px solid black;
    overflow-y: scroll;
    h2 {
      margin: 0 0 1rem 0;
    }

    .chat-box {
      flex: 3;
      padding: 10px;
      overflow-y: scroll;
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
  }
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
  position: relative; /* Ensure relative positioning for child elements */
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

/* 加载中弹窗样式 */
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
    z-index: 1000;
  }

  .loading-content {
    background-color: #fff;
    padding: 20px;
    border-radius: 5px;
    text-align: center;
  }

  .voice-button {
    background-color: #6c757d;
    color: white;
    border: none;
    padding: 8px 16px;
    font-size: 16px;
    cursor: pointer;
    margin-left: 10px;
    border-radius: 4px;
  }

  .voice-button:hover {
    background-color: #5a6268;
  }

  .voice-button.recording {
    background-color: #dc3545; /* 红色表示录音中 */
  }

  .time-options button {
    margin-right: 10px; /* 调整这个值来增加或减少间距 */
  }

  .time-options button:last-child {
    margin-right: 0; /* 移除最后一个按钮的右边距 */
  }

  .DDmodal {
    display: flex;
    justify-content: center;
    align-items: center;
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background-color: rgba(0, 0, 0, 0.4);
  }

  .DDmodal-content {
    background-color: #fff;
    margin: 15% auto;
    padding: 20px;
    border: 1px solid #888;
    border-radius: 10px; /* 增加圆角 */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* 添加阴影 */
    width: 80%;
    max-width: 600px;
    position: relative;
    text-align: center;
  }

  .DDclose {
    color: #aaa;
    position: absolute;
    top: 10px;
    right: 10px;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
  }

  .DDclose:hover,
  .DDclose:focus {
    color: black;
    text-decoration: none;
    cursor: pointer;
  }

  .student-list {
    list-style-type: none;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(5, 1fr); /* 调整列数 */
    gap: 10px;
    margin-bottom: 20px; /* 增加下方间距 */
  }

  .student-list li {
    padding: 10px; /* 增加内边距 */
    text-align: center;
    background-color: #f9f9f9; /* 修改背景颜色 */
    border: 1px solid #ddd;
    border-radius: 5px; /* 增加圆角 */
    transition: background-color 0.3s ease; /* 添加过渡效果 */
  }

  .student-list li.selected {
    background-color: #ffd700; /* 选择后的背景颜色，可以根据需要进行调整 */
  }

  .select-button {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s ease; /* 添加过渡效果 */
  }

  .select-button:hover {
    background-color: #0056b3;
  }

  .alert-modal {
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

  .alert-modal-content {
    background-color: #fff;
    padding: 20px;
    border-radius: 10px;
    width: 300px;
    text-align: center;
    position: relative;
  }

  .alert-close {
    position: absolute;
    top: 10px;
    right: 10px;
    font-size: 28px;
    cursor: pointer;
  }

  .alert-close:hover {
    color: black;
  }

  .alert-modal-content h3 {
    margin: 0 0 10px 0;
  }

  .alert-modal-content p {
    margin: 0 0 20px 0;
  }

  .alert-modal-content button {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s ease;
  }

  .alert-modal-content button:hover {
    background-color: #0056b3;
  }

  .class-dialog {
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

.class-content {
  position: relative; /* Ensure relative positioning for child elements */
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-width: 600px; /* Limit the width of the content */
  width: 90%; /* Ensure content is responsive */
}

.summary-container {
  max-height: 400px; /* Adjust the height as needed */
  overflow-y: auto; /* Add vertical scrolling */
}

.summary-content p {
  margin: 0;
  padding: 5px 0;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
}

.close-button i {
  color: #000;
}

.close-button:hover i {
  color: #f00;
}
  .user-message-bubble {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 8px;
    margin: 5px 0;
    max-width: 70%;
    word-wrap: break-word;
    align-self: flex-start;
  }

  .assistant-message-bubble {
    background-color: #e0f7fa;
    padding: 10px;
    border-radius: 8px;
    margin: 5px 0;
    max-width: 70%;
    word-wrap: break-word;
    align-self: flex-end;
  }
</style>
