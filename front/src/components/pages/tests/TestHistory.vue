<template>
  <div class="self-test-history">
    <header class="header">
      <h1><i class="fas fa-book-open"></i> 自测历史</h1>
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
        </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';
import { openDB } from 'idb';
import HexagonChart from '../../component/HexagonChart.vue';

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
    background-color: #3498db;
    color: #fff;
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
    color: #2389d7; /* Blue color for the labels */
  }

  .section-content textarea {
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
    width: 48%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
}
</style>