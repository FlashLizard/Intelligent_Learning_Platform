<template>
    <div class="evaluation-page">
      <header>
        <h1><i class="fas fa-star"></i> 测试评估</h1>
        <button @click="goBack"><i class="fas fa-arrow-left"></i>  返回</button>
      </header>
      <div class="content">
        <div class="left-panel">
          <div class="evaluation-section">
            <h2><i class="fas fa-star"></i> 评价</h2>
            <textarea v-model="evaluationContent" readonly></textarea>
          </div>
          <div class="evaluation-section">
            <h2><i class="fas fa-exclamation-triangle"></i> 不足</h2>
            <textarea v-model="shortcomingContent" readonly></textarea>
          </div>
          <div class="evaluation-section">
            <h2><i class="fas fa-lightbulb"></i> 建议</h2>
            <textarea v-model="suggestionContent" readonly></textarea>
          </div>
        </div>
        <div class="right-panel">
          <hexagon-chart :data="userAbilities" :labels="userLabels"></hexagon-chart>
          <div class="button-container">
          </div>
          <div class="button-container">
            <button @click="viewQuestions"><i class="fas fa-save"></i> 查看答案</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { openDB } from 'idb';
  import HexagonChart from '../../component/HexagonChart.vue';
  
  export default {
    components: {
      HexagonChart,
    },
    data() {
      return {
        userAbilities: [50,50,50,50,50,50],
        userLabels: ['分析','使用','思维','理论','计算','综合'],
        evaluationContent: '',
        shortcomingContent: '',
        suggestionContent: '',
      };
    },
    methods: {
      async loadDataFromIndexedDB() {
        try {
          const db = await openDB('ClassTestProblems', 1);
          const evaluation = await db.get('evaluation', 1);
          const shortcoming = await db.get('shortcoming', 1);
          const suggestion = await db.get('suggestion', 1);
          const dimensions = await db.getAll('dimension');
          const scores = await db.getAll('score');
          
          this.userLabels = dimensions.map(dim => dim.dimension);
          // this.userAbilities = scores.map(score => score.score);        
          this.userAbilities = scores.map(score => {
            return score.score < 10 ? 10 : score.score;
          });       
          if (evaluation) this.evaluationContent = evaluation.content;
          if (shortcoming) this.shortcomingContent = shortcoming.content;
          if (suggestion) this.suggestionContent = suggestion.content;
        } catch (error) {
          console.error('Failed to load data from IndexedDB:', error);
        }
      },
      goBack() {
        this.$router.push('/index');
      },
      viewQuestions() {
        this.$router.push('/classtestanswer');
        console.log('查看题目');
      },
    },
    async mounted() {
      await this.loadDataFromIndexedDB();
      // 假设这里还需要加载用户能力数据到 userAbilities 和 userLabels
    },
  };
  </script>
  
  <style lang="scss">
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
      margin-top: 20px;
      height: 100%;
  
      .left-panel {
        border: 1px solid black;
        padding: 10px;
        width: 50%;
        margin-top: 40px;
        height: 90%;
  
        .evaluation-section {
          margin-bottom: 20px;
  
          h2 {
            margin-bottom: 5px;
            font-size: 2.0m; /* 增加标题字体大小 */
          }
  
          textarea {
            width: 100%;
            height: 80px; /* 调整高度 */
            resize: none; /* 禁止文本框大小调整 */
            border: 1px solid #ccc;
            padding: 10px;
            font-size: 1.5em; /* 增加字体大小 */
            box-sizing: border-box; /* 包括内边距和边框在内的宽度和高度计算 */
          }
        }
      }
  
      .right-panel {
        width: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
  
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
    }
  }
  </style>
  
  