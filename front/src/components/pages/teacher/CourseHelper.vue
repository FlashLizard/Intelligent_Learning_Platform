<template>
  <div class="guide-modal" v-if="guidevisible">
    <div class="guide-modal-content">
      <button class="guide-close-button" @click="guidevisible=false">
        <i class="fas fa-times"></i>
      </button>
      <h3> <i class="fas fa-exclamation-circle"></i> 页面操作指南</h3>
      <textarea type="text" v-model="guidetext" class="guide-text" readonly />
      <slot></slot>
      <button class="guide-action-button" @click="guidevisible=false"><i class="fas fa-check"></i> 确认</button>
    </div>
  </div>

  <div class="container">
    <!-- 加载中弹窗 -->
  <div v-if="recordloading" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-spinner fa-spin"></i> 课堂总结生成中...</h2>
    </div>
  </div>
  <div v-if="classtext" class="class-dialog">
    <div class="class-content summary-container">
      <button class="sumclose-button" @click="closeClassSummary">
        <i class="fas fa-times"></i>
      </button>
      <h3><i class="fas fa-book-open"></i> 课堂概述</h3>
      <div class="summary-content">
        <p v-for="line in classtext.split('\n')" :key="line">{{ line }}</p>
      </div>
      <!-- Copy Button -->
      <button class="copy-button" @click="copyClassSummary">{{ copyButtonText }}</button>
    </div>
  </div>
    <div class="header-container">
      <header class="header">
        <h1><i class="fas fa-book-open"></i> 随堂助手</h1>
        <button class="openguide-button" @click="guidevisible = true"> <i class="fas fa-exclamation-circle"></i> </button>
        <button class="back-button" @click="goBack"><i class="fas fa-arrow-left"></i>返回</button>
      </header>
    </div>

    <!-- 主内容 -->
    <div class="content">
      <div class="main-content">
        <div class="left">
          <!-- 课堂控制 -->
          <div class="classroom-controls">
            <button @click="classStarted ? endClass() : startClass()">
              <i :class="classStarted ? 'fas fa-stop' : 'fas fa-play'"></i>
              {{ classStarted ? '结束课堂' : '开始课堂' }}
            </button>
            <span>倒计时：{{ formatCountdownTime }}</span>
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
              <h2><i class="fas fa-bell"></i> 点答器</h2>
              <div class="button-container">
                <button @click="selectUploadFile"><i class="fas fa-file-upload"></i> 上传学生名单</button>
                <button @click="randomSelectStudent"><i class="fas fa-random"></i> 随机抽取学生</button>
              </div>
              
              <!-- 隐藏的文件输入框 -->
              <input type="file" ref="fileInput" @change="handleDDFileUpload" style="display: none" />
              
              <!-- 显示学生名字的模态框 -->
              <div v-if="showDDModal" class="DDmodal">
                <div class="DDmodal-content">
                  <span class="DDclose" @click="closeDDModal">
                    <i class="fas fa-times"></i>
                  </span>
                  <h2><i class="fas fa-book-open"></i> 学生名单</h2>
                  <ul class="student-list">
                    <li v-for="(student, index) in students" :key="index" :class="{ selected: index === selectedStudentIndex }">{{ student }}</li>
                  </ul>
                  <button @click="startSelection" class="extract-button" ><i class="fas fa-check"></i> 抽取学生</button>
                </div>
              </div>
              <!-- 警告模态框 -->
              <div v-if="showDDAlertModal" class="alert-modal">
                <div class="alert-modal-content">
                  <span class="alert-close" @click="closeDDAlertModal">
                    <i class="fas fa-times"></i>
                  </span>
                  <p>学生名单为空，请先上传学生名单。</p>
                  <button @click="closeDDAlertModal"><i class="fas fa-check"></i> 确定</button>
                </div>
              </div>
            </div>

            <div class="section">
              <h2><i class="fas fa-pencil-alt"></i> 随堂测试</h2>
              <div class="button-container">
                <button @click="openModal"><i class="fas fa-pencil-alt"></i> 在线测试</button>
                <button @click="isDownloadModalVisible = true"><i class="fas fa-download"></i> 下载试卷</button>
              </div>
            </div>

            <div class="section">
              <h2><i class="fas fa-comments"></i> 随堂答疑</h2>
              <div class="button-container">
                <button @click="toggleVoiceInput"> {{ isaskRecording ? '🛑' : '🎤' }} 语音提问</button>
                <button @click="sendMessage"><i class="fas fa-paper-plane"></i>  发送问题 </button>
              </div>
              <div class="qa-container">
                <div class="input-group">
                  <label><i class="fas fa-question-circle"></i> 问题：</label>
                  <textarea v-model="inputValue" class="input-field scrollable-input" placeholder="输入您的问题..." @keypress.enter="sendMessage"></textarea>
                </div>
                <div class="input-group">
                  <label><i class="fas fa-reply"></i> 回答：</label>
                  <textarea v-model="AIanswer" class="input-field scrollable-input" placeholder="AI回答将显示在这里..." readonly></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 在线测试弹窗 -->
    <div class="test-modal" v-show="isModalVisible">
      <div class="test-modal-content">
        <button class="test-close-button" @click="closeModal"><i class="fas fa-times"></i></button>
        <h3><i class="fas fa-exclamation-circle"></i> 设置题目要求</h3>
        <div class="test-input-group">
          <label><i class="fas fa-book"></i> 学科：</label>
          <input type="text" class="test-input-field" v-model="questionRequirements.subject" />
        </div>
        <div class="test-input-group">
          <label><i class="fas fa-lightbulb"></i> 知识点：</label>
          <input type="text" class="test-input-field" v-model="questionRequirements.topic" />
        </div>
        <div class="test-input-group">
          <label><i class="fas fa-clipboard-list"></i> 其他要求：</label>
          <input type="text" class="test-input-field" v-model="questionRequirements.other" />
        </div>
        <button class="test-generate-button" @click="generateQuestions"><i class="fas fa-magic"></i> 生成题目</button>
      </div>
    </div>
    <!-- 下载试卷弹窗 -->
    <div class="test-modal" v-show="isDownloadModalVisible">
      <div class="test-modal-content">
        <button class="test-close-button" @click="isDownloadModalVisible=false"><i class="fas fa-times"></i></button>
        <h3><i class="fas fa-exclamation-circle"></i> 设置题目要求</h3>
        <div class="test-input-group">
          <label><i class="fas fa-book"></i> 学科：</label>
          <input type="text" class="test-input-field" v-model="questionRequirements.subject" />
        </div>
        <div class="test-input-group">
          <label><i class="fas fa-lightbulb"></i> 知识点：</label>
          <input type="text" class="test-input-field" v-model="questionRequirements.topic" />
        </div>
        <div class="test-input-group">
          <label><i class="fas fa-clipboard-list"></i> 其他要求：</label>
          <input type="text" class="test-input-field" v-model="questionRequirements.other" />
        </div>
        <button class="test-generate-button" @click="downloadQuestions_docx"><i class="fas fa-magic"></i> 下载试卷</button>
      </div>
    </div>
    <!-- 加载中弹窗 -->
    <div v-if="loading" class="loading-dialog">
      <div class="loading-content">
        <h2><i class="fas fa-spinner fa-spin"></i> 题目生成中,请稍等...</h2>
      </div>
    </div>
  </div>
  
  <!-- 开始课堂 -->
