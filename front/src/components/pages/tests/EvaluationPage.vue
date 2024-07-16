<template>
  <div class="evaluation-page">
    <header>
      <h1>测试评估</h1>
      <button @click="goBack">返回</button>
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
          <button @click="viewQuestions">查看题目</button>
          <button @click="saveResults">保存结果</button>
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
      userAbilities: [],
      userLabels: [],
      evaluationContent: '',
      shortcomingContent: '',
      suggestionContent: '',
    };
  },
  methods: {
    async loadDataFromIndexedDB() {
      try {
        const db = await openDB('problemsDB', 1);
        const evaluation = await db.get('evaluation', 1);
        const shortcoming = await db.get('shortcoming', 1);
        const suggestion = await db.get('suggestion', 1);
        const dimensions = await db.getAll('dimension');
        const scores = await db.getAll('score');
        
        this.userLabels = dimensions.map(dim => dim.dimension);
        this.userAbilities = scores.map(score => score.score);        
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
    const response = await fetch('http://localhost:5000/save_test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (data.status === 'success') {
      console.log('测试结果保存成功:', data.test_id);
    } else {
      console.error('测试结果保存失败');
    }
  } catch (error) {
    console.error('保存结果失败:', error);
  }
},
  },
  async mounted() {
    await this.loadDataFromIndexedDB();
  },
};
</script>

<style lang="scss">
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

