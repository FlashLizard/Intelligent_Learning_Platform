<template>
  <div class="guide-modal" v-if="guidevisible">
    <div class="guide-modal-content">
      <button class="guide-close-button" @click="guidevisible=false">
        <i class="fas fa-times"></i>
      </button>
      <h3> <i class="fas fa-exclamation-circle"></i> 测试保存成功</h3>
    </div>
  </div>
  <div class="evaluation-page">
    <header>
      <h1><i class="fas fa-star"></i> 测试评估 </h1>
      <div class="stars">
        <div v-for="n in 6" :key="n" class="star" :ref="'starTitle' + n"></div>
      </div>
      <button @click="goBack"><i class="fas fa-arrow-left"></i> 返回</button>
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
        <table class="ability-table">
          <thead>
            <tr>
              <th>智能评卷指标</th>
              <th>智教评分</th>
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
      guidevisible: false,
      userAbilities: [50,50,50,50,50,50],
      userLabels: ['分析','使用','思维','理论','计算','综合'],
      evaluationContent: '',
      shortcomingContent: '',
      suggestionContent: '',
      saving:false,
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
        const userId = allUsers[0].userId;
        const username = allUsers[0].username;
        console.log('Retrieved userId:', userId);
        console.log('Retrieved username:', username);

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
          // user_id: userId,
          user_name: username,
          test_name: testName === "" ? "综合" : testName,
          test_subjects: testSubjects === "" ? "综合" : testSubjects,
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
          this.saving = false;
          this.guidevisible = true;
          // alert('本次测试保存成功')
          console.log('测试结果保存成功:', data.test_id);
        } else {
          this.saving = false;
          alert('网络不畅，请重新保存')
          console.error('测试结果保存失败');
        }
      } catch (error) {
        this.saving = false;
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
    margin-bottom: 20px;

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
  width: 10%;
  max-width: 300px !important;
  height: 20% !important;
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
  font-size: 1.7em !important;
  font-weight: bold !important;
  margin-top: 60px !important;
  justify-content: center !important;
  text-align: center;
  color:#007bff;
}
</style>

