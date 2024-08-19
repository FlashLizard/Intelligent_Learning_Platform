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
  <div class="homework-management">
    <!-- Page Title -->
    <div class="page-title">
      <h1><i class="fas fa-book-open"></i> 背诵管理</h1>
    </div>

    <!-- Return Button -->
    <div class="top-right">
      <button class="openguide-button" @click="guidevisible = true"> <i class="fas fa-exclamation-circle"></i> </button>
      <button class="return-button" @click="goBack"><i class="fas fa-arrow-left"></i> 返回</button>
    </div>

    <!-- Content Section -->
    <div class="content">
      <!-- Left Section -->
      <div class="left-section">
        <div class="upload-container">
          <!-- Upload Answer Button -->
          <button class="upload-answer-button" @click="triggerAnswerUpload"><i class="fas fa-file-upload"></i> 上传答案</button>
          <!-- File Input for Answer Upload -->
          <input type="file" id="answer-upload" ref="answerUpload" style="display: none" @change="handleAnswerUpload">
          
          <!-- File Upload Button for Homework -->
          <input type="file" id="file-upload" ref="fileUpload" multiple style="display: none" @change="handleFileUpload">
          <button class="upload-button" @click="triggerFileUpload"><i class="fas fa-upload"></i> {{ uploadButtonText }}</button>
        </div>

        <!-- Standard Answer Title -->
        <h2 class="standard-answer-title"><i class="fas fa-file-alt"></i> 标准答案</h2>
        <!-- Standard Answer Textarea -->
        <textarea class="standard-answer" v-model="standardAnswer" placeholder="标准答案"></textarea>
      </div>

      <!-- Right Section -->
      <div class="right-section">
        <h2><i class="fas fa-check-circle"></i> 批改结果</h2>
        <div class="upload-info">
          <div class="info-item">
            <span><i class="fas fa-file-alt"></i> 上传作业数量：</span>
            <div class="info-value">{{ uploadResults.length }}</div>
          </div>
          <div class="info-item">
            <span><i class="fas fa-chart-pie"></i> 平均正确率：</span>
            <div class="info-value">{{ calculateAccuracy() }}%</div>
          </div>
        </div>
        <div class="upload-results">
          <table>
            <thead>
              <tr>
                <th><i class="fas fa-list-ol"></i> 序号</th>
                <th><i class="fas fa-file-alt"></i> 文件名</th>
                <th><i class="fas fa-percentage"></i> 正确率</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(result, index) in uploadResults" :key="index">
                <td>{{ index + 1 }}</td>
                <td>{{ result.filename }}</td>
                <td>{{ result.accuracy }}</td>
              </tr>
              <tr v-for="index in emptyRows" :key="'empty' + index">
                <td>&nbsp;</td>
                <td>&nbsp;</td>
                <td>&nbsp;</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
  <div v-if="loading" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-spinner fa-spin"></i> 背诵作业批改中...</h2>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  name: 'HomeworkManagement',
  data() {
    return {
      standardAnswer: '',
      uploadResults: [],
      uploadButtonText: '批量上传作业',
      initialRows: 15,
      loading:false,
      guidetext: "1. 用户点击“上传答案”按键，从本地选择答案文件\n\n2. 用户点击“批量上传答案”按键，从本地选择待检查的录音。\n\n3. 用户可以从右侧的方框中得到智能批改的结果。",
      guidevisible:false,
    };
  },
  computed: {
    emptyRows() {
      return Math.max(this.initialRows - this.uploadResults.length, 0);
    }
  },
  methods: {
    triggerFileUpload() {
      this.$refs.fileUpload.click();
    },
    handleFileUpload(event) {
      const files = event.target.files;

      const formData = new FormData();

      //const int file_count = files.length;
      formData.append("num_files",files.length);
      // 将文本框中的答案字符串转换为 txt 文件
      const standardAnswerFile = new File([this.standardAnswer], 'standardanswer.txt', {
        type: 'text/plain'
      });
      this.loading = true;
      // 将标准答案文件添加到 FormData 对象中
      formData.append('answer', standardAnswerFile);

      // 将作业文件添加到 FormData 对象中
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        formData.append('audio_files', file);
      }

      const url = '/uploadhomework';
      
      console.log('formData',formData)
      axios.post(url, formData)
      .then(response => response.data)
      .then(data => {
        // 处理后端返回的 accuracy_results
        console.log('accuracy_results:', data);
        this.uploadResults.push(...Object.entries(data).map(([filename, accuracy]) => ({ filename, accuracy })));
        console.log(this.uploadResults)
        this.uploadButtonText = '继续上传作业';
        this.loading = false;
      })
      .catch(error => {
        this.loading = false;
        console.error('Error:', error);
      });
    },
    triggerAnswerUpload() {
      this.$refs.answerUpload.click();
    },
    handleAnswerUpload(event) {
      const file = event.target.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.standardAnswer = e.target.result;
      };
      reader.readAsText(file);
    },
    calculateAccuracy() {
      if (this.uploadResults.length === 0) return 0;

      const totalAccuracy = this.uploadResults.reduce((total, result) => {
        let accuracy = result.accuracy;
        // 使用正则表达式提取数值部分
        const match = accuracy.match(/([\d.]+)/);
        if (match) {
          accuracy = parseFloat(match[1]);
        } else {
          accuracy = NaN;
        }

        if (!isNaN(accuracy)) {
          return total + accuracy;
        } else {
          console.warn(`Invalid accuracy value: ${result.accuracy}`);
          return total;
        }
      }, 0);

      const averageAccuracy = totalAccuracy / this.uploadResults.length;
      return averageAccuracy.toFixed(2);
    },
    goBack() {
      this.$router.go(-1); // 返回到上一页
    }
  }
};
</script>

