<template>
    <div class="homework-management">
      <!-- Page Title -->
      <div class="page-title">
        <h1>作业管理</h1>
      </div>
  
      <!-- Return Button -->
      <div class="top-right">
        <button class="return-button" @click="goBack">返回</button>
      </div>
  
      <!-- Content Section -->
      <div class="content">
        <!-- Left Section -->
        <div class="left-section">
          <textarea class="standard-answer" v-model="standardAnswer" placeholder="标准答案"></textarea>
          <input type="file" id="file-upload" ref="fileUpload" multiple style="display: none" @change="handleFileUpload">
          <button class="upload-button" @click="triggerFileUpload">批量上传作业</button>
        </div>
  
        <!-- Right Section -->
        <div class="right-section">
          <h2>批改结果</h2>
          <ul>
            <li v-for="(result, index) in uploadResults" :key="index">{{ result }}</li>
          </ul>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'HomeworkManagement',
    data() {
      return {
        standardAnswer: '',
        uploadResults: []
      };
    },
    methods: {
      triggerFileUpload() {
        this.$refs.fileUpload.click();
      },
      handleFileUpload(event) {
        const files = event.target.files;
        this.uploadResults = []; // Clear previous results
        for (let i = 0; i < files.length; i++) {
          const file = files[i];
          const reader = new FileReader();
          reader.onload = (e) => {
            const content = e.target.result;
            // 模拟批改作业逻辑，这里简单判断文件内容是否包含标准答案的文字
            const result = content.includes(this.standardAnswer) ? '正确' : '错误';
            this.uploadResults.push(`作业${i + 1}：${result}`);
          };
          reader.readAsText(file);
        }
      },
      goBack() {
        this.$router.go(-1); // 返回到上一页
      }
    }
  };
  </script>
  
  <style scoped lang="scss">
  .homework-management {
    text-align: center;
    padding: 1px;
    background: #f0f0f0;
    border-radius: 1px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    color: #333;
    font-family: 'Arial, sans-serif';
  
    .page-title {
      margin-bottom: 20px;
  
      h1 {
        font-size: 2.5rem;
        color: #333;
        margin: 0;
      }
    }
  
    .top-right {
      position: absolute;
      top: 20px;
      right: 20px;
    }
  
    .return-button {
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
    }
  
    .content {
      display: flex;
      justify-content: space-between;
      gap: 20px;
      margin-top: 20px;
  
      .left-section,
      .right-section {
        flex: 1;
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
  
        &:hover {
          transform: translateY(-5px);
          box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }
      }
  
      .left-section {
        display: flex;
        flex-direction: column;
        align-items: center;
  
        .standard-answer {
          width: 100%;
          height: 200px;
          margin-bottom: 20px;
          padding: 10px;
          border: 1px solid #ccc;
          border-radius: 5px;
          font-size: 1rem;
          resize: none;
        }
  
        .upload-button {
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
        }
      }
  
      .right-section {
        display: flex;
        flex-direction: column;
        align-items: center;
  
        h2 {
          font-size: 1.5rem;
          color: #444;
          margin-bottom: 20px;
        }
  
        ul {
          list-style-type: none;
          padding: 0;
          width: 100%;
  
          li {
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background: #f9f9f9;
          }
        }
      }
    }
  }
  </style>
  