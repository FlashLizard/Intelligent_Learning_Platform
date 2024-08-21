<template>
  <!-- 加载中弹窗 -->
  <div v-if="loading" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-spinner fa-spin"></i> 星火大模型生成在线密卷中...</h2>
    </div>
  </div>
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
  <div class="self-test-history">
    <header class="header">
      <h1><i class="fas fa-book-open"></i> 自测历史</h1>
      <button class="openguide-button" @click="guidevisible = true"> <i class="fas fa-exclamation-circle"></i> </button>
      <button class="back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i>
      </button>
    </header>
    <main class="main">
      <div class="scroll-panel">
        <!-- 表头 -->
        <div class="table-header">
          <span class="table-cell"><i class="fas fa-calendar-alt" style="margin-right: 8px;"></i>  测试时间</span>
          <span class="table-cell"><i class="fas fa-book" style="margin-right: 8px;"></i>  测试学科</span>
          <span class="table-cell"><i class="fas fa-lightbulb" style="margin-right: 8px;"></i>  测试知识点</span>
          <span class="table-cell"><i class="fas fa-star" style="margin-right: 8px;"></i>  测试评分</span>
          <span class="table-cell"></span> 
        </div>
        <!-- 表格内容 -->
        <div class="table-body">
          <div
            class="table-row"
            v-for="item in history"
            :key="item.id"
            @mouseenter="highlightItem(item.id)"
            @mouseleave="unhighlightItem()"
            @click="fetchTestDetail(item.id)"
          >
            <span class="table-cell">{{ formatDateTime(item.test_time) }}</span>
            <span class="table-cell">{{ item.test_name }}</span>
            <span class="table-cell">{{ removeQuotes(item.test_subjects) }}</span>
            <span class="table-cell">{{ item.test_score }}</span>
            <span class="table-cell">
              <h2 class="fas fa-times" @click.stop="deleteTest(item.id)"></h2>
            </span>
          </div>
        </div>
      </div>
      <!-- 评价、缺陷、建议 和 六边形图表布局 -->
      <div class="analysis-section">
        <div class="section-title"><i class="fas fa-chart-line"></i>  历史分析
          <i class="fas fa-search-plus expand-icon" @click="goToExpandedPage"> 更多</i></div>
        <!-- 加载动画 -->
        <div v-if="isLoading" class="loading-container">
          <i class="fas fa-spinner fa-spin"></i> 星火大模型加急分析您的测试历史中，请稍等......
        </div>
        <div v-else class = "section-content">
          <!-- 实际内容 -->
          <div class="analysis-text">
          <div>
            <label for="evaluation"><i class="fas fa-star"></i> 总体评价</label>
            <textarea id="evaluation" v-model="evaluation" readonly></textarea>
          </div>
          <div>
            <label for="shortcoming"><i class="fas fa-exclamation-triangle"></i> 总体缺陷</label>
            <textarea id="shortcoming" v-model="shortcoming" readonly></textarea>
          </div>
          <div>
            <label for="suggestion"><i class="fas fa-lightbulb"></i> 总体建议</label>
            <textarea id="suggestion" v-model="suggestion" readonly></textarea>
          </div>
        </div>
        <div class="hexagon-chart">
          <hexagon-chart :data="userAbilities" :labels="userLabels"></hexagon-chart>
          <div class="extra-buttons">
            <button class="extra-button" @click="goOnlineTest">
              <i class="fas fa-laptop-code"></i> 在线加练
            </button>
            <button class="extra-button" @click="downloadCustomPaper">
              <i class="fas fa-download"></i> 下载密卷
            </button>
          </div>
        </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';
import { openDB } from 'idb';
import HexagonChart from '../../component/HistoryHexagonChart.vue';

