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
  <div v-if="textloading" class="loading-dialog">
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
        <h2><i class="fas fa-spinner fa-spin"></i> PPT生成中...</h2>
      </div>
    </div>
    <!-- Loading Dialog -->
  <div v-if="yinpining" class="loading-dialog">
      <div class="loading-content">
        <h2><i class="fas fa-wave-square"></i> 音频解析中...</h2>
      </div>
    </div>
  <!-- Theme Selection Dialog -->
  <div v-if="showDialog" class="theme-dialog">
    <div class="theme-dialog-content">
      <button class="close-button" @click="showDialog = false">
        <i class="fas fa-times"></i>
      </button>

      <h2><i class="fas fa-tasks"></i> PPT具体需求</h2>

      <!-- PPT Style Section -->
      <h3><i class="fas fa-paint-brush"></i> PPT风格</h3>
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
      <h3><i class="fas fa-comment-dots"></i> 是否需要备注</h3>
      <div class="notes-buttons">
        <button @click="selectNotesOption(1)" :class="{ selected: notesOption === 1 }">
          <span class="radio-button"></span> <i class="fas fa-check-circle"></i>  是
        </button>
        <button @click="selectNotesOption(0)" :class="{ selected: notesOption === 0 }">
          <span class="radio-button"></span> <i class="fas fa-times-circle"></i>  否
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

  <!-- 页面顶部的图片背景 -->
  <!-- <div class="top-background">
    <h1><i class="fas fa-book-open"></i> PPT生成助手</h1>
    <button class="back-button" @click="goBack">
      <i class="fas fa-arrow-left"></i> 返回
    </button>
  </div> -->
  <div class="translation-container">
    <button class="back-button" @click="goBack">
      <i class="fas fa-arrow-left"></i> 返回
    </button> 
    <button class="openguide-button" @click="guidevisible = true"> <i class="fas fa-exclamation-circle"></i> </button>
        
    <h1><i class="fas fa-book-open"></i> PPT生成助手</h1>
    <div class="switch-tabs">
      <div
        v-for="tab in tabs"
        :key="tab.name"
        :class="['tab', { active: activeTab === tab.name }]"
        @click="setActiveTab(tab.name)"
      >
        <i :class="tab.icon"></i> {{ tab.label }}
      </div>
    </div>
    <div class="button-container">
      <label v-if="isTranslateFileTab || isTranslateImageTab || isTranslateAudioTab" class="upload-button">
        <i class="fas fa-cloud-upload-alt"></i> 上传
        <input type="file" @change="uploadFile" class="file-input" />
      </label>
      <div v-else-if="isTranslateSpeechTab">
        <button v-if="!isrecording" class="upload-button" @click="startVoiceRecognition">
          <i id="startIcon" class="fas fa-microphone"></i> 录音
        </button>
        <button v-if="isrecording" class="upload-button orange-button" @click="stopVoiceRecognition">
          <i id="stopIcon" class="fas fa-stop"></i> 结束录音
        </button>
      </div>
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
        // tabs: ['文本生成','文件生成', '图片生成', '音频生成', '语音生成'],
        tabs: [
          { name: '文本生成', label: '文本生成', icon: 'fas fa-file-alt' },
          { name: '文件生成', label: '文件生成', icon: 'fas fa-folder' },
          { name: '图片生成', label: '图片生成', icon: 'fas fa-image' },
          { name: '音频生成', label: '音频生成', icon: 'fas fa-music' },
          { name: '语音生成', label: '语音生成', icon: 'fas fa-microphone' }
        ],
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
        yinpining:false,
        imageloading:false,
        textloading:false,
        isrecording:false,
        mediaRecorder: null,
        audioChunks: [],
        stream: [],
        guidetext: "1.用户可以根据自身需求，使用文本，文件，图片，音频，语音（即时的录音）方式键入PPT的文本要求。\n\n2. 键入的文本会显示在左侧的文本框中，可以手动修改\n\n3. 确认文本无误后，点击“PPT生成”即可得到智能生成的PPT",
        guidevisible:false,
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
        this.textToTranslate = '';//0821
        this.translationResult = '';//0821
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
        axios.post('/conclude_text', requestData)
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
              this.imageloading=true;
              endpoint = '/get_imageppt';
              break;
            case '音频生成':
              this.yinpining = true;
              endpoint = '/get_audioppt';
              break;
            case '文件生成':
              this.textloading = true;
              endpoint = '/get_allfileppt';
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

          // 重置 input 的值，以确保下次选择同一个文件时仍然会触发事件
          event.target.value = null;
          this.imageloading = false;
          this.textloading = false;
          this.yinpining = false;
        } catch (error) {
          this.imageloading = false;
          this.textloading = false;
          this.yinpining = false;
          console.error('Error uploading file:', error);
        }
      },
      async generatePPT() {
        // 设置 loading 为 true，显示加载弹窗
        this.loading = true;
        this.showDialog = false;
        // 构建请求数据
        const requestData = {
          text: this.textToTranslate,
          theme: this.selectedTheme,
          isCardNote: this.notesOption
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
          this.translationResult = this.tmptext;
        } catch (error) {
          console.error('Error generating PPT:', error);
        }
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
            this.isrecording = true;

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
              this.isRecording = false;
              // 向后端发送请求
              axios.post('/get_speechtranslation', formData, {
                headers: {
                  'Content-Type': 'multipart/form-data'
                }
              })
              .then((res) => {
                this.isRecording = false;
                this.yinpining= false;
                this.textToTranslate = res.data.word; // Assuming the response contains translated text
              })
              .catch((err) => {
                this.isRecording = false;
                this.yinpining = false;
                console.error(err);
              });
            };
          })
          .catch(error => {
            this.isRecording = false;
            console.error('getUserMedia error:', error);
          });
      },
      stopVoiceRecognition() {
        this.recording = false;
        this.isrecording = false;
        this.$forceUpdate();
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
          this.mediaRecorder.stop();
          this.mediaRecorder = null;

          // Stop all tracks from the media stream
          if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null; 
          }
        }
      },
    },
  };
  </script>
  
  <style scoped>
  @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