<div class="modal" v-show="isStartClassModalVisible">
  <div class="ktmodal-content">
    <button class="ktclose-button" @click="closeStartClassModal">
      <i class="fas fa-times"></i>
    </button>
    <h3><i class="fas fa-file-powerpoint"></i><span class="blue-text"> 课堂信息</span></h3>
    <div class="ktinput-group">
      <label><i class="fas fa-book"></i><span class="blue-text"> 学科：</span></label>
      <input type="text" v-model="questionRequirements.subject" />
    </div>
    <div class="ktinput-group">
      <label><i class="far fa-clock"></i><span class="blue-text"> 课堂时间:</span> </label>
      <div class="kttime-options">
        <button @click="selectTime(30)" :class="{ selected: questionRequirements.classTime === 30 }">30分钟</button>
        <button @click="selectTime(45)" :class="{ selected: questionRequirements.classTime === 45 }">45分钟</button>
        <button @click="selectTime(60)" :class="{ selected: questionRequirements.classTime === 60 }">60分钟</button>
        <button @click="selectTime(120)" :class="{ selected: questionRequirements.classTime === 120 }">120分钟</button>
      </div>
    </div>
    <button @click="confirmstartClass" class="ktbutton"><i class="fas fa-check-circle"></i> 开始上课</button>
  </div>
