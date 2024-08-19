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
      <h1><i class="fas fa-book-open"></i> 文档归类</h1>
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
        <!-- Category Input Section -->
        <div class="category-input-container">
          <label for="category-input"><i class="fas fa-folder-plus"></i> 输入文档类别：</label>
          <input
            id="category-input"
            type="text"
            v-model="categoryInput"
            @keyup.enter="addCategory"
            placeholder="按回车键添加类别"
          />
        </div>

        <!-- Display Categories as Buttons -->
        <div class="category-list">
          <p v-if="categories.length === 0" class="empty-message">请逐个输入您需要的文档类别。</p>
          <button v-for="(category, index) in categories" :key="index" class="category-button">
            {{ category }} <span class="delete-button" @click="removeCategory(index)">×</span>
          </button>
        </div>

        <div class="upload-button-container">
          <button class="upload-button" @click="triggerFileUpload"><i class="fas fa-file-upload"></i>  {{ uploadButtonText }}</button>
          <input type="file" ref="fileUpload" style="display: none" @change="handleFileUpload" multiple />
        </div>
      </div>

      <!-- Right Section -->
      <div class="right-section">
        <h2><i class="fas fa-check-circle"></i> 分类结果</h2>
        <div class="upload-info">
          <div class="info-item">
            <span><i class="fas fa-file-alt"></i> 上传文档数量 ：</span>
            <div class="info-value">{{ uploadResults.length }}</div>
          </div>
          <div class="info-item">
            <span><i class="fas fa-folder-open"></i> 类别数量 ：</span>
            <div class="info-value">{{ countCategories }}</div>
          </div>
        </div>
        <div class="upload-results">
          <table>
            <thead>
              <tr>
                <th><i class="fas fa-list-ol"></i> 序号</th>
                <th><i class="fas fa-file"></i> 文件名</th>
                <th><i class="fas fa-folder"></i> 所属类别</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(result, index) in uploadResults" :key="index">
                <td>{{ index + 1 }}</td>
                <td>{{ result.filename }}</td>
                <td>{{ result.category }}</td>
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
      <h2><i class="fas fa-spinner fa-spin"></i> 文档分类中...</h2>
    </div>
  </div>
  <div v-if="hasCategory" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-folder-plus"></i> 请先在上方输入分类类别</h2>
      <button class="confirm-button" @click="hasCategory = false">确认</button>
    </div>
  </div>