export default {
  components: {
    HexagonChart,
  },
  data() {
    return {
      history: [],
      highlightedItemId: null,
      evaluation: '',
      shortcoming: '',
      suggestion: '',
      userAbilities: [50,50,50,50,50,50],
      userLabels: ['分析','使用','思维','理论','计算','综合'],
      isLoading: true,
      loading:false,//是否生成试卷中
      guidetext: "1. 用户可以在页面上看见自己的测试记录，包括测试时间、测试学科、测试知识点和测试评分\n\n2. 用户可以在“历史分析”一栏看到AI对自己过去一段时间做题结果的评价和建议\n\n3. 用户点击相应测试条目，即可看到原卷、自己的答案和标准答案。",
      guidevisible:false,
    };
  },
  async mounted() {
    this.$nextTick(() => {
      // 在组件渲染完成后进行 DOM 操作
      const hexagonChartElement = this.$refs.hexagonChart;
      if (hexagonChartElement) {
        console.log('HexagonChart component:', hexagonChartElement);
      } else {
        console.error('HexagonChart component not found');
      }
    });
    try {
      // Open UserDatabase and get the userId
      const db = await openDB('UserDatabase', 1);
      const tx = db.transaction('users', 'readonly');
      const store = tx.objectStore('users');
      const allUsers = await store.getAll();
      await tx.done;
      if (allUsers.length > 0) {
        const userId = allUsers[0].userId;
        const username = allUsers[0].username;
        console.log("allUsers:",allUsers)
        console.log('Retrieved userId:', userId);
        console.log('Retrieved username:', username);
        this.fetchUserTestsAnalysis(username); //加载用户个性化分析
        const response = await axios.post('/get_user_tests', 
          {user_name: username}
        ).then((response) => {
          return response;
        });

        const data = response.data;
        if (data.status === 'success') {
          this.history = data.tests;
          console.log('this.history:', this.history);
        } else {
          console.error('Failed to fetch user tests');
        }
      } else {
        console.error('No user found in UserDatabase');
      }
    } catch (error) {
      console.error('Error retrieving user tests:', error);
    }
  },
  methods: {
    async downloadCustomPaper() {
      try {
        this.loading = true;
        const response = await axios.post('/get_historyevaluation_download_custompaper', {
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
        this.loading = false;
      } catch (error) {
        this.loading= false;
        alert("网络不畅，请重试")
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
        this.loading = false;
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
    goToExpandedPage() {
      this.$router.push({
        path: '/historyevaluationpage',
        query: {
          evaluation: this.evaluation,
          shortcoming: this.shortcoming,
          suggestion: this.suggestion,
          userAbilities: JSON.stringify(this.userAbilities),
          userLabels: JSON.stringify(this.userLabels),
        }
      });
    },
    async fetchUserTestsAnalysis(username) {
      try {
        const response = await axios.post('/get_user_tests_analysis', {
          user_name: username
        });

        if (response.data.status === 'success') {
          const analysis = JSON.parse(response.data.tests_analysis.replace(/`/g, '"').replace(/^"""\w*/, '').replace(/"""$/, '').trim());
          this.evaluation = analysis.evaluation;
          this.shortcoming = analysis.shortcoming;
          this.suggestion = analysis.suggestion;
          this.userAbilities = analysis.knowledge_radar.score;
          this.userLabels = analysis.knowledge_radar.dimension;
          console.log('this.evaluation:',this.evaluation)
          console.log('this.shortcoming:',this.shortcoming)
          console.log('this.suggestion:',this.suggestion)
          console.log('analysis.knowledge_radar.dimension:',analysis.knowledge_radar.dimension)
          console.log('analysis.knowledge_radar.score:',analysis.knowledge_radar.score)

        } else {
          console.error('Failed to fetch tests analysis:', response.data);
        }
      } catch (error) {
        console.error('Error fetching tests analysis:', error);
      } finally {
        this.isLoading = false; // 数据加载完成后隐藏加载动画
      }
    },
    goBack() {
      this.$router.back();
    },
    highlightItem(id) {
      this.highlightedItemId = id;
    },
    unhighlightItem() {
      this.highlightedItemId = null;
    },
    async fetchTestDetail(testId) {
      try {
        const response = await axios.post('/get_test', { test_id: testId }).then((response) => {
          return response;
        });

        const data = response.data;
        console.log('Received response:', data);

        if (data['status'] === 'success') {
          this.test = {
            id: data.id,
            user_name: data.user_name,
            test_name: data.test_name,
            test_time: data.test_time,
            test_questions: data.test_questions,
            test_score: data.test_score,
            test_subjects: data.test_subjects,
            user_answers: data.user_answers,
            test_result_analysis: data.test_result_analysis,
          };

          // Open (or create) the IndexedDB
          const db = await openDB('HistoryTestDB', 1, {
            upgrade(db) {
              if (!db.objectStoreNames.contains('tests')) {
                db.createObjectStore('tests', { keyPath: 'id', autoIncrement: true });
              }
            },
          });

          const tx = db.transaction('tests', 'readwrite');
          const store = tx.objectStore('tests');
          await store.clear();
          await store.add(this.test);
          await tx.done;

          console.log('Test details saved to IndexedDB:', this.test);
          this.$router.push('/historytestans');
        } else {
          console.error('Failed to fetch test data:', data.msg);
        }
      } catch (error) {
        console.error('Error fetching test details:', error);
      }
    },
    async deleteTest(testId) {
      try {
        const response = await axios.post('/delete_test', { test_id: testId });
        const data = response.data;

        if (data.status === 'success') {
          this.history = this.history.filter(item => item.id !== testId);
          console.log('Test deleted successfully:', testId);
        } else {
          console.error('Failed to delete test');
        }
      } catch (error) {
        console.error('Error deleting test:', error);
      }
    },
    removeQuotes(str) {
      return str.replace(/"/g, '');
    },
    formatDateTime(dateTimeStr) {
      return dateTimeStr.replace(' GMT', '');
    },
  },
};
</script>

<style lang="scss">
.self-test-history {
  font-family: Arial, sans-serif;
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    // background-color: #3498db;
    color: #fff;
    background-image: url('../../../assets/PPTbackground.jpg'); /* 背景图片的路径 */
    background-size: cover; /* 让背景图片充满容器 */
    background-position: center; /* 居中显示背景图片 */
    background-repeat: no-repeat; /* 禁止背景图片重复 */

    .openguide-button {
        text-align: center;
        justify-self: center;
        padding: 0.5rem;
        display: inline-block; 
        vertical-align: middle;
        background-color: transparent;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        position: absolute; 
        font-weight: bold;
        font-size: 1.5em;
        top:29px;
        right:100px;
      }
      .openguide-button:hover {
        color: #acfafa;
      }

    h1 {
      font-size: 28px;
      margin-left: 48%;
      margin-top: 5px;
      margin-bottom: 5px;
    }
    .back-button {
      background: none;
      border: none;
      cursor: pointer;
      color: #fff;
      font-size: 24px;
    }
    .back-button:hover {
      color:#99e7f5
    }
  }
  .main {
    padding: 20px;
  }
  .scroll-panel {
    max-height: 250px;
    overflow-y: scroll;
    border: 1px solid #ddd;
    border-radius: 5px;

    .table-container {
      display: grid;
      grid-template-rows: auto 1fr;
    }

    .table-header {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      background-color: #3498db;
      color: #fff;
      font-weight: bold;
      padding: 10px;
      font-size: 1.0em;
    }

    .table-body {
      max-height: 200px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
    }

    .table-row {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      padding: 2px;
      cursor: pointer;
      transition: background-color 0.3s ease;
      &:hover {
        background-color: #f0f0f0;
      }
      &:not(:last-child) {
        border-bottom: 1px solid #ccc;
      }
    }

    .table-cell {
      display: flex;
      align-items: center;
      justify-content: center;
      white-space: nowrap; 

      h2 {
        color:#66b0f9
      }
      h2:hover {
        color:rgb(137, 184, 247)
      }
    }
  }
  .analysis-section {
    height:330px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: fixed; /* 将组件固定在窗口底部 */
    bottom: 20px;
    left: 40px; /* 确保组件从左侧开始 */
    right: 40px; /* 确保组件延伸到右侧 */
    margin: 0 auto; /* 居中组件，如果宽度小于100% */
    border-radius: 5px !important;
    border-width: 3px !important;
    border-style: solid;
    animation: border-rotation 5s linear infinite;

    .section-title {
      position: relative;
      top: 0px;
      width:100%;
      text-align: center;
      height: 30px;
      font-size: 20px;
      font-weight: bold;
      color: #fefefe;
      background-color: #2389d7;
      white-space: nowrap;
      margin-bottom: 5px;
    }
    .expand-icon {
      position: absolute;
      right: 15px; 
      top: 50%; 
      transform: translateY(-50%); 
      font-size: 20px; 
      cursor: pointer;
    }
    .expand-icon:hover {
      color:#b3d8f5
    }

    .section-content {
      display: flex;
      justify-content: space-between;
      width: 100%;
      height: 100%;
      margin-top: -5px;
      flex-direction: row;
    }

    .loading-container {
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      height: 100%;
      font-size: 24px;
      color: #2389d7;
      i {
        font-size: 24px;
        margin-right: 10px;
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

  .section-content .analysis-text {
    display: flex;
    flex-direction: column;
    width: 50%;
    margin-top: 5px !important;
    margin-left: 10px !important;
  }

  .section-content .analysis-text div {
    margin-bottom: 5px;
  }

  .section-content .analysis-text label {
    font-size:1em;
    font-weight:bold;
    color: #2389d7; /* Blue color for the labels */
  }

  .section-content textarea {
    font-size: 1.2em;
    width: 100%;
    height: 55px;
    resize: none;
    border: 2px solid #2389d7; 
    color: #2389d7; /* Blue text color */
    background-color: #f7f9fc; /* Light background color for better readability */
    
    ::placeholder {
      color: #a1c4fd; /* Optional: light blue placeholder text color */
    }
  }

  .section-content .hexagon-chart {
    width: 46%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top:-5px;

    .extra-buttons {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      align-items: center;
      margin-left: 40px; /* 可以根据需要调整间距 */
      margin-top: 40px;
      margin-bottom: 40px;
    }

    .extra-button {
      width: 150px;
      padding: 10px;
      margin-bottom: 10px;
      background-color: #2389d7;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-size: 16px;
      font-weight: bold;
      text-align: center;
      transition: background-color 0.3s;
    }

    .extra-button i {
      margin-right: 8px;
    }

    .extra-button:hover {
      background-color: #1b6fb3;
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
  z-index: 9999;
}

.loading-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 9999;
}

// .loading-spinner {
//   margin-top: 10px;
//   text-align: center;
// }
</style>