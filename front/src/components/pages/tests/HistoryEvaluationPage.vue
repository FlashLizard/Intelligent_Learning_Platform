<template>
  <div class="evaluation-page">
    <header>
      <h1><i class="fas fa-star"></i>学情评估 </h1>
      <div class="stars">
        <div v-for="n in 6" :key="n" class="star" :ref="'starTitle' + n"></div>
      </div>
      <button @click="goBack"><i class="fas fa-arrow-left"></i> 返回</button>
    </header>
    <div class="content">
      <div class="left-panel">
        <div class="evaluation-section">
          <h2><i class="fas fa-star"></i> 评价</h2>
          <textarea v-model="evaluation" readonly></textarea>
        </div>
        <div class="evaluation-section">
          <h2><i class="fas fa-exclamation-triangle"></i> 不足</h2>
          <textarea v-model="shortcoming" readonly></textarea>
        </div>
        <div class="evaluation-section">
          <h2><i class="fas fa-lightbulb"></i> 建议</h2>
          <textarea v-model="suggestion" readonly></textarea>
        </div>
      </div>
      <div class="right-panel">
        <hexagon-chart :data="userAbilities" :labels="userLabels"></hexagon-chart>
        <table class="ability-table">
          <thead>
            <tr>
              <th>学情评估指标</th>
              <th>学情指标评分</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(label, index) in userLabels" :key="index" :style="{ color: colors[index][0] }">
              <td>{{ label }}</td>
              <td>{{ userAbilities[index] }}</td>
            </tr>
          </tbody>
        </table>
        <div class="button-container">
          <button @click="downloadCustomPaper"><i class="fas fa-save"></i> 下载个性化试题</button>
          <button @click="goOnlineTest"><i class="fas fa-save"></i> 在线个性化练习</button>
        </div>
      </div>
    </div>
  </div>
  <!-- 加载中弹窗 -->
  <div v-if="saving" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-spinner fa-spin"></i> 在线密卷下载中...</h2>
    </div>
  </div>
  <!-- 加载中弹窗 -->
  <div v-if="loading" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-spinner fa-spin"></i> 星火大模型生成在线密卷中...</h2>
    </div>
  </div>
</template>

<script>
import HexagonChart from '../../component/HexagonChart.vue';
import axios from 'axios';
import { openDB } from 'idb';