/* .top-background {
  background-image: url('../../../assets/PPTbackground.jpg'); 背景图片的路径
  background-size: cover; 让背景图片充满容器
  background-position: center; 居中显示背景图片
  background-repeat: no-repeat; 禁止背景图片重复
  height: 90px; 设置背景高度，根据需要调整
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
  /* background: linear-gradient(-45deg, #A1CFFF, #B3E5FF, #CDEFFF, #D1F5FF); */
  /* background-size: 300% 300%; */
  /* animation: gradientAnimation 5s ease infinite; 添加循环渐变动画 */
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

.openguide-button {
    text-align: center;
    justify-self: center;
    padding: 0.5rem;
    display: inline-block; 
    vertical-align: middle;
    background-color: transparent;
    color: #bcd9f7;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    position: absolute; 
    font-weight: bold;
    font-size: 1.5em;
    top:35px;
    right:130px;
  }
  .openguide-button:hover {
    color: #77b4f7;
  }

.back-button {
  position: absolute;
  margin-top:20px;
  top: 20px;
  right: 20px;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background: #a0ddfe;
  color: #1228eb;
  font-size:1em;
  font-weight:bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.back-button:hover {
  background: #77b4f7;
  color:white;
}

h1 {
  font-size: 2.5rem;
  margin-top: 0px;
  margin-bottom: 20px;
  color: #c6e0fa;
}

.switch-tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  border-radius: 10px;
  background-color: #539eea;
  overflow: hidden;
  width: 60%;
  margin: 0 auto 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.switch-tabs .tab {
  flex: 1;
  padding: 10px 0;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  justify-content: center;
  text-align: center;
  transition: background-color 0.3s, color 0.3s;
  color: #fff;
}

.switch-tabs .tab.active {
  background-color: #0379ef;
  font-weight: bold;
  font-size: 1.4rem;
}

.switch-tabs .tab:hover:not(.active) {
  background-color: #3b8edb;
  font-weight: bold;
}

.translation-content {
  display: flex;
  justify-content: space-between;
  width: 100%;
  height:400px;
  max-width: 1200px;
  background: #f9f9f9;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background: linear-gradient(-45deg, #A1CFFF, #B3E5FF, #CDEFFF, #D1F5FF);
  background-size: 300% 300%;
  animation: gradientAnimation 5s ease infinite; /* 添加循环渐变动画 */
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

.left-pane,
.right-pane {
  width: 48%;
  height: 370px;
  display: flex;
  flex-direction: column;
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #fff;
  padding: 15px;
}
.left-pane {
  margin-right: 5px;
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
  font-size: 1.1em;
  font-weight: bold;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  background: #007bff;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  pointer-events: none;
}

.language-button i {
  margin-right: 5px;
  pointer-events: none;
}

/* .dropdown-menu {
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
} */

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
.orange-button {
  background-color: orange;
  color: white; /* 文字颜色 */
  /* 可以根据需要添加其他样式，如边框、阴影等 */
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
  /* background: #fff; */
  padding: 20px;
  border-radius: 10px;
  width: 80%;
  max-width: 600px;
  text-align: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  position: relative;
  background: linear-gradient(-45deg, #A1CFFF, #B3E5FF, #CDEFFF, #D1F5FF);
  background-size: 300% 300%;
  animation: gradientAnimation 5s ease infinite; /* 添加循环渐变动画 */
  h2{
    color:#007bff;
    font-size: 1.8em;
    font-weight: bold;
    margin-top: -5px;
  }
  h3{
    color:#2894f9;
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
  margin-right: 0px;
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
  animation: waveAnimation 1s infinite linear,color-cycle 3s linear infinite; 
}

/* 冷色调循环变色动画 */
@keyframes color-cycle {
  0% {
    color: #4a90e2; /* 冷蓝色 */
  }
  25% {
    color: #50e3c2; /* 冷青色 */
  }
  50% {
    color: #b8e986; /* 冷绿色 */
  }
  75% {
    color: #7ed321; /* 浅绿色 */
  }
  100% {
    color: #4a90e2; /* 回到初始冷蓝色 */
  }
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