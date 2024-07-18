<template>
  <div v-if="imageloading" class="loading-dialog">
      <div class="loading-content">
        <h2><i class="fas fa-spinner fa-spin"></i> 图片解析中...</h2>
      </div>
    </div>
  <!-- Loading Dialog -->
  <div v-if="loading" class="loading-dialog">
      <div class="loading-content">
        <h2><i class="fas fa-spinner fa-spin"></i> 翻译生成中...</h2>
      </div>
    </div>
    <!-- Loading Dialog -->
  <div v-if="yinpining" class="loading-dialog">
      <div class="loading-content">
        <h2><i class="fas fa-wave-square"></i> 音频解析中...</h2>
      </div>
    </div>
    <div class="top-background">
    <h1><i class="fas fa-book-open"></i> 即时翻译</h1>
    <button class="back-button" @click="goBack">
      <i class="fas fa-arrow-left"></i> 返回
    </button>
  </div>
  <div class="translation-container">
    <!-- <button class="back-button" @click="goBack">
      <i class="fas fa-arrow-left"></i> 返回
    </button>
    <h1><i class="fas fa-book-open"></i>AI翻译助手</h1> -->
    <div class="switch-tabs">
      <div
        v-for="tab in tabs"
        :key="tab"
        :class="['tab', { active: activeTab === tab }]"
        @click="setActiveTab(tab)"
      >
        {{ tab }}
      </div>
    </div>
    <div class="button-container">
      <button v-if="isTranslateTextTab" @click="translateText" class="translate-button">
        <i class="fas fa-language"></i> 翻译
      </button>
      <div v-else-if="isTranslateImageTab || isTranslateAudioTab" class="upload-translate-group">
        <label class="upload-button">
          <i class="fas fa-upload"></i> 上传
          <input type="file" @change="uploadFile" class="file-input" />
        </label>
        <button @click="translateText" class="translate-button">
          <i class="fas fa-language"></i> 翻译
        </button>
      </div>
      <div v-else-if="isTranslateSpeechTab" class="upload-translate-group">
        <button @click="toggleRecording" class="upload-button" :class="{'orange-button': recording}">
          <i :class="recording ? 'fas fa-stop' : 'fas fa-microphone'"></i> {{ recording ? '结束录音' : '录音' }}
        </button>
        <button @click="translateText" class="translate-button">
          <i class="fas fa-language"></i> 翻译
        </button>
      </div>
    </div>
    <div class="translation-content">
      <div v-if="isTranslateTextTab" class="left-pane">
        <div class="input-container">
          <div class="language-selector">
            <button @click="toggleSourceLanguageMenu" class="language-button">
              <i class="fas fa-globe"></i> {{ sourceLanguage }}
            </button>
            <ul v-if="showSourceLanguageMenu" class="dropdown-menu">
              <li @click="setSourceLanguage('中文')">中文</li>
              <li @click="setSourceLanguage('英文')">英文</li>
            </ul>
          </div>
          <textarea
            v-model="textToTranslate"
            placeholder="键入文本"
            @keyup.enter="translateText"
          ></textarea>
        </div>
      </div>
      <div v-else-if="isTranslateImageTab || isTranslateAudioTab" class="left-pane">
        <div class="input-container">
          <div class="language-selector">
            <button @click="toggleSourceLanguageMenu" class="language-button">
              <i class="fas fa-globe"></i> {{ sourceLanguage }}
            </button>
            <ul v-if="showSourceLanguageMenu" class="dropdown-menu">
              <li @click="setSourceLanguage('中文')">中文</li>
              <li @click="setSourceLanguage('英文')">英文</li>
            </ul>
          </div>
          <textarea
            v-model="textToTranslate"
            placeholder="请点击上传文件"
            @keyup.enter="translateText"
          ></textarea>
        </div>
      </div>
      <div v-else-if="isTranslateSpeechTab" class="left-pane">
        <div class="input-container">
          <div class="language-selector">
            <button @click="toggleSourceLanguageMenu" class="language-button">
              <i class="fas fa-globe"></i> {{ sourceLanguage }}
            </button>
            <ul v-if="showSourceLanguageMenu" class="dropdown-menu">
              <li @click="setSourceLanguage('中文')">中文</li>
              <li @click="setSourceLanguage('英文')">英文</li>
            </ul>
          </div>
          <textarea
            v-model="textToTranslate"
            placeholder="请点击录入语音"
            @keyup.enter="translateText"
          ></textarea>
        </div>
      </div>
      <div class="right-pane">
        <div class="input-container">
          <div class="language-selector">
            <button @click="toggleTargetLanguageMenu" class="language-button">
              <i class="fas fa-flag"></i> {{ targetLanguage }}
            </button>
            <ul v-if="showTargetLanguageMenu" class="dropdown-menu">
              <li @click="setTargetLanguage('中文')">中文</li>
              <li @click="setTargetLanguage('英文')">英文</li>
            </ul>
          </div>
          <textarea
            v-model="translationResult"
            placeholder="翻译后"
            readonly
          ></textarea>
        </div>
      </div>
    </div>
  </div>
