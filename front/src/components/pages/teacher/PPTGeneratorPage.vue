<template>
  <!-- Loading Dialog -->
  <div v-if="loading" class="loading-dialog">
      <div class="loading-content">
        <h2><i class="fas fa-spinner fa-spin"></i> PPT生成中...</h2>
      </div>
    </div>
  <!-- Theme Selection Dialog -->
  <div v-if="showDialog" class="theme-dialog">
    <div class="theme-dialog-content">
      <button class="close-button" @click="showDialog = false">
        <i class="fas fa-times"></i>
      </button>

      <h2>PPT具体需求</h2>

      <!-- PPT Style Section -->
      <h3>PPT风格</h3>
      <div class="theme-buttons">
        <button @click="selectTheme('auto')" :class="{ selected: selectedTheme === 'auto' }">自动</button>
        <button @click="selectTheme('purple')" :class="{ selected: selectedTheme === 'purple' }">紫色主题</button>
        <button @click="selectTheme('green')" :class="{ selected: selectedTheme === 'green' }">绿色主题</button>
        <button @click="selectTheme('lightblue')" :class="{ selected: selectedTheme === 'lightblue' }">清逸天蓝</button>
      </div>
      <div class="theme-buttons">
        <button @click="selectTheme('taupe')" :class="{ selected: selectedTheme === 'taupe' }">质感之境</button>
        <button @click="selectTheme('blue')" :class="{ selected: selectedTheme === 'blue' }">星光夜影</button>
        <button @click="selectTheme('telecomRed')" :class="{ selected: selectedTheme === 'telecomRed' }">炽热暖阳</button>
        <button @click="selectTheme('telecomGreen')" :class="{ selected: selectedTheme === 'telecomGreen' }">幻翠奇旅</button>
      </div>

      <!-- PPT Notes Section -->
      <h3>是否需要备注</h3>
      <div class="notes-buttons">
        <button @click="selectNotesOption(1)" :class="{ selected: notesOption === 1 }">
          <span class="radio-button"></span> 是
        </button>
        <button @click="selectNotesOption(0)" :class="{ selected: notesOption === 0 }">
          <span class="radio-button"></span> 否
        </button>
      </div>

      <!-- Generate PPT Button -->
      <div class="generate-ppt-button">
        <button @click="generatePPT">
          <i class="fas fa-file-powerpoint"></i> 开始生成PPT
        </button>
      </div>
    </div>
  </div>

  <div class="translation-container">
    <button class="back-button" @click="goBack">
      <i class="fas fa-arrow-left"></i> 返回
    </button>
    <h1>PPT生成助手</h1>
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
      <label v-if="isTranslateFileTab || isTranslateImageTab || isTranslateAudioTab" class="upload-button">
        <i class="fas fa-cloud-upload-alt"></i> 上传
        <input type="file" @change="uploadFile" class="file-input" />
      </label>
      <button v-else-if="isTranslateSpeechTab" @click="toggleRecording" class="upload-button">
        <i :class="recording ? 'fas fa-stop' : 'fas fa-microphone'"></i> {{ recording ? '结束录音' : '录音' }}
      </button>
      <button @click="showDialog = true" class="upload-ppt-button">
        <i class="fas fa-file-powerpoint"></i> PPT生成
      </button>
    </div>
    <div class="translation-content">
      <div v-if="isTranslateTextTab" class="left-pane">
        <div class="input-container">
          <div class="language-selector">
            <button class="language-button">
              <i class="fas fa-globe"></i> {{ sourceLanguage }}
            </button>
          </div>
          <textarea
            v-model="textToTranslate"
            placeholder="键入文本后点击PPT生成按钮，讯飞智教将为您生成相应的PPT。"
            @keyup.enter="concludeText"
          ></textarea>
        </div>
      </div>
      <div v-else-if="isTranslateFileTab || isTranslateImageTab || isTranslateAudioTab" class="left-pane">
        <div class="input-container">
          <div class="language-selector">
            <button class="language-button">
              <i class="fas fa-globe"></i> {{ sourceLanguage }}
            </button>
          </div>
          <textarea
            v-model="textToTranslate"
            placeholder="上传文件后点击PPT生成按钮，讯飞智教将为您生成相应的PPT。"
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
          </div>
          <textarea
            v-model="textToTranslate"
            placeholder="录入语音后点击PPT生成按钮，讯飞智教将为您生成相应的PPT。"
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
          </div>
          <textarea
            v-model="translationResult"
            placeholder="PPT内容概述"
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
        tabs: ['文本生成','文件生成', '图片生成', '音频生成', '语音生成'],
        activeTab: '文本生成',
        textToTranslate: '',
        tmptext: '',
        translationResult: '',
        sourceLanguage: '主要内容',
        targetLanguage: 'PPT简介',
        recording: false, // 新增录音状态
        showDialog: false,
        selectedTheme: 'auto', // 默认选择的主题
        notesOption: 1, // 默认选择的备注选项
        loading: false,
      };
    },
    computed: {
      isTranslateTextTab() {
        return this.activeTab === '文本生成';
      },
      isTranslateFileTab() {
        return this.activeTab === '文件生成';
      },
      isTranslateImageTab() {
        return this.activeTab === '图片生成';
      },
      isTranslateAudioTab() {
        return this.activeTab === '音频生成';
      },
      isTranslateSpeechTab() {
        return this.activeTab === '语音生成';
      }
    },
    methods: {
      goBack() {
        this.$router.go(-1);
      },
      setActiveTab(tab) {
        this.activeTab = tab;
      },
      selectTheme(theme) {
        this.selectedTheme = theme;
      },
      selectNotesOption(option) {
        this.notesOption = option;
      },
      concludeText() {
        // 准备发送给后端的数据
        const requestData = {
          text: this.textToTranslate
        };

        // 发起 POST 请求
        axios.post('http://localhost:5000/conclude_text', requestData)
          .then(response => {
            // 处理后端返回的数据
            console.log('后端返回的结果:', response.data);
            // 在这里处理返回的数据，例如更新界面上的显示结果等操作
            this.tmptext = response.data.translation; // 假设后端返回一个 translation 字段
          })
          .catch(error => {
            console.error('发送请求时出错:', error);
            // 在这里处理错误，例如显示错误信息给用户
          });
      },
      async uploadFile(event) {
        const file = event.target.files[0];
        if (!file) return;
  
        const formData = new FormData();
        formData.append('file', file);
  
        try {
          let endpoint;
          switch (this.activeTab) {
            case '图片生成':
              endpoint = 'http://localhost:5000/get_imageppt';
              break;
            case '音频生成':
              endpoint = 'http://localhost:5000/get_audioppt';
              break;
            case '文件生成':
              endpoint = 'http://localhost:5000/get_fileppt';
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
          this.tmptext = (response.data)['ans'];
          this.$forceUpdate();
          console.log(this.textToTranslate);
        } catch (error) {
          console.error('Error uploading file:', error);
        }
      },
      async generatePPT() {
        // 设置 loading 为 true，显示加载弹窗
        this.loading = true;

        // 构建请求数据
        const requestData = {
          text: this.textToTranslate,
          theme: this.selectedTheme,
          isCardNote: this.notesOption
        };

        try {
          // 发送请求
          const response = await axios.post('http://localhost:5000/downloadppt', requestData, {
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
          this.translationResult = this.tmptext;
        } catch (error) {
          console.error('Error generating PPT:', error);
        }
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
          if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            console.log('结束录音');

            this.mediaRecorder.onstop = () => {
              const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
              this.audioChunks = [];
              const formData = new FormData();
              formData.append('audio', audioBlob, 'voice.wav');

              // Stop all tracks of the media stream
              this.mediaStream.getTracks().forEach(track => track.stop());

              // Send audio to the backend
              axios.post('http://localhost:5000/get_speechppt', formData, {
                headers: {
                  'Content-Type': 'multipart/form-data'
                }
              })
              .then((res) => {
                console.log(res.data);
                this.textToTranslate = res.data.word; // Assuming the response contains translated text
                this.tmptext = (res.data)['ans'];
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
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
.translation-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  height: 100vh;
  padding: 20px;
  background: #ffffff;
  text-align: center;
  position: relative;
}

.back-button {
  position: absolute;
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
  gap: 10px; /* 添加这个样式来增加按钮之间的间距 */
}

.translate-button,
.upload-button,
.upload-ppt-button { /* 包括新的上传PPT按钮 */
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
  transition: background 0.3s, transform 0.3s;
}

.translate-button:hover,
.upload-button:hover,
.upload-ppt-button:hover { /* 包括新的上传PPT按钮 */
  background: #0056b3;
  transform: translateY(-3px);
}

.translate-button:active,
.upload-button:active,
.upload-ppt-button:active { /* 包括新的上传PPT按钮 */
  transform: translateY(0);
}

.file-input {
  display: none;
}
.theme-dialog {
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

.theme-dialog-content {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  width: 80%;
  max-width: 600px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  position: relative;
}

.close-button {
    position: absolute;
    top: 15px; /* 调整上边距 */
    right: 15px; /* 调整右边距 */
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 1.5rem;
    color: #d02222;
}

.close-button i {
    font-size: 1.5rem;
}

.close-button:hover {
    color: #007bff;
}

.theme-dialog h2, .theme-dialog h3 {
  margin-bottom: 20px;
}

.theme-buttons, .notes-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.theme-buttons button, .notes-buttons button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s, color 0.3s;
}

.theme-buttons button.selected, .notes-buttons button.selected {
  background: #007bff;
  color: #fff;
}

.theme-buttons button:not(.selected):hover, .notes-buttons button:not(.selected):hover {
  background: #0056b3;
  color: #fff;
}

.radio-button {
  margin-right: 5px;
}

.generate-ppt-button {
  display: flex;
  justify-content: center;
}

.generate-ppt-button button {
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
  transition: background 0.3s, transform 0.3s;
}

.generate-ppt-button button:hover {
  background: #0056b3;
  transform: translateY(-3px);
}

.generate-ppt-button button:active {
  transform: translateY(0);
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
}
</style>