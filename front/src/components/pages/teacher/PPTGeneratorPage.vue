<template>
  <div class="file-uploader">
    <!-- Page Title -->
    <div class="page-title">
      <h1>PPT生成</h1>
    </div>

    <!-- Content Section -->
    <div class="content">
      <!-- Left Section -->
      <div class="left-section">
        <div class="upload-section">
          <label for="file-upload" class="upload-label">上传文件：</label>
          <input type="file" id="file-upload" @change="handleFileUpload" accept=".pdf,.doc,.docx,.txt" />
        </div>
        <textarea v-if="!fileContent" readonly class="placeholder-textarea" placeholder="文件主要内容">文件主要内容</textarea>
        <textarea v-else v-model="fileContent" readonly placeholder="文件主要内容"></textarea>
      </div>

      <!-- Right Section -->
      <div class="right-section">
        <div class="generate-section">
          <button @click="downloadFile">生成PPT</button>
        </div>
        <textarea v-if="!fileContent" readonly class="placeholder-textarea" placeholder="PPT生成结果">PPT生成结果</textarea>
        <textarea v-else v-model="fileContent" readonly placeholder="PPT生成结果"></textarea>
      </div>
    </div>

    <!-- Back Button -->
    <button class="back-button" @click="goBack">返回</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      fileContent: '', // 存储文件主要内容
    };
  },
  methods: {
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.fileContent = e.target.result;
        };
        reader.readAsText(file); // 这里只读取文本文件内容
      }
    },
    downloadFile() {
      const content = this.fileContent || ''; // 如果没有上传文件，内容为空字符串
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'file-content.txt';
      a.click();
      URL.revokeObjectURL(url);
    },
    goBack() {
      this.$router.back();
    }
  },
};
</script>

<style scoped lang="scss">
.file-uploader {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 90%;
  height: 100%;
  margin: 0 auto;
  margin-top: 20px;
  position: relative;
}

.page-title {
  width: 100%;
  text-align: center;
  margin-bottom: 20px;

  h1 {
    font-size: 2rem;
    margin: 0;
  }
}

.content {
  display: flex;
  justify-content: space-between;
  width: 100%;
  gap: 20px;
}

.left-section,
.right-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.upload-section,
.generate-section {
  width: 100%;
  text-align: center;
  margin-bottom: 20px;

  .upload-label {
    font-weight: bold;
  }

  #file-upload,
  button {
    margin-top: 10px;
    padding: 10px;
    border: 1px solid #007BFF;
    border-radius: 4px;
    cursor: pointer;
    width: 80%;
    max-width: 300px;
  }

  button {
    margin-top: 10px;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 1em;
    padding: 10px;
    border: 1px solid #007BFF;
    border-radius: 3px;
    cursor: pointer;
    width: 80%;
    text-align: center;
    background-color: #007BFF;
    color: white;
    border: none;
    transition: background-color 0.3s;

    &:hover {
      background-color: #0056b3;
    }
  }
}

textarea {
  width: 100%;
  height: 500px;
  padding: 10px;
  border: 1px solid #0d0c0c;
  border-radius: 4px;
  font-family: inherit;
  resize: none;
  background-color: #f9f9f9;
}

.left-section {
  margin-right: 20px; /* 为左侧部分添加右边距 */
}

.right-section {
  margin-left: 20px; /* 为右侧部分添加左边距 */
}

.placeholder-textarea {
  width: 100%;
  height: 500px;
  padding: 10px;
  border: 1px solid #0d0c0c;
  border-radius: 4px;
  font-family: inherit;
  resize: none;
  background-color: #f9f9f9;
  position: relative;
  text-align: center;
  font-size: 1.2rem; /* Adjust font size as needed */
}

.placeholder-textarea::before {
  content: attr(placeholder);
  position: absolute;
  top: 50%;
  left: 10px;
  transform: translateY(-50%);
  color: #ccc; /* Adjust color to a lighter shade */
}

.back-button {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 10px 20px;
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;

  &:hover {
    background-color: #0056b3;
  }
}
</style>
