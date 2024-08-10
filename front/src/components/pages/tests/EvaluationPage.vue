<template>
  <div class="evaluation-page">
    <header>
      <h1><i class="fas fa-star"></i>测试评估 </h1>
      <div class="stars">
        <div v-for="n in 6" :key="n" class="star" :ref="'starTitle' + n"></div>
      </div>
      <button @click="goBack"><i class="fas fa-arrow-left"></i> 返回</button>
    </header>
    <div class="content">
      <div class="left-panel">
        <div class="evaluation-section">
          <h2>评价</h2>
          <textarea v-model="evaluationContent" readonly></textarea>
        </div>
        <div class="evaluation-section">
          <h2>不足</h2>
          <textarea v-model="shortcomingContent" readonly></textarea>
        </div>
        <div class="evaluation-section">
          <h2>建议</h2>
          <textarea v-model="suggestionContent" readonly></textarea>
        </div>
      </div>
      <div class="right-panel">
        <hexagon-chart :data="userAbilities" :labels="userLabels"></hexagon-chart>
        <div class="button-container">
          <button @click="viewQuestions"><i class="fas fa-save"></i> 查看答案</button>
          <button @click="saveResults"><i class="fas fa-save"></i> 保存结果</button>
        </div>
      </div>
    </div>
  </div>
  <!-- 加载中弹窗 -->
  <div v-if="saving" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-spinner fa-spin"></i> 测试结果保存中...</h2>
    </div>
  </div>
</template>

<script>
import { openDB } from 'idb';
import HexagonChart from '../../component/HexagonChart.vue';
import axios from 'axios';

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
      saving:false,
    };
  },
  methods: {
    setTitleStarPositions() {
      const positions = [
        { top: '10px', left: '380px' },  
        { top: '0px', left: '560px' }, 
        { top: '20px', left: '750px' }, 
        { top: '10px', left: '1100px' },
        { top: '0px', left: '1250px' },
        { top: '15px', left: '1410px' },
      ];

      for (let i = 1; i <= 6; i++) {
        const starElement = this.$refs[`starTitle${i}`][0];
        const position = positions[i - 1] || { top: '0px', left: '50%' };
        starElement.style.top = position.top;
        starElement.style.left = position.left;
        starElement.style.transform = `translate(-50%, ${position.top})`;
      }
    },
    async loadDataFromIndexedDB() {
      try {
        const db = await openDB('problemsDB', 1);
        const evaluation = await db.get('evaluation', 1);
        const shortcoming = await db.get('shortcoming', 1);
        const suggestion = await db.get('suggestion', 1);
        let dimensions = await db.getAll('dimension');
        let scores = await db.getAll('score');
        dimensions = dimensions.length > 6 ? dimensions.slice(0, 6) : dimensions;
        scores = scores.length > 6 ? scores.slice(0, 6) : scores;
        if (dimensions.length < 6 && scores.length < 6) {
            for (let i = 0; i < dimensions.length; i++) {
                this.userLabels[i] = dimensions[i].dimension;
            }
            for (let i = 0; i < scores.length; i++) {
                this.userAbilities[i] = scores[i].score < 10 ? 10 : scores[i].score;
            }
        }else{
          this.userLabels = dimensions.map(dim => dim.dimension);     
          this.userAbilities = scores.map(score => {
            return score.score < 10 ? 10 : score.score;
          });
        }
        
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
      this.$router.push('/testanswer');
      console.log('查看题目');
    },
    async saveResults() {
      this.saving = true;
      try {
        const problemsDB = await openDB('problemsDB', 1);
        const db = await openDB('UserDatabase', 1);
        const tx = db.transaction('users', 'readonly');
        const store = tx.objectStore('users');
        // Get all stored entries (assuming there's only one due to the clear operation)
        const allUsers = await store.getAll();
        await tx.done;
        // Check if we have at least one user
        const { userId } = allUsers[0]; // Get the first user's userId
        console.log('Retrieved userId:', userId);

        const singleChoiceProblems = await problemsDB.getAll('single_choice_problems');
        const fillinProblems = await problemsDB.getAll('fillin_problems');
        const judgementProblems = await problemsDB.getAll('judgement_problems');

        const evaluation = await problemsDB.get('evaluation', 1);
        const scores = await problemsDB.getAll('score');

        const subjects = await problemsDB.getAll('subjects');
        const knowledgePoints = await problemsDB.getAll('knowledge_points');

        const testName = subjects.map(subject => subject.name).join(', ');
        const testSubjects = knowledgePoints.map(point => point.name).join(', ');

        const problems = [
          ...singleChoiceProblems.map(p => ({
            type: 'single_choice',
            problem: p.problem,
            choices: p.choices,
            answer: p.answer,
            analysis: p.analysis,
          })),
          ...fillinProblems.map(p => ({
            type: 'fillin',
            problem: p.problem,
            answer: p.answer,
            analysis: p.analysis,
          })),
          ...judgementProblems.map(p => ({
            type: 'judgement',
            problem: p.problem,
            answer: p.answer,
            analysis: p.analysis,
          })),
        ];

        const answers = [
          ...singleChoiceProblems.map(p => p.doneanswer),
          ...fillinProblems.map(p => p.doneanswer),
          ...judgementProblems.map(p => p.doneanswer),
        ];

        const testScore = scores.reduce((acc, score) => acc + score.score, 0) / scores.length;

        const payload = {
          user_id: userId,
          test_name: testName,
          test_subjects: testSubjects,
          problems,
          answers,
          evaluation: evaluation.content,
          test_score: testScore,
        };
        console.log('payload:',payload)
        const response = await axios.post('/save_test', payload).then((res) => {
          return res
        });

        const data = response.data;
        this.saving = false;
        if (data.status === 'success') {
          alert('测试结果保存成功!')
          console.log('测试结果保存成功:', data.test_id);
        } else {
          alert('网络不畅，请重新保存')
          console.error('测试结果保存失败');
        }
      } catch (error) {
        console.error('保存结果失败:', error);
      }
    },
  },
  async mounted() {
    this.setTitleStarPositions();
    await this.loadDataFromIndexedDB();
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
        top: 0px; /* 调整星星的位置 */
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
          ); /* 五角星形状 */
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

    // .right-panel {
    //   width: 50%;
    //   display: flex;
    //   flex-direction: column;
    //   align-items: center;
    //   justify-content: center;

    //   .button-container {
    //     margin-top: 20px;
    //     display: flex;
    //     justify-content: center;

    //     button {
    //       margin: 0 10px;
    //       padding: 10px 20px;
    //       cursor: pointer;
    //       background-color: #3778e0;
    //       color: white;
    //       border: none;
    //       border-radius: 5px;
    //       transition: background-color 0.3s;

    //       &:hover {
    //         background-color: #584eec;
    //       }
    //     }
    //   }
    // }
  }

  .right-panel {
    width: 70%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px; /* Add padding to ensure space around the hexagon chart */

    hexagon-chart {
      width: 50%; /* Ensure the chart takes full width */
      height: 50%; /* Ensure the chart takes full height */
      max-width: 500px; /* Set a maximum width for the chart */
      max-height: 500px; /* Set a maximum height for the chart */
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

}
</style>