</template>
  <script>
  import axios from 'axios';
  
  export default {
    name: 'TranslationPage',
    data() {
      return {
        tabs: ['翻译文本', '翻译图片', '翻译音频', '翻译语音'],
        activeTab: '翻译文本',
        textToTranslate: '',
        translationResult: '',
        sourceLanguage: '源语言',
        targetLanguage: '目标语言',
        showSourceLanguageMenu: false,
        showTargetLanguageMenu: false,
        recording: false, // 新增录音状态
        yinpining:false,
        loading:false,
        imageloading:false,
      };
    },
    computed: {
      isTranslateTextTab() {
        return this.activeTab === '翻译文本';
      },
      isTranslateImageTab() {
        return this.activeTab === '翻译图片';
      },
      isTranslateAudioTab() {
        return this.activeTab === '翻译音频';
      },
      isTranslateSpeechTab() {
        return this.activeTab === '翻译语音';
      }
    },
    methods: {
      goBack() {
        this.$router.go(-1);
      },
      setActiveTab(tab) {
        this.activeTab = tab;
      },
      async translateText() {
        let message = {
          text: this.textToTranslate,
          target_language: this.targetLanguage === '中文' ? 'zh' : 'en',
          source_language: this.sourceLanguage === '英文' ? 'en' : 'zh',
        };
        try {
          console.log(message);
          this.loading = true;
          const response = await axios.post('/get_texttranslation', message);
          this.translationResult = response.data;
          this.loading = false;
          console.log(response.data);
        } catch (error) {
          console.error('Error translating text:', error);
        }
      },
      async uploadFile(event) {
        const file = event.target.files[0];
        if (!file) return;
  
        const formData = new FormData();
        formData.append('file', file);
  
        try {
          let endpoint;
          switch (this.activeTab) {
            case '翻译图片':
              endpoint = '/get_imagetranslation';
              this.imageloading = true;
              break;
            case '翻译音频':
              endpoint = '/get_audiotranslation';
              this.yinpining = true;
              break;
            // Add more cases if needed
            default:
              console.error('Unsupported tab for upload');
              return;
          }
  
          const response = await axios.post(endpoint, formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          });
          this.textToTranslate = (response.data)['word'];
          this.imageloading = false;
          this.yinpining = false;
          this.$forceUpdate();
          console.log(this.textToTranslate);
        } catch (error) {
          console.error('Error uploading file:', error);
        }
      },
      toggleSourceLanguageMenu() {
        this.showSourceLanguageMenu = !this.showSourceLanguageMenu;
      },
      toggleTargetLanguageMenu() {
        this.showTargetLanguageMenu = !this.showTargetLanguageMenu;
      },
      setSourceLanguage(language) {
        this.sourceLanguage = language;
        this.showSourceLanguageMenu = false;
        this.targetLanguage = language === '中文' ? '英文' : '中文';
      },
      setTargetLanguage(language) {
        this.targetLanguage = language;
        this.showTargetLanguageMenu = false;
        this.sourceLanguage = language === '中文' ? '英文' : '中文';
      },
      toggleRecording() {
        this.recording = !this.recording;
        if (this.recording) {
          // Start recording logic
          console.log('开始录音');
          if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert('您的浏览器不支持语音识别功能。');
            return;
          }

          this.audioChunks = []; // Initialize audio chunks array

          navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
              this.mediaStream = stream; // Store the media stream for later use
              this.mediaRecorder = new MediaRecorder(stream);
              this.mediaRecorder.start();
              this.isRecording = true;

              this.mediaRecorder.ondataavailable = event => {
                this.audioChunks.push(event.data);
              };
            })
            .catch(error => {
              console.error('getUserMedia error:', error);
            });
        } else {
          // Stop recording logic
          if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            console.log('结束录音');
            this.yinpining = true;
            this.mediaRecorder.onstop = () => {
              const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
              this.audioChunks = [];
              const formData = new FormData();
              formData.append('audio', audioBlob, 'voice.wav');

              // Stop all tracks of the media stream
              this.mediaStream.getTracks().forEach(track => track.stop());

              // Send audio to the backend
              axios.post('/get_speechtranslation', formData, {
                headers: {
                  'Content-Type': 'multipart/form-data'
                }
              })
              .then((res) => {
                this.yinpining = false;
                console.log(res.data);
                this.textToTranslate = res.data.word; // Assuming the response contains translated text
                this.translationResult = res.data.translation;
              })
              .catch((err) => {
                console.error(err);
              });
            };
          }
        }
      }
    },
  };
  </script>
  
  <style scoped>
  .top-background {
  background-image: url('../../../assets/10.png'); /* 背景图片的路径 */
  background-size: cover; /* 让背景图片充满容器 */
  background-position: center; /* 居中显示背景图片 */
  background-repeat: no-repeat; /* 禁止背景图片重复 */
  height: 120px; /* 设置背景高度，根据需要调整 */
  text-align: center;
  padding-top: 20px;
  h1 
{
      margin-top: 0;
      padding: 10px;
      color: #0474de; /* 将颜色设置为白色 */
    }
}
  .translation-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    height: 80vh;
    padding: 20px;
    background: #ffffff;
    text-align: center;
    position: relative;
  }
  
  .back-button {
  position: absolute;
  margin-top:20px;
  top: 20px;
  right: 20px;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background: #007bff;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}
  .back-button:hover {
    background: #0056b3;
  }
  
  h1 {
    font-size: 2.5rem;
    margin-top: 40px;
    margin-bottom: 20px;
    color: #333;
  }
  
  .switch-tabs {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
    border-radius: 10px;
    background-color: #5aa0e6;
    overflow: hidden;
    width: 60%;
    margin: 0 auto 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .switch-tabs .tab {
    flex: 1;
    padding: 10px 0;
    font-size: 1.2rem;
    cursor: pointer;
    text-align: center;
    transition: background-color 0.3s, color 0.3s;
    color: #fff;
  }
  
  .switch-tabs .tab.active {
    background-color: #1a75d2;
    font-weight: bold;
  }
  
  .switch-tabs .tab:hover:not(.active) {
    background-color: #3b8edb;
  }
  
  .translation-content {
    display: flex;
    justify-content: space-between;
    width: 100%;
    max-width: 1200px;
    background: #f9f9f9;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .left-pane,
  .right-pane {
    width: 48%;
    height: 300px;
    display: flex;
    flex-direction: column;
    border: 1px solid #ddd;
    border-radius: 10px;
    background: #fff;
    padding: 15px;
  }
  
  .input-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex-grow: 1;
  }
  
  textarea {
    width: 100%;
    height: 100%;
    padding: 15px;
    border: none;
    resize: none;
    flex-grow: 1;
    font-size: 1rem;
    color: #050505;
    outline: none;
  }
  
  .language-selector {
    position: relative;
    margin-bottom: 10px;
  }
  
  .language-button {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    background: #007bff;
    color: #fff;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .language-button i {
    margin-right: 5px;
  }
  
  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 5px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .dropdown-menu li {
    padding: 10px;
    cursor: pointer;
    transition: background 0.3s;
  }
  
  .dropdown-menu li:hover {
    background: #f0f0f0;
  }
  
  .button-container {
    display: flex;
    justify-content: center;
    width: 100%;
    margin-bottom: 20px;
  }
  .upload-translate-group {
    display: flex;
    align-items: center;
  }

  .translate-button,
  .upload-button {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    background: #007bff;
    color: #fff;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-size: 1rem;
    margin-left: 10px;
    transition: background 0.3s, transform 0.3s;

  }
  
  .translate-button:hover,
  .upload-button:hover {
    background: #0056b3;
    transform: translateY(-3px);
  }
  
  .translate-button:active,
  .upload-button:active {
    transform: translateY(0);
  }
  
  .orange-button {
    background-color: orange;
    color: white; 
  }

  .file-input {
    display: none;
  }

  .loading-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-content {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  animation: waveAnimation 1s infinite linear; 
}
@keyframes waveAnimation {
  0% {
    transform: translateY(0); /* 初始位置 */
  }
  50% {
    transform: translateY(-5px); /* 波动上升 */
  }
  100% {
    transform: translateY(0); /* 回到初始位置 */
  }
}
  </style>