</template>
<script>
import axios from 'axios';
export default {
  name: 'HomeworkManagement',
  data() {
    return {
      categoryInput: '', // 新增的类别输入框绑定的数据
      categories: [], // 存储所有添加的类别
      uploadResults: [],
      uploadButtonText: '批量上传文件',
      initialRows: 15,
      loading: false,
      hasCategory: false,
      guidetext: "1. 用户点击“批量上传文件”按键，从本地选择待分类文档。\n\n2.  用户在“输出文档类别”中输入预期分类的名称。（如备课、工作、试卷）\n\n3.  用户可以得到分类完毕后的文件夹压缩包",
      guidevisible:false,
    };
  },
  computed: {
    emptyRows() {
      return Math.max(this.initialRows - this.uploadResults.length, 0);
    },
    countCategories() {
      // 使用 Set 来计算唯一类别
      const uniqueCategories = new Set(this.uploadResults.map(result => result.category));
      return uniqueCategories.size; // 返回类别数量
    },
  },
  methods: {
    addCategory() {
      if (this.categoryInput.trim() && !this.categories.includes(this.categoryInput.trim())) {
        this.categories.push(this.categoryInput.trim());
        this.categoryInput = ''; // 清空输入框
      }
    },
    removeCategory(index) {
      this.categories.splice(index, 1);
    },
    triggerFileUpload() {
      // this.$refs.fileUpload.click();
      if (this.categories.length === 0) {
        // alert('请先输入待分类的文档类别');
        this.hasCategory = true;
        return;
      }
      this.$refs.fileUpload.click();
    },
    handleFileUpload(event) {
      if (this.categories.length === 0) {
        alert('请先输入待分类的文档类别');
        return;
      }

      const files = event.target.files;
      const formData = new FormData();
      formData.append("num_files", files.length);
      formData.append('categories', JSON.stringify(this.categories)); // 传递类别信息

      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]); // 注意这里传输的是 'files'
      }

      const url = '/docclassify'; // 调用后端分类接口
      this.loading = true;

      // 遍历并打印 FormData 数据
      formData.forEach((value, key) => {
        console.log(`${key}: ${value}`);
      });

      axios.post(url, formData, {
        responseType: 'json' // 处理 JSON 数据
      })
      .then(response => {
        // 处理分类信息和压缩文件
        const data = response.data;

        // 处理文件分类信息
        if (data.classification) {
          console.log('文件分类结果:', data.classification);
          // 将分类信息映射到 uploadResults 数组
          this.uploadResults = Object.entries(data.classification).map(([filename, category]) => {
            return { filename, category }; // 映射文件名和分类
          });
        }

        // 处理压缩文件下载
        if (data.zip_file) {
          // 使用 Axios 下载文件
          axios({
            url: data.zip_file,
            method: 'GET',
            responseType: 'blob' // 告诉 Axios 接收 Blob 类型的数据
          }).then(response => {
            const blob = new Blob([response.data], { type: 'application/zip' });
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = 'classified_documents.zip'; // 设置下载文件名
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            this.loading = false;
          }).catch(error => {
            this.loading = false;
            console.error('Error downloading the zip file:', error);
          });
        }
      })
      .catch(error => {
        this.loading = false;
        console.error('Error:', error);
      });
    },
    goBack() {
      this.$router.go(-1);
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

  .confirm-button {
    justify-content: center;
    align-items: center;
    margin-left: 110px;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    background-color: #3778e0;
    color: #fff;
    font-size: 1.2rem;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.3s;
    &:hover {
      background-color: #584eec;
      transform: translateY(-3px);
    }
  }

  .homework-management {
    text-align: center;
    background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    font-family: 'Arial, sans-serif';
    position: relative;
    
    .page-title {
      padding: 20px;
      background-image: url('../../../assets/PPTbackground.jpg');
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
      h1 {
        font-size: 2.5rem;
        color: #bcddfc;
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
      color: #acd2fa;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      position: absolute; 
      font-weight: bold;
      font-size: 1.5em;
      top:0px;
      right:100px;
    }
    .openguide-button:hover {
      color: #4ca0fa;
    }

    .return-button {
      padding: 10px 20px;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      background: #c3d6f4;
      color: #1630f7;
      font-size:1em;
      font-weight: bold;
      transition: background-color 0.3s, transform 0.3s;
      &:hover {
        background: #9a94f1;
        // transform: translateY(-5px);
      }
    }
  
    .content {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      height: 85vh;
      border: 4px solid transparent;
      border-radius: 5px;
      animation: border-rotation 3s linear infinite; 
  
      .left-section,
      .right-section {
        flex-grow: 1;
        // background: #ffffff;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);

        // border: 3px solid transparent;
        // border-radius: 5px;
        // animation: border-rotation 5s linear infinite; 
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
        width: 40%;
        display: flex;
        flex-direction: column;
        align-items: center;
        background: linear-gradient(-45deg, #A1CFFF, #B3E5FF, #CDEFFF, #D1F5FF);
        background-size: 300% 300%;
        animation: gradientAnimation 6s ease infinite; /* 添加循环渐变动画 */

        .category-input-container {
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 10px;
          label {
            color: #3778e0;
            font-size: 1.5rem;
            font-weight: bold;
          }
          input {
            padding: 10px;
            border: 2px solid #3778e0;
            border-radius: 5px;
            font-size: 1rem;
            margin-left: 5px;
            flex-grow: 1;
          }
        }

        .category-list {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          padding: 10px;
          border: 2px solid #3778e0;
          border-radius: 5px;
          width: 90%;
          height: 450px;
          background: #f7f7f7;

          .empty-message {
            color: #999;
            font-size: 1.4rem;
            text-align: center;
            width: 100%;
          }

          .category-button {
            display: flex;
            align-items: center;
            padding: 5px 10px;
            border: 1px solid #3778e0;
            background: #3778e0;
            color: #fff;
            border-radius: 5px;
            font-size: 1.2rem;
            height: 40px;
            cursor: pointer;

            .delete-button {
              margin-left: 10px;
              font-weight: bold;
              cursor: pointer;
            }
          }
        }
        .upload-button-container {
          display: flex;
          justify-content: center;
          margin-top: 20px;
        }

        .upload-button {
          padding: 10px 20px;
          border: none;
          border-radius: 5px;
          background-color: #3778e0;
          color: #fff;
          font-size: 1.2rem;
          cursor: pointer;
          transition: background-color 0.3s, transform 0.3s;
          &:hover {
            background-color: #584eec;
            transform: translateY(-3px);
          }
        }
      }
  
      .right-section {
        width: 40%;
        background: linear-gradient(-45deg, #FDF6E3, #FBE8A6, #F7C39D, #F5B37D);
        background-size: 300% 300%;
        animation: gradientAnimation 10s ease infinite; /* 添加循环渐变动画 */
        h2 {
          font-size: 1.5rem;
          color: #3778e0;
          margin-top: 1px;
          margin-bottom: 10px;
          i {
            margin-right: 8px;
            color: #3778e0;
          }
        }

        .upload-info {
          display: flex;
          justify-content: center; /* 居中对齐 */
          margin-bottom: 10px;
          .info-item {
            display: flex;
            flex-direction: row; /* 标签和值水平排列 */
            align-items: center; /* 垂直居中对齐 */
            color: #3778e0; /* 字体颜色蓝色 */
            margin-left: 10px;
            
            span:first-of-type {
              margin-right: 1px; /* 标签和数值之间的间距 */
              font-weight: bold; /* 标签加粗 */
            }
            
            .info-value {
              font-size: 1.2rem; /* 数值字体大小 */
              margin-right: 25px;
            }
          }
        }

        .upload-results {
          overflow-y: auto;
          height: 74%;
          width: 100%;
          padding: 10px;
          table {
            width: 100%;
            border-collapse: collapse;
            thead {
              background-color: #24daf1 !important; /* 冷色调背景色 */
              th {
                color: #0879f9; /* 冷色调文字颜色 */
                padding: 10px;
                text-align: center;
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