</div>
<div v-if="thinking" class="AIloading-dialog">
  <div class="AIloading-content">
    <h2><i class="fas fa-spinner fa-spin"></i> AI思考中...</h2>
  </div>
</div>
</template>

<script>
import axios from 'axios';
import { openDB } from 'idb';

export default {
  data() {
    return {
      guidetext: "1. 如果用户需要AI生成课堂总结,在开课前点击'开始课堂'按钮开启摄像头和麦克风,下课时点击'结束课堂'按钮关闭摄像头麦克风的同时,讯飞智教为您提供您的随堂总结. \n\n2.点答器从用户上传的名单随机抽取学生,方便教师课堂提问或点到. \n\n3.用户可以点击'在线测试'按钮直接做题并查看答案,也可以点击'下载试题'按钮直接下载题目文件. \n\n4.用户可以使用随堂答疑功能,语音提问或键入提问,点击'发送问题'按钮得到AI回答. ",
      guidevisible:false,
      isLoading: false,
      isRecording: false,
      mediaRecorder: null,
      videoChunks: [],
      audioChunks: [],
      classStarted: false,
      startTime: 0,
      elapsed: 0,
      timer: null,
      // messages: [
      //   { text: '您好，我是教育辅导AI小助手，有什么我可以帮忙的吗？', isUser: false }
      // ],
      AIanswer: '',
      inputValue: '',
      isStartClassModalVisible: false,
      isModalVisible: false,
      isDownloadModalVisible: false,
      questionRequirements: {
        subject: '',
        topic: '',
        other: '无',
        useClassContent: false
      },
      loading: false, // 增加loading控制生成题目弹窗
      thinking:false,
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
      copyButtonText: '复制',
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
    copyClassSummary() {
      // Create a temporary text area to copy the text
      const tempTextarea = document.createElement('textarea');
      tempTextarea.value = this.classtext;
      document.body.appendChild(tempTextarea);
      tempTextarea.select();
      document.execCommand('copy');
      document.body.removeChild(tempTextarea);

      // Update the button text to indicate success
      this.copyButtonText = '复制成功';

      // Change it back after 3 seconds
      setTimeout(() => {
        this.copyButtonText = '复制';
      }, 3000);
    },
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
            // console.log(this.audioChunks)
            this.saveAudioToServer();
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
        const response = await axios.post('/get_classaudio', formData, {
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
      this.questionRequirements.classTime = time;
    },
    toggleVoiceInput() {
      if (this.isaskRecording) {
        this.stopVoiceRecognition();
      } else {
        this.startVoiceRecognition();
      }
    },
    sendMessage() {
      this.thinking = true;
      if (this.inputValue.trim() === '') return;
      console.log("this.inputValue",this.inputValue)
      // this.messages.push({ text: this.inputValue, isUser: true });
      // this.questions.push(this.inputValue);
      const userMessage = this.inputValue;
      // this.inputValue = '';

      // Display thinking message
      this.thinking = true;

      // 向后端发送请求
      axios.post('/get_chatanswer', {
        message: userMessage
      })
      .then((res) => {
        this.thinking = false;
        this.AIanswer = (res.data);
        console.log("AIanswer",this.AIanswer)
        // this.messages.push({ text: res.data, isUser: false });
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

          // 关闭麦克风
          if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
          }
          this.thinking = true;
          // 向后端发送请求
          axios.post('/get_chatvoiceanswer', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
          .then((res) => {
            this.thinking = false;
            this.inputValue = res.data['question'];
            this.AIanswer = res.data['answer'];
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
      axios.post('/get_ClassTestProblems', requestData)
        .then((res) => {
          console.log("res.data['problems']:",(res.data)['problems']);
          this.saveQuestionsToIndexedDB((res.data)['problems']);
          this.closeModal(); // Close modal after successful operation
          this.questionRequirements = {
            subject: '',
            topic: '',
            other: '无',
            useClassContent: false
          };
        })
        .catch((err) => {
          console.error('Error generating questions:', err);
          // Optionally handle error display or logging
        });
    },
    async downloadQuestions_docx() {
      this.loading = true;
      this.isDownloadModalVisible=false;
      const requestData = {
        username: "教师",
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
      // 发送 POST 请求到后端获取试题文本
      const response = await axios.post('/get_downloadproblems_docx', requestData, {
        responseType: 'blob' // 响应类型为 Blob
      });

      // 创建一个 Blob URL
      const blob = new Blob([response.data], { type: response.headers['content-type'] });
      const url = window.URL.createObjectURL(blob);

      // 创建一个隐藏的链接并触发下载
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'problems.docx'); // 设置下载文件名
      document.body.appendChild(link);
      link.click();

      // 清除 URL 和链接
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);

      // 完成下载后，隐藏加载动画
      this.loading = false;
      this.questionRequirements = {
        subject: '',
        topic: '',
        other: '无',
        useClassContent: false
      };
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
        // console.log(111)
        this.showDDAlertModal = true;
      } else {
        // console.log(222)
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
        if (counter >= 10) { // 控制循环次数来模拟动画效果
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

.header-container {
  width: 100%;
  text-align: center; /* Center the content horizontally */
}
.header {
  background-image: url('../../../assets/PPTbackground.jpg'); /* 背景图片的路径 */
  background-size: cover; /* 让背景图片充满容器 */
  background-position: center; /* 居中显示背景图片 */
  background-repeat: no-repeat; /* 禁止背景图片重复 */
  display: flex;
  justify-content: space-between;
  text-align: center;
  align-items: center;
  padding: 1rem;
  /* background-color: #f5f5f5; */
  /* border-bottom: 1px solid #ddd; */

  h1 {
    text-align: center;
    color:#c8ebf8;
    margin: 0px;
    margin-left: 600px;
  }

  .openguide-button {
    text-align: center;
    justify-self: center;
    padding: 0.5rem;
    display: inline-block; 
    vertical-align: middle;
    background-color: transparent;
    color: #c8ebf8;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    position: absolute; 
    font-weight: bold;
    font-size: 1.5em;
    top:26px;
    right:130px;
  }
  .openguide-button:hover {
    color: #667cfa;
  }

  .back-button {
    padding: 0.5rem 1rem;
    background-color: #c8ebf8;
    color: rgb(1, 117, 232);
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size:1.0em;
    font-weight:bold;
  }
  .back-button:hover {
    background-color: #15a7dc;
    color:white;
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

  button {
    margin-right:5rem; 
    padding: 0.5rem 1rem;
    background-color: #007bff;
    color: white;
    font-size:1.4em;
    font-weight:bold;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  span {
    height: 40px;
    width:250px;
    padding: 5px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    text-align: center;
    justify-content: center;
    background-color: #4862f8;;
    color:#fbfdff;
    font-size: 1.4em;
    font-weight: bold;
  }
}

.main-content {
  display: flex;
  flex: 1;
  /* background-color: #bbd8f9; */
  background-image: url('../../../assets/PPTbackground1.jpg'); /* 背景图片的路径 */
  background-size: cover; /* 让背景图片充满容器 */
  background-position: center; /* 居中显示背景图片 */
  background-repeat: no-repeat; /* 禁止背景图片重复 */
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
  background-color: #eaf0f6;
  background-image: url('../../../assets/blackboard.jpg'); /* 背景图片的路径 */
  background-size: cover; /* 让背景图片充满容器 */
  background-position: center; /* 居中显示背景图片 */
  background-repeat: no-repeat; /* 禁止背景图片重复 */

  .loading-spinner {
    width: 50px;
    height: 50px;
    border: 5px solid #f3f3f3;
    border-top: 5px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  canvas.video-canvas {
    width: 90%;
    height: 70%;
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
    /* white-space: nowrap; */
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
    gap: 0.1rem;

    .section {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      border: 3px solid #79d2fb; /* 设置蓝色边框 */
      border-radius: 5px;
      padding: 0.5rem; /* 为内容添加一些内边距 */

      h2 {
        color:#ebf6fc;
        margin: 0 0 1rem 0;
      }

      .button-container {
        display: flex;
        gap: 1rem;
        margin-bottom: 30px;

        button {
          font-weight: bold;
          padding: 0.5rem 1rem;
          background-color: #79d2fb;;
          color: rgb(39, 94, 245);
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        button:hover{
          background-color: #0072ff;
          color:white;
        }
      }

      .qa-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
      }

      .input-group {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
      }

      .input-group label {
        font-size: 14px;
        font-weight: bold;
        margin-top:-20px;
        margin-bottom: 3px;
        color: #bce6fa;
      }

      .scrollable-input {
        width: 100%;
        max-height: 150px; /* 适当设置文本框的最大高度 */
        overflow-y: auto; /* 启用纵向滚动 */
        white-space: normal; /* 允许文本换行 */
        word-wrap: break-word; /* 自动换行，避免超出容器范围 */
        padding: 10px;
        font-size: 14px;
        line-height: 1.5em;
        box-sizing: border-box; /* 包括内边距在内的宽度计算 */
        border: 1px solid #ccc;
        border-radius: 4px;
        resize: none; 
      }

      .input-field {
        width:310px;
        height: 90px; 
      }

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
      background-color: #9be08f;
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

.tmclose-button {
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
  font-size:1.1em !important;
  font-weight: bold;
  margin-right: 10px;
  margin-top: 0px;
}

.input-group input {
  padding: 0.5rem;
  border: 2px solid #4a4949 !important;
  border-radius: 4px;
  height:120px;
  width:300px;
}

.input-group div {
  margin-top: 0.5rem;
}

.selected {
  background-color: #0379f7 !important;
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

    h2 {
      color:#0738fc !important;
    }
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
    background-color: #7596ea; /* 修改背景颜色 */
    border: 1px solid #ddd;
    border-radius: 5px; /* 增加圆角 */
    transition: background-color 0.3s ease; /* 添加过渡效果 */
  }

  .student-list li.selected {
    background-color: #ebef10 !important; /* 选择后的背景颜色，可以根据需要进行调整 */
    color: #000 !important;
  }
  .extract-button {
    background-color: #007bff; /* 设置按钮背景颜色 */
    color: white; /* 设置按钮文字颜色 */
    border: none; /* 去掉按钮边框 */
    padding: 10px 20px; /* 设置按钮内边距 */
    cursor: pointer; /* 设置鼠标悬停样式为手型 */
    transition: background-color 0.3s ease; /* 添加过渡效果 */
  }

  .extract-button:hover {
    background-color: #0056b3; /* 设置鼠标悬停时的背景颜色 */
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

.copy-button {
  margin-top: 0px;
  background-color: #007BFF;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
  display: block;
  margin-left: auto;
  margin-right: auto;
}

.copy-button:hover {
  background-color: #0056b3;
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

h3 {
  text-align: center;
  color: #007BFF; /* 蓝色调 */
  font-size: 1.5rem;
  margin-bottom: 1rem;
  margin-top: -5px;
}

.summary-container {
  max-height: 400px; 
  overflow-y: auto;
  background: linear-gradient(-45deg, #A1CFFF, #B3E5FF, #CDEFFF, #D1F5FF);
  background-size: 300% 300%;
  animation: gradientAnimation 5s ease infinite; 
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

.summary-content {
  padding: 1rem;
  color: #333;
  line-height: 1.6;
  font-size: 1rem;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.summary-content p {
  width: 550px;
  min-height: 300px;
  /* margin: 0.5rem 0; */
  margin-top: -5px;
  border: 3px solid #007BFF;
  padding-left: 10px;
}

.sumclose-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
}

.sumclose-button:hover {
  color: #0738fc !important;
}

.sumclose-button i {
  color: #0860f7;
}

/* 开始课堂弹窗样式 */
.ktmodal-content {
  background-color: #baeff8;
  padding: 20px;
  border-radius: 5px;
  width: 500px;
  height: 40%;
  max-width: 90%;
  justify-content: center;
  text-align: center;
  position: relative; /* Ensure relative positioning for child elements */

  h3 {
    margin-top: -5px;
    color: #007bff;
    font-size: 2em;
    font-weight: bold;
  }

  .ktbutton {
    margin-top:50px;
    width:150px;
    height:40px;
    padding: 0.5rem 1rem;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1.2em;
  }

  .ktbutton:hover {
    background-color: #0056b3;
  }
}
.blue-text {
    color: #066dce;
  }
.ktclose-button {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 0.5rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.ktclose-button i {
  font-size: 1.2rem;
}

.ktinput-group {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-top: 3em;
  margin-bottom: em;
}

.ktinput-group label {
  margin-right: 10px;
  font-size: 1.4em;
  font-weight: bold;
  color: #007bff;
}

.ktinput-group input {
  padding: 0.5rem;
  border: 2px solid #066dce !important;
  border-radius: 4px;
}

.kttime-options button {
  width: 87px;
  margin-top: 10px;
  margin-right: 5px; /* Adjust spacing between buttons */
  background-color: #72b9fc;
  border: 1px solid #066dce;
  border-radius: 3px;
  font-size: 1.2em;
  font-weight: bold;
  color:#ffffff;
}

.kttime-options button:hover {
  background-color: #1890ff;
}

.kttime-options button:selected {
  background-color: #1890ff;
  margin-right: 10px; /* Adjust spacing between buttons */
}

.kttime-options button:last-child {
  margin-right: 0; /* Remove right margin from the last button */
}


.AIloading-dialog {
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

.AIloading-content {
  background: linear-gradient(45deg, #00c6ff, #0072ff, #00c6ff, #0072ff); 
  background-size: 400% 400%;
  animation: gradientAnimation 8s ease infinite; 
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  color:white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

.AIloading-spinner {
  margin-top: 10px;
  text-align: center;
}

/* .AIloading-dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: linear-gradient(45deg, #00c6ff, #0072ff, #00c6ff, #0072ff); 
  background-size: 400% 400%;
  padding: 20px;
  border-radius: 10px;
  animation: gradientAnimation 8s ease infinite; 
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
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
} */

.ai-text {
  color: #ffffff;
  font-size: 1.5rem;
  animation: textColorAnimation 3s ease infinite; /* 循环文字变色 */
}

@keyframes textColorAnimation {
  0% {
    color: #00c6ff;
  }
  50% {
    color: #0072ff;
  }
  100% {
    color: #00c6ff;
  }
}

.test-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4); /* 背景半透明遮罩 */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.test-modal-content {
  background-color: #e0f7ff; /* 浅蓝色背景 */
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
  color: #003366; /* 深蓝色字体 */
}

.test-close-button {
  position: relative;
  top: 10px;
  left: 350px;
  background: none;
  border: none;
  color: #003366; /* 深蓝色图标 */
  font-size: 18px;
  cursor: pointer;
}

h3 {
  text-align: center;
  margin-bottom: 20px;
  color: #003366; /* 深蓝色标题 */
}

.test-input-group {
  margin-bottom: 15px;
}

.test-input-group label {
  color: #003366; /* 深蓝色标签 */
  font-weight: bold;
}

.test-input-field {
  width: 90%;
  padding: 8px;
  margin-top: 5px;
  border: 2px solid #003366; /* 深蓝色边框 */
  border-radius: 4px;
  color: #003366; /* 深蓝色文本 */
}

.test-generate-button {
  justify-content: center;
  text-align: center;
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.0em;
  font-weight: bold;
  margin-top: 20px;
}

.test-generate-button:hover {
  background-color: #0056b3;
}

.guide-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.guide-modal-content {
  background: #a9e2f7;
  border-radius: 8px;
  padding: 20px;
  position: relative;
  width: 80%;
  max-width: 500px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.guide-close-button {
  color:#007bff;
  position: absolute;
  top: 20px;
  right: 10px;
  background: transparent;
  border: none;
  font-size: 1.5em;
  cursor: pointer;
}

.guide-action-button {
  display: block;
  margin: 20px auto 0;
  padding: 10px 20px;
  background: #007bff;
  color: #fff;
  border: none;
  border-radius: 5px;
  font-size: 1.1em;
  font-weight:bold;
  cursor: pointer;
}

.guide-action-button:hover {
  background: #0056b3;
}

.guide-text {
  width: 100%;
  min-height: 200px;
  margin: 20px 0;
  margin-bottom: 0px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  font-size:1.2em;
}

h3 {
  text-align: center;
  margin: 0;
  color:#007bff;
  font-size: 1.5em;
}

</style>