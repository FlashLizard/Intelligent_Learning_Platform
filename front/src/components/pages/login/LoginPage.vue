<template>
  <div class="login-page">
    <div class="login-container">
      <h1>欢迎来到讯飞智教</h1>

      <!-- 切换栏 -->
      <div class="switch-tabs">
        <div class="tab" :class="{ active: activeTab === 'password' }" @click="switchTab('password')">
          <i class="fas fa-lock"></i> 密码登录
        </div>
        <div class="tab" :class="{ active: activeTab === 'face' }" @click="switchTab('face')">
          <i class="fas fa-camera"></i> 人脸登录
        </div>
        <div class="tab" :class="{ active: activeTab === 'voice' }" @click="switchTab('voice')">
          <i class="fas fa-microphone"></i> 声纹登录
        </div>
      </div>

      <form @submit.prevent="login">
        <!-- 表单内容根据选中的登录方式来显示 -->
        <div v-if="activeTab === 'password'" class="form-group">
          <label for="username">用户名</label>
          <input type="text" id="username" v-model="username" required />
        </div>
        <div v-if="activeTab === 'password'" class="form-group">
          <label for="password">密码</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <!-- 声纹登录的用户名输入框 -->
        <div v-if="activeTab === 'voice'" class="form-group">
          <label for="voice-username">用户名</label>
          <input type="text" id="voice-username" v-model="username" required />
        </div>
        <!-- 声纹登录的麦克风按钮 -->
        <div v-if="activeTab === 'voice'" class="microphone-container">
          <label class="voice-label">录入语音: </label>
          <button type="button" @click="toggleRecording" class="microphone-button">
            <i :class="isRecording ? 'fas fa-stop' : 'fas fa-microphone'"></i>
          </button>
        </div>
        <!-- 人脸识别登录的内容 -->
        <div v-if="activeTab === 'face'" class="form-group">
          <label for="face-username">用户名</label>
          <input type="text" id="face-username" v-model="username" required />
        </div>
        <div v-if="activeTab === 'face'" class="photo-container">
          <label class="face-label">人脸拍照: </label>
          <button type="button" @click="startCamera" class="photo-button">
            <i class="fas fa-camera"></i>
          </button>
        </div>
        <!-- 其他登录方式的输入框可以在这里添加 -->
        <div v-if="activeTab === 'password'" class="button-group">
          <button type="submit" class="animated-button">登录</button>
          <button type="button" @click="register" class="animated-button register-button">注册</button>
        </div>
        <div v-else-if="activeTab === 'voice'" class="button-group">
          <button type="submit" class="animated-button">登录</button>
          <button type="button" @click="registerVoice" class="animated-button register-button">注册</button>
        </div>
        <div v-else-if="activeTab === 'face'" class="button-group">
          <button type="submit" class="animated-button">登录</button>
          <button type="button" @click="register" class="animated-button register-button">注册</button>
        </div>
      </form>

      <!-- 自定义弹窗 -->
      <div v-if="dialogVisible" class="dialog-overlay">
        <div class="dialog-content">
          <h2>{{ dialogMessage }}</h2>
          <button @click="handleDialogClose">确定</button>
        </div>
      </div>
    </div>
    <!-- 摄像头弹窗 -->
    <div v-if="cameraDialogVisible" class="camera-overlay">
      <div class="camera-content">
        <i class="fas fa-times close-icon" @click="closeCameraDialog"></i>
        <div class="circle-overlay"></div> <!-- 圆圈 -->
        <video ref="video" class="camera-video" autoplay></video>
        <button @click="capturePhoto" class="capture-button">截图</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { openDB } from 'idb';