<style scoped lang="scss">
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

.loading-spinner {
  margin-top: 10px;
  text-align: center;
}

.homework-management {
  text-align: center;
  // padding: 10px;
  background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  color: #333;
  font-family: 'Arial, sans-serif';
  position: relative;
  
  .page-title {
    // margin-bottom: 20p
    padding:20px;
    background-image: url('../../../assets/PPTbackground.jpg'); /* 背景图片的路径 */
    background-size: cover; /* 让背景图片充满容器 */
    background-position: center; /* 居中显示背景图片 */
    background-repeat: no-repeat; /* 禁止背景图片重复 */
    h1 {
      font-size: 2.5rem;
      color: #b2d8fc;
      margin: 0;

      i {
        margin-right: 10px;
      }
    }
  }

  .top-right {
    position: absolute;
    top: 20px;
    right: 20px;
  }
  .openguide-button {
    text-align: center;
    justify-self: center;
    padding: 0.5rem;
    display: inline-block; 
    vertical-align: middle;
    background-color: transparent;
    color: #c3cbf9;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    position: absolute; 
    font-weight: bold;
    font-size: 1.5em;
    top:0px;
    right:130px;
  }
  .openguide-button:hover {
    color: #98a7fd;
  }
  .return-button {
    padding: 10px 20px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.3s;
    background: #c4d8fa;
    color: #4542fc;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);

    &:hover {
      background: #a7a1fa;
      // transform: translateY(-5px);
    }
  }

  .content {
    display: flex;
    justify-content: space-between;
    gap: 2px;
    // margin-top: 20px;
    height: 85vh;
    border: 3px solid transparent;
    border-radius: 5px !important;
    animation: border-rotation 3s linear infinite; 

    .left-section,
    .right-section {
      flex-grow: 1;
      background: #ffffff;
      padding: 20px;
      border-radius: 2px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
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

    .left-section {
      width: 45%;
      display: flex;
      flex-direction: column;
      align-items: center;

      .upload-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px; /* 缩小间距 */
      }

      .upload-answer-button,
      .upload-button {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px 20px;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        transition: background-color 0.3s, transform 0.3s;
        background: #3778e0;
        color: #fff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);

        &:hover {
          background: #584eec;
          transform: translateY(-5px);
        }

        i {
          margin-right: 5px;
        }
      }

      .upload-button {
        margin-left: 10px;
      }

      .standard-answer-title {
        font-size: 1.5rem;
        color: #064ec1;
        text-align: center;
        margin-bottom: 10px; /* 缩小间距 */

        i {
          margin-right: 8px;
          color: #064ec1;
        }
      }

      .standard-answer {
        width: 100%;
        height: 100%;
        margin-bottom: 20px;
        padding: 10px;
        border: 1px solid #0f0e0e;
        border-radius: 5px;
        font-size: 1rem;
        resize: none;
      }
    }

    .right-section {
      width: 45%;
      display: flex;
      flex-direction: column;
      align-items: center;

      h2 {
        margin-top:-5px;
        font-size: 1.5rem;
        color: #064ec1;
        margin-bottom: 30px;

        i {
          margin-right: 8px;
          color: #064ec1;
        }
      }

      .upload-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        padding-bottom: 10px;

        .info-item {
          font-weight: bold;
          display: flex;
          align-items: center;
          margin-right: 30px;
          color: #064ec1;

          i {
            margin-right: 5px;
            color: #064ec1;
          }
        }

        .info-value {
          padding: 5px;
          margin-left: 5px;
        }
      }

      .upload-results {
        overflow-y: auto;
        height: 74%;
        width: 100%;
        border: 1.5px solid #000;
        border-radius: 3px;
        padding: 10px;

        table {
          width: 100%;
          border-collapse: collapse;

          thread {
            tr{
              th{
                color: 3778e0;
              }
            }
          }

          th, td {
            border: 1px solid #797777;
            padding: 8px;
            text-align: center;
          }

          th {
            background-color: #f2f2f2;
          }

          tr:hover {
            background-color: #e6f7ff;
          }
        }
      }
    }

    /* 移除右侧部分的悬停效果 */
    .right-section:hover {
      transform: none;
      box-shadow: none;
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
