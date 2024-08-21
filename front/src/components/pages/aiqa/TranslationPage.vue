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
  <div v-if="fileloading" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-spinner fa-spin"></i> 文件解析中...</h2>
    </div>
  </div>
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
  <div class="translation-container">
    <button class="openguide-button" @click="guidevisible = true"> <i class="fas fa-exclamation-circle"></i> </button>
    <button class="back-button" @click="goBack">
      <i class="fas fa-arrow-left"></i> 返回
    </button> 
    <h1><i class="fas fa-book-open"></i> 即时翻译</h1>
    <div class="switch-tabs">
      <div
        v-for=" (tab, index) in tabs"
        :key="tab"
        :class="['tab', { active: activeTab === tab }]"
        @click="setActiveTab(tab)"
      >
        <i :class="['fas', tabIcons[index]]"></i>
        {{ tab }}
      </div>
    </div>
    <div class="button-container">
      <button v-if="isTranslateTextTab" @click="translateText" class="translate-button">
        <i class="fas fa-language"></i> 翻译
      </button>
      <div v-else-if="isTranslateFileTab || isTranslateImageTab || isTranslateAudioTab" class="upload-translate-group">
        <label class="upload-button">
          <i class="fas fa-upload"></i> 上传
          <input type="file" @change="uploadFile" class="file-input" />
        </label>
        <button @click="translateText" class="translate-button">
          <i class="fas fa-language"></i> 翻译
        </button>
      </div>
      <div v-else-if="isTranslateSpeechTab" class="upload-translate-group">
        <!-- <button @click="toggleRecording" class="upload-button" :class="{'orange-button': recording}">
          <i :class="recording ? 'fas fa-stop' : 'fas fa-microphone'"></i> {{ recording ? '结束录音' : '录音' }}
        </button> -->
        <button v-if="!recording" class="upload-button" @click="startVoiceRecognition">
          <i id="startIcon" class="fas fa-microphone"></i> 录音
        </button>
        <button v-else-if="recording" class="upload-button orange-button" @click="stopVoiceRecognition">
          <i id="stopIcon" class="fas fa-stop"></i> 结束录音
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
      <div v-else-if="isTranslateFileTab || isTranslateImageTab || isTranslateAudioTab" class="left-pane">
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
          <!-- 下载图标按钮 -->
          <button class="download-button" @click="downloadTranslation">
            <i class="fas fa-download"></i> 下载结果
          </button>
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
        tabs: ['翻译文本', '翻译文件', '翻译图片', '翻译音频', '翻译语音'],
        tabIcons: ['fa-file-alt', 'fa-folder','fa-image', 'fa-music', 'fa-microphone'],
        activeTab: '翻译文本',
        textToTranslate: '',
        translationResult: '',
        sourceLanguage: '源语言',
        targetLanguage: '目标语言',
        showSourceLanguageMenu: false,
        showTargetLanguageMenu: false,
        recording: false, // 新增录音状态
        yinpining:false,
        fileloading:false,
        loading:false,
        imageloading:false,
        mediaRecorder: null,
        audioChunks: [],
        stream: [],
        guidetext: "1. 用户可以根据自身需求，使用文本，图片，音频，语音（即时的录音）方式键入文本\n\n2. 键入的文本会显示在左侧的文本框中，可以手动修改\n\n3. 确认文本无误后，点击“源语言”和“目标语言”选择翻译的语言种类\n\n4. 点击“翻译”即可在右侧得到翻译结果",
        guidevisible:false,
      };
    },
    computed: {
      isTranslateTextTab() {
        return this.activeTab === '翻译文本';
      },
      isTranslateFileTab() {
        return this.activeTab === '翻译文件';
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
        this.textToTranslate = '';//0821
        this.translationResult = '';//0821
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
            case '翻译文件':
              endpoint = '/get_allfileppt'
              this.fileloading = true;
              break;
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
          console.log('formData',formData)
          const response = await axios.post(endpoint, formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          });
          // 重置 input 的值，以确保下次选择同一个文件时仍然会触发事件
          event.target.value = null;
          this.textToTranslate = (response.data)['word'];
          this.imageloading = false;
          this.fileloading = false;
          this.yinpining = false;
          this.$forceUpdate();
          console.log(this.textToTranslate);
        } catch (error) {
          this.imageloading = false;
          this.yinpining = false;
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
      startVoiceRecognition() {
        this.recording = true;
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          alert('您的浏览器不支持语音识别功能。');
          return;
        }

        navigator.mediaDevices.getUserMedia({ audio: true })
          .then(stream => {
            this.mediaRecorder = new MediaRecorder(stream);
            this.mediaRecorder.start();
            this.stream = stream; 
            this.recording = true;

            this.mediaRecorder.ondataavailable = event => {
              this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
              const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
              this.audioChunks = [];
              const formData = new FormData();
              formData.append('audio', audioBlob, 'voice.wav');

              // Display thinking message
              this.yinpining = true;

              // 向后端发送请求
              axios.post('/get_speechtranslation', formData, {
                headers: {
                  'Content-Type': 'multipart/form-data'
                }
              })
              .then((res) => {
                this.yinpining= false;
                this.textToTranslate = res.data.word; // Assuming the response contains translated text
              })
              .catch((err) => {
                this.yinpining = false;
                console.error(err);
              });
            };
          })
          .catch(error => {
            console.error('getUserMedia error:', error);
          });
      },
      stopVoiceRecognition() {
        this.recording = false;
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
          this.mediaRecorder.stop();
          this.mediaRecorder = null;
          this.isRecording = false;

          // Stop all tracks from the media stream
          if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null; 
          }
        }
      },
      downloadTranslation() {
        // 创建一个Blob对象，用于存储翻译结果
        const blob = new Blob([this.translationResult], { type: 'text/plain;charset=utf-8' });

        // 创建一个链接并模拟点击，触发文件下载
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = '翻译结果.txt'; // 指定下载文件的名称
        link.click();

        // 释放URL对象资源
        URL.revokeObjectURL(link.href);
      },
    },
  };
  </script>
  
  <style scoped>
  /* .top-background {
  background-image: url('../../../assets/10.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat; 
  height: 120px;
  text-align: center;
  padding-top: 20px;
  h1 
{
      margin-top: 0;
      padding: 10px;
      color: #0474de; 
    }
} */
  .translation-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    height: 92vh;
    padding: 20px;
    /* background: #ffffff; */
    text-align: center;
    position: relative;
    background-image: url('../../../assets/PPTbackground.jpg'); /* 背景图片的路径 */
    background-size: cover; /* 让背景图片充满容器 */
    background-position: center; /* 居中显示背景图片 */
    background-repeat: no-repeat; /* 禁止背景图片重复 */
  }
  .openguide-button {
  text-align: center;
  justify-self: center;
  padding: 0.5rem;
  display: inline-block; 
  vertical-align: middle;
  background-color: transparent;
  color: #007bff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  position: absolute; 
  font-weight: bold;
  font-size: 1.5em;
  top:28px;
  right:120px;
}
.openguide-button:hover {
  color: #4ca0fa;
}

  .back-button {
  position: absolute;
  font-size: 1.2em;
  font-weight: bold;
  margin-top:20px;
  top: 5px;
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
    background: hsl(211, 94%, 65%);
  }
  
  h1 {
    font-size: 2.5rem;
    margin-top: 0px;
    margin-bottom: 20px;
    color: #63aef9;
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
    background: linear-gradient(-45deg, #A1CFFF, #B3E5FF, #CDEFFF, #D1F5FF);
    border-radius: 10px;
    padding: 20px !important;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .left-pane,
  .right-pane {
    width: 48%;
    height: 400px;
    display: flex;
    flex-direction: column;
    border: 1px solid #ddd;
    border-radius: 5px;
    background: #fff;
    padding: 15px;
  }
  
  .input-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex-grow: 1;
  }

  .download-button {
    position: absolute;
    top: 267px;
    right: 180px !important;
    cursor: pointer;
    color: #ffffff;
    background-color: #007bff;
    font-size: 16px;
    padding: 4px;
    border-radius: 10px;
    border: 2px solid #007bff;
  }

  .download-button:hover {
    background-color: #056cda;
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
    display: flex;
    align-items: center;
    padding: 10px;
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
  background: linear-gradient(-45deg, #A1CFFF, #B3E5FF, #CDEFFF, #D1F5FF); 
  background-size: 300% 300%; 
  animation: waveAnimation 1s infinite linear , gradientAnimation 5s ease infinite; 
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