export default {
  data() {
    return {
      username: '',
      password: '',
      dialogMessage: '',
      dialogVisible: false,
      loading: false,
      activeTab: 'password', 
      isRecording: false,
      mediaRecorder: null,
      audioChunks: [],
      hasRecorded: false,  // 记录用户是否已经录制了声纹
      cameraDialogVisible: false,
      capturedPhoto: null,
    };
  },
  methods: {
    switchTab(tab) {
      this.activeTab = tab;
    },
    // 切换摄像头弹窗的显示状态
    closeCameraDialog() {
      this.cameraDialogVisible = false;
      this.stopCamera();
    },
    startCamera() {
      this.cameraDialogVisible = true;
      navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((stream) => {
          this.$refs.video.srcObject = stream;
        })
        .catch((err) => {
          console.error("Error accessing camera: ", err);
        });
    },
    stopCamera() {
      const stream = this.$refs.video.srcObject;
      if (stream instanceof MediaStream) {
        const tracks = stream.getTracks();
        tracks.forEach((track) => track.stop());
        this.$refs.video.srcObject = null;
        console.log('Camera stopped successfully');
      } else {
        console.error('No media stream found');
      }
    },
    capturePhoto() {
      const video = this.$refs.video;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataURL = canvas.toDataURL('image/png');
      const photoBlob = this.dataURLToBlob(dataURL);

      // 发送截图数据到后端
      this.sendPhotoToBackend(photoBlob);
      
      this.closeCameraDialog();
    },
    dataURLToBlob(dataURL) {
      const [header, data] = dataURL.split(',');
      const mime = header.split(':')[1].split(';')[0];
      const byteString = atob(data);
      const arrayBuffer = new ArrayBuffer(byteString.length);
      const uintArray = new Uint8Array(arrayBuffer);
      
      for (let i = 0; i < byteString.length; i++) {
        uintArray[i] = byteString.charCodeAt(i);
      }
      
      return new Blob([uintArray], { type: mime });
    },
    async sendPhotoToBackend(photoBlob) {
      try {
        const formData = new FormData();
        formData.append('username', this.username);
        formData.append('photo', photoBlob, 'photo.png');

        const response = await axios.post('/face_login', formData);
        if (response.data.status === 'success') {
          this.dialogMessage = '人脸登录成功';
        } else {
          this.dialogMessage = response.data.msg;
        }
        this.dialogVisible = true;
      } catch (error) {
        console.error('发送照片失败:', error);
        this.dialogMessage = '人脸登录请求失败';
        this.dialogVisible = true;
      }
    },
    async toggleRecording() {
      if(!(this.username)){
        alert('请先输入用户名');
        return;
      }
      if (this.isRecording && this.username) {
        this.stopRecording();
      } else {
        this.startRecording();
      }
    },
    async startRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream);
        this.mediaRecorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data);
        };
        this.mediaRecorder.start();
        this.isRecording = true;
      } catch (err) {
        console.error('Error accessing microphone:', err);
      }
    },
    stopRecording() {
      this.mediaRecorder.stop();
      this.mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        this.audioChunks = [];
        this.isRecording = false;

        // 停止麦克风捕获并释放资源
        const tracks = this.mediaRecorder.stream.getTracks();
        tracks.forEach(track => track.stop());

        // 将录音发送到后端
        const formData = new FormData();
        formData.append('username', this.username);
        formData.append('voice_file', audioBlob, 'voice.wav');

        try {
          const response = await axios.post('/save_user_voice', formData);
          this.hasRecorded = true;
          this.dialogMessage = '声纹上传成功';
          this.dialogVisible = true;
          console.log('Voice saved:', response.data);
        } catch (error) {
          console.error('Failed to save voice:', error);
        }
      };
    },
    async login() {
      console.log('Into login')
      try {
        if(this.activeTab === 'password'){
          const response = await axios.post('/password_login', { username: this.username , password:this.password }).then((res) => {
            return res;
          });
          const data = response.data;
          if (data.status === 'success') {
            console.log('userid',data.user_id)
            const userId = data.user_id;
            await this.saveUserToIndexedDB(this.username, userId);
            this.$router.push('/index');
          } else {
            this.dialogMessage = data.msg;
            this.dialogVisible = true;
          }
        }
        if(this.activeTab === "voice"){
          if (!this.hasRecorded) {
            this.dialogMessage = '请先上传声纹信息';
            this.dialogVisible = true;
            return;
          }
          console.log("login_voice")
          const response = await axios.post('/voicelogin', { username: this.username}).then((res) => {
            return res;
          });
          const data = response.data;
          if (data.status === 'success') {
            console.log('userid',data.user_id)
            const userId = data.user_id;
            await this.saveUserToIndexedDB(this.username, userId);
            this.$router.push('/index');
          } else {
            this.dialogMessage = data.msg;
            this.dialogVisible = true;
          }
        }
        if(this.activeTab === "face"){
          console.log("face")
        }
      } catch (error) {
        console.error('登录失败:', error);
      }
    },
    async register() {
      console.log('注册用户名:', this.username);
      console.log('注册密码:', this.password);

      try {
        this.loading = true;
        const response = await axios.post('create_user', {
          username: this.username,
          password: this.password,
        });

        this.loading = false;

        if (response.data.status === 'success') {
          this.dialogMessage = '注册成功';
          const userId = response.data.user_id;
          await this.saveUserToIndexedDB(this.username, userId);
          this.dialogVisible = true;
        } else {
          this.dialogMessage = response.data.msg;
          this.dialogVisible = true;
        }
      } catch (error) {
        this.loading = false;
        console.error('注册请求失败:', error);
        this.dialogMessage = '注册请求失败';
        this.dialogVisible = true;
      }
    },
    async registerVoice() {
      if (!this.hasRecorded) {
        this.dialogMessage = '请先上传声纹信息';
        this.dialogVisible = true;
        return;
      }
      try {
        const response = await axios.post('/voiceregister', {
          username: this.username
        });

        if (response.data.group_id) {
          this.dialogMessage = '声纹注册成功';
        } else {
          this.dialogMessage = '声纹注册失败';
        }
        this.dialogVisible = true;
      } catch (error) {
        console.error('声纹注册请求失败:', error);
        this.dialogMessage = '声纹注册请求失败';
        this.dialogVisible = true;
      }
    },
    async saveUserToIndexedDB(username, userId) {
      const db = await openDB('UserDatabase', 1, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('users')) {
            db.createObjectStore('users', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
        },
      });

      const tx = db.transaction('users', 'readwrite');
      const store = tx.objectStore('users');
      await store.clear();
      await store.put({ username, userId });
      await tx.done;
      console.log('用户数据已保存到 IndexedDB');
    },
    handleDialogClose() {
      this.dialogVisible = false;
    }
  },
};
</script>