export default {
  components: {
    HexagonChart,
  },
  data() {
    return {
      userAbilities: [50,50,50,50,50,50],
      userLabels: ['分析','使用','思维','理论','计算','综合'],
      evaluation: '',
      shortcoming: '',
      suggestion: '',
      saving:false,
      loading:false,
      colors: [
        ['#FF5733', '#FF5733'],
        ['#e23c09', '#e23c09'],
        ['#C70039', '#900C3F'],
        ['#581845', '#900C3F'],
        ['#1F618D', '#2874A6'],
        ['#1ABC9C', '#16A085'],
      ],
    };
  },
  methods: {
    setTitleStarPositions() {
      const positions = [
        { top: '10px', left: '380px' },  
        { top: '0px', left: '560px' }, 
        { top: '12px', left: '750px' }, 
        { top: '10px', left: '1100px' },
        { top: '0px', left: '1250px' },
        { top: '12px', left: '1410px' },
      ];

      for (let i = 1; i <= 6; i++) {
        const starElement = this.$refs[`starTitle${i}`][0];
        const position = positions[i - 1] || { top: '0px', left: '50%' };
        starElement.style.top = position.top;
        starElement.style.left = position.left;
        starElement.style.transform = `translate(-50%, ${position.top})`;
      }
    },
    
    goBack() {
      this.$router.push('/index');
    },
    async downloadCustomPaper() {
      try {
        this.saving = true;
        const response = await axios.post('/get_download_custompaper', {
          evaluation: this.evaluation,
          shortcoming: this.shortcoming,
          suggestion: this.suggestion,
        }, {
          responseType: 'blob'  // 重要：指定响应类型为 blob
        });

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'problems.txt');  // 指定下载文件名
        document.body.appendChild(link);
        link.click();

        // 清理
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);
        this.saving = false;
      } catch (error) {
        this.saving= false;
        alert("")
        console.error('下载失败:', error);
      }
    },
    async goOnlineTest() {
      this.loading = true;
      try {
        const response = await axios.post('/get_custom_onlinepaper', {
            evaluation: this.evaluation,
            shortcoming: this.shortcoming,
            suggestion: this.suggestion,
          }).then((response) => {
            return response;
          });
        const data = response.data;
        await this.storeProblems(data.problems);
      } catch (error) {
        console.error('Error starting test:', error);
      } finally {
        this.loading = false;
        this.$router.push('/testpage');
      }
    },
    async storeProblems(problems) {
      const db = await openDB('problemsDB', 1, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('single_choice_problems')) {
            db.createObjectStore('single_choice_problems', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('judgement_problems')) {
            db.createObjectStore('judgement_problems', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('fillin_problems')) {
            db.createObjectStore('fillin_problems', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('evaluation')) {
            console.log("create evaluation")
            db.createObjectStore('evaluation', { keyPath: 'id', autoIncrement: true });
          }
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
          if (!db.objectStoreNames.contains('subjects')) {
            db.createObjectStore('subjects', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('knowledge_points')) {
            db.createObjectStore('knowledge_points', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
        },
      });
      // 开始新的事务，先清空所有存储的数据
      const tx = db.transaction(['single_choice_problems', 'judgement_problems', 'fillin_problems','subjects','knowledge_points'], 'readwrite');
      await Promise.all([
        tx.objectStore('single_choice_problems').clear(),
        tx.objectStore('judgement_problems').clear(),
        tx.objectStore('fillin_problems').clear(),
        tx.objectStore('subjects').clear(),
        tx.objectStore('knowledge_points').clear(),
      ]);
      await tx.done;

      // 重新创建数据库，确保ID从1开始
      const txNew = db.transaction(['single_choice_problems', 'judgement_problems', 'fillin_problems'], 'readwrite');
      let singleChoiceId = 1;
      let judgementId = 1;
      let fillinId = 1;

      problems.forEach((problem) => {
        const problemWithDoneanswer = { ...problem, doneanswer: '' };
        if (problem.type === 'single_choice') {
          txNew.objectStore('single_choice_problems').put({ ...problemWithDoneanswer, id: singleChoiceId++ });
        } else if (problem.type === 'judgement') {
          txNew.objectStore('judgement_problems').put({ ...problemWithDoneanswer, id: judgementId++ });
        } else if (problem.type === 'fillin') {
          txNew.objectStore('fillin_problems').put({ ...problemWithDoneanswer, id: fillinId++ });
        }
      });
      await txNew.done;
      const txSubjects = db.transaction(['subjects', 'knowledge_points'], 'readwrite');
      let selectedsubject = ["综合"]
      selectedsubject.forEach((subject) => {
        txSubjects.objectStore('subjects').put({ name: subject });
      });
      let selectedSubjects = ["综合"]
      selectedSubjects.forEach((knowledge) => {
        txSubjects.objectStore('knowledge_points').put({ name: knowledge });
      });
      await txSubjects.done;
    },
  },
  async mounted() {
    this.setTitleStarPositions();
    // 从 query 参数中获取数据
    const query = this.$route.query;
    this.evaluation = query.evaluation;
    this.shortcoming = query.shortcoming;
    this.suggestion = query.suggestion;
    this.userAbilities = JSON.parse(query.userAbilities || '[]');
    this.userLabels = JSON.parse(query.userLabels || '[]');
    console.log(this.evaluation,this.shortcoming,this.suggestion,this.userAbilities,this.userLabels)
  },
};
</script>

<style lang="scss">
header button {
  background-color: #007bff;
  color: #fff;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

header button i {
  margin-right: 8px;
}

header button:hover {
  background-color: #0056b3;
}

header .stars {
  position: absolute;
  top: 0px;
  left: 35%;
  transform: translateX(-50%);
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  overflow: visible;

  .star {
    position: absolute;
    width: 20px;
    height: 20px;
    filter: blur(4px);
    animation: sparkle 1s infinite ease-in-out, colorChange 7s infinite;
    clip-path: polygon(
      50% 0%,
      61% 35%,
      98% 35%,
      68% 57%,
      79% 91%,
      50% 70%,
      21% 91%,
      32% 57%,
      2% 35%,
      39% 35%
    ); 
  }
  @keyframes colorChange {
    0% { background: red; }
    16.66% { background: orange; }
    33.33% { background: yellow; }
    50% { background: green; }
    66.66% { background: rgb(1, 235, 235); }
    83.33% { background: blue; }
    100% { background: purple; }
  }
}

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
.evaluation-page {
  padding: 20px;

  header {
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;

    h1 {
      margin: 0;
      flex: 1;
      text-align: center;
      color: #0474de;
    }

    button {
      padding: 5px 10px;
      cursor: pointer;
      position: absolute;
      right: 0;
    }
  }

  .content {
    display: flex;
    margin-top: 0px;
    min-height: 500px;
    border-width: 3px !important;
    border-style: solid;
    animation: border-rotation 5s linear infinite;

    .left-panel {
      margin-left: 20px;
      border: none !important; /* 确保移除边框 */
      padding: 5px;
      width: 50%;
      min-height: 500px;
      margin-top: 0px;

      .evaluation-section {
        color: #067cfa;
        margin-bottom: 20px;

        h2 {
          margin-bottom: 5px;
          font-size: 2.0em;
          background:#03bad2;
          // background: linear-gradient(to right, #03bad2, #0056b3, #000d8b);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          // animation: gradient-animation 3s infinite;
          background-size: 300% 300%;
        }

        textarea {
          width: 100%;
          height: 100px;
          resize: none;
          border: 2px solid #06b8ef !important;
          padding: 10px;
          font-size: 1.5em;
          box-sizing: border-box;
          color: #00008a;
          font-weight: bolder;
        }
        @keyframes gradient-animation {
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
      }
    }
  }

  .right-panel {
    margin-top: -30px;
    width: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5px; 

    hexagon-chart {
      max-width: 80px !important; 
      max-height: 80px !important; 
    }

    .ability-table {
        width: 80%;
        height: 40%;
        margin-top: -15px;
        border-collapse: collapse;

        th,
        td {
          padding: 5px;
          text-align: center;
          border: 2px solid #06b8ef;
        }

        th {
          background-color: #007bff;
          color: white;
        }

        td {
          font-size: 0.08em;
          // color: #0360ff;
          font-weight: bold;
        }
      }

    .button-container {
      margin-top: 20px;
      display: flex;
      justify-content: center;

      button {
        margin: 0 10px;
        padding: 10px 20px;
        cursor: pointer;
        background-color: #3778e0;
        color: white;
        border: none;
        border-radius: 5px;
        transition: background-color 0.3s;

        &:hover {
          background-color: #584eec;
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

@keyframes gradientText {
  0% {
    color: #00c6ff; /* 起始颜色 */
  }
  50% {
    color: #0072ff; /* 中间颜色 */
  }
  100% {
    color: #00c6ff; /* 结束颜色 */
  }
}

.loading-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5); /* 保持不变的背景色 */
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-content {
  background: white; /* 保持不变的背景色 */
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-size: 16px;
  font-weight: bold;
  animation: gradientText 2s linear infinite; /* 添加字体渐变色动画 */
}

.loading-spinner {
  margin-top: 10px;
  text-align: center;
}
</style>