<style lang="scss" scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
  font-family: 'Arial', sans-serif;
}

.login-container {
  background-color: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 75%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

h1 {
  margin-top: 5px;
  margin-bottom: 40px;
  color: #2e83df;
  font-size: 2.5em;
}

.switch-tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.tab {
  padding: 10px 20px;
  cursor: pointer;
  background-color: #e0e0e0;
  border-radius: 0px;
  margin: 0;
  font-weight: bold;
  color: #555;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.tab.active {
  background-color: #4facfe;
  color: white;
}

.tab i {
  margin-right: 8px;
}

.form-group {
  margin-bottom: 30px;
  text-align: left;
  width: 100%;
}

label {
  display: block;
  margin-bottom: 10px;
  color: #4facfe;
  font-weight: bold;
  font-size: 1.2em;
}

input[type='text'],
input[type='password'] {
  width: 100%;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  font-size: 1.1em;
}

.button-group {
  width: 100%;
  display: flex;
  justify-content: space-between;
}

button {
  width: calc(50% - 10px); /* 计算按钮宽度，减去间距 */
  padding: 15px;
  background-color: rgba(10, 132, 238, 0.8); /* 变淡的背景颜色 */
  border: none;
  border-radius: 5px;
  color: white;
  font-size: 1.2em;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: rgba(36, 168, 234, 0.8); /* 悬停时变淡的背景颜色 */
}

.animated-button {
  position: relative;
  overflow: hidden;
}

.animated-button span {
  position: absolute;
  display: block;
}

.animated-button span.border-top {
  top: 0;
  left: -100%;
  width: 100%;
  height: 4px;
  animation: animate-top 2s linear infinite;
  animation-delay: 0.0s;
  background: linear-gradient(90deg, transparent, #03e9f4);
}

.animated-button span.border-right {
  top: -100%;
  right: 0;
  width: 4px;
  height: 100%;
  animation: animate-right 2s linear infinite;
  animation-delay: 0.5s;
  background: linear-gradient(180deg, transparent, #03e9f4);
}

.animated-button span.border-bottom {
  bottom: 0;
  left: -100%;
  width: 100%;
  height: 4px;
  animation: animate-bottom 2s linear infinite;
  animation-delay: 1s;
  background: linear-gradient(90deg, #03e9f4, transparent);
}

.animated-button span.border-left {
  bottom: -100%;
  left: 0;
  width: 4px;
  height: 100%;
  animation: animate-left 2s linear infinite;
  animation-delay: 1.5s;
  background: linear-gradient(0deg, transparent, #03e9f4);
}

@keyframes animate-top {
  0% {
    left: -100%;
    background-size: 0% 100%;
  }
  50% {
    left: 100%;
    background-size: 100% 100%;
  }
  100% {
    left: 100%;
    background-size: 0% 100%;
  }
}

@keyframes animate-right {
  0% {
    top: -100%;
    background-size: 100% 0%;
  }
  50% {
    top: 100%;
    background-size: 100% 100%;
  }
  100% {
    top: 100%;
    background-size: 100% 0%;
  }
}

@keyframes animate-bottom {
  0% {
    left: 100%;
    background-size: 0% 100%;
  }
  50% {
    left: -100%;
    background-size: 100% 100%;
  }
  100% {
    left: -100%;
    background-size: 0% 100%;
  }
}

@keyframes animate-left {
  0% {
    bottom: -100%;
    background-size: 100% 0%;
  }
  50% {
    bottom: 100%;
    background-size: 100% 100%;
  }
  100% {
    bottom: 100%;
    background-size: 100% 0%;
  }
}

.loading-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-content {
  background: white;
  padding: 20px;
  border-radius: 5px;
  text-align: center;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  width:300px;
  height:150px;
  background: white;
  padding: 20px;
  border-radius: 5px;
  text-align: center;
}

button {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #4facfe;
  border: none;
  border-radius: 5px;
  color: white;
  font-size: 1em;
  cursor: pointer;
}

button:hover {
  background-color: #2e83df;
}

.microphone-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 10px;
}

.voice-label {
  margin-right: 45px;
  font-size: 1.2em;
  color: #4facfe;
}

.microphone-button {
  margin-right: 45px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #4facfe;
  color: white;
  border: none;
  font-size: 2.3em;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.microphone-button:hover {
  background-color: #2e83df;
}

.microphone-button .fa-stop {
  color: red;
}

.photo-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 10px;
}

.face-label {
  margin-right: 45px;
  font-size: 1.2em;
  color: #4facfe;
}

.photo-button {
  margin-right: 45px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #4facfe;
  color: white;
  border: none;
  font-size: 2.3em;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.photo-button:hover {
  background-color: #2e83df;
}
/* 摄像头弹窗样式 */
.camera-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.camera-content {
  background: white;
  padding: 20px;
  border-radius: 5px;
  text-align: center;
  position: relative;
}

.camera-video {
  width: 100%;
  max-width: 300px;
  height: auto;
  border-radius: 5px;
  margin-bottom: 20px;
}

.capture-button {
  padding: 10px 20px;
  background-color: #4facfe;
  border: none;
  border-radius: 5px;
  color: white;
  font-size: 1.2em;
  cursor: pointer;
}

.capture-button:hover {
  background-color: #2e83df;
}

.circle-overlay {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  border: 5px solid white;
  border-radius: 50%;
  pointer-events: none; /* 防止点击事件被阻挡 */
  box-sizing: border-box;
}

.close-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 1.5em;
  cursor: pointer;
}

</style>
