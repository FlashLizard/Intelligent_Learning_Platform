<template>
  <div class="test-page">
    <header>
      <span class="title"><i class="fas fa-pencil-alt"></i> 测试
        <div class="stars">
          <div v-for="n in 6" :key="n" class="star" :ref="'starTitle' + n"></div>
        </div>
      </span>
      <!-- 星星装饰 -->
      <button class="return-button" @click="returnToPreviousPage">
        <i class="fas fa-arrow-left"></i> 返回
      </button>
    </header>
    <main>
      <aside class="sidebar">
        <div class="timer-container">
          <div class="time">
            <i class="fas fa-clock"></i> 考试时间：{{ formattedMinutes }}:{{ formattedSeconds }}
          </div>
          <button @click="submitTest" class="submit-button">
            <i class="fas fa-paper-plane"></i> 交卷
          </button>
        </div>
        <div class="section" v-for="section in sections" :key="section.name">
          <div class="section-title">
            <i class="fas fa-book"></i> {{ section.name }}
          </div>
          <div class="question-status-container">
            <div
              class="question-status"
              v-for="question in section.questions"
              :key="question.id"
              :class="{ 'done': isQuestionDone(section.name, question.id), 'not-done': !isQuestionDone(section.name, question.id) }"
              @click="jumpToQuestion(section.name, question.id)"
            >
              {{ question.id }}
            </div>
          </div>
        </div>
      </aside>
      <div class="content">
        <h2>
          <i class="fas fa-question-circle"></i>
          {{ currentSection ? currentSection.name : '' }}题 第{{ currentQuestionIndex + 1 }}题
        </h2>
        <div v-if="currentQuestion" :key="currentQuestion.id">
          <div v-if="currentSection && currentSection.name === '选择'" class="choice-question">
            <div class="question-content">
              {{ currentQuestionIndex + 1 }}. {{ currentQuestionContent }}
            </div>
            <div class="options">
              <div v-for="(option, index) in currentQuestion.choices" :key="index" class="option" @click="selectOption(index)">
                <span> {{" "}} {{ letterlist[index] }}. {{ option }} </span>
                <span class="circle" :class="{ selected: this.selectedOption === index }"></span>
              </div>
            </div>
          </div>
          <div v-if="currentSection && currentSection.name === '填空'" class="fill-blank-question">
            <div class="question-content">
              {{ currentQuestionIndex + 1 }}. {{ currentQuestionContent }}
            </div>
            <input type="text" class="input-box" placeholder="请输入答案" v-model="filledAnswer" />
          </div>
          <div v-if="currentSection && currentSection.name === '判断'" class="judge-question">
            <div class="question-content">
              {{ currentQuestionIndex + 1 }}. {{ currentQuestionContent }}
            </div>
            <div class="options">
              <div class="option" @click="selectOption(true)">
                <span>A. 正确</span>
                <span class="circle" :class="{ selected: selectedOption === true }"></span>
              </div>
              <div class="option" @click="selectOption(false)">
                <span>B. 错误</span>
                <span class="circle" :class="{ selected: selectedOption === false }"></span>
              </div>
            </div>
          </div>
        </div>
        <div class="buttons">
          <div class="navigation-buttons">
            <button @click="previousQuestion">
              <i class="fas fa-arrow-left"></i> 上一题
            </button>
            <button @click="nextQuestion">
              下一题 <i class="fas fa-arrow-right"></i>
            </button>
          </div>
        </div>
      </div>
      <!-- 星光特效 -->
      <!-- <div class="star-effect-container">
        <div v-for="n in 16" :key="n" class="star" :ref="'star' + n"></div>
      </div> -->
    </main>
    <!-- AI正在阅卷中...弹窗 -->
    <div v-if="grading" class="grading-dialog">
      <div class="grading-content">
        <h2><i class="fas fa-robot"></i> AI正在阅卷中...</h2>
      </div>
    </div>
  </div>
</template>



<script>
import { openDB } from 'idb';
import axios from 'axios';

export default {
  data() {
    return {
      timer: null,
      minutes: 0,
      seconds: 0,
      sections: [
        { name: '选择', questions: [], done: [], answers: {} },
        { name: '填空', questions: [], done: [], answers: {} },
        { name: '判断', questions: [], done: [], answers: {} }
      ],
      currentSection: null,
      currentQuestionIndex: 0,
      selectedOption: null,
      filledAnswer: '',
      questionContents: {},
      grading: false, // 新增属性，控制“AI正在阅卷中...”弹窗显示
      letterlist : ['A','B','C','D'],
    };
  },
  computed: {
    formattedMinutes() {
      return this.minutes.toString().padStart(2, '0');
    },
    formattedSeconds() {
      return this.seconds.toString().padStart(2, '0');
    },
    currentQuestion() {
      if (this.currentSection && this.currentSection.questions) {
        return this.currentSection.questions[this.currentQuestionIndex];
      }
      return null;
    },
    currentQuestionContent() {
      if (this.currentQuestion) {
        return this.currentQuestion.problem;
      }
      return '';
    }
  },
  methods: {
    setTitleStarPositions() {
    const positions = [
      { top: '20px', left: '200px' },  
      { top: '35px', left: '400px' }, 
      { top: '10px', left: '600px' }, 
      { top: '30px', left: '1000px' },
      { top: '10px', left: '1200px' },
      { top: '35px', left: '1400px' },
    ];

    for (let i = 1; i <= 6; i++) {
      const starElement = this.$refs[`starTitle${i}`][0];
      const position = positions[i - 1] || { top: '0px', left: '50%' };
      starElement.style.top = position.top;
      starElement.style.left = position.left;
      starElement.style.transform = `translate(-50%, ${position.top})`;
    }
  },
    setStarPositions() {
      const positions = [
        { top: '0px', right: '0px' },       // 1
        { bottom: '0px', right: '0px' },    // 2
        { top: '0px', left: '0px' },        // 3
        { bottom: '0px', left: '0px' },     // 4
        { top: '220px', right: '0px' },     // 5
        { top: '450px', right: '0px' },     // 6
        { top: '220px', left: '0px' },      // 7
        { top: '450px', left: '0px' },      // 8
        { bottom: '0px', right: '300px' },  // 9
        { bottom: '0px', right: '600px' },  // 10
        { bottom: '0px', right: '900px' },  // 11
        { bottom: '0px', right: '1200px' }, // 12
        { top: '0px', right: '300px' },     // 13
        { top: '0px', right: '600px' },     // 14
        { top: '0px', right: '900px' },     // 15
        { top: '0px', right: '1200px' },    // 16
      ];

      // 先处理编号为奇数的星星
      for (let i = 1; i <= 16; i += 2) {
        const starElement = this.$refs[`star${i}`][0];
        const position = positions[i - 1]; // 奇数编号的星星对应的索引

        if (position.top !== undefined) {
          starElement.style.top = position.top;
        }
        if (position.bottom !== undefined) {
          starElement.style.bottom = position.bottom;
        }
        if (position.left !== undefined) {
          starElement.style.left = position.left;
        }
        if (position.right !== undefined) {
          starElement.style.right = position.right;
        }
      }

      // 再处理编号为偶数的星星
      for (let i = 2; i <= 16; i += 2) {
        const starElement = this.$refs[`star${i}`][0];
        const position = positions[i-1]; // 偶数编号的星星对应的索引（从第9个位置开始）

        if (position.top !== undefined) {
          starElement.style.top = position.top;
        }
        if (position.bottom !== undefined) {
          starElement.style.bottom = position.bottom;
        }
        if (position.left !== undefined) {
          starElement.style.left = position.left;
        }
        if (position.right !== undefined) {
          starElement.style.right = position.right;
        }
      }
    },
    async loadQuestions() {
      try {
        const db = await openDB('problemsDB', 1);
        await this.loadQuestionsByType(db, 'fillin_problems', '填空');
        await this.loadQuestionsByType(db, 'judgement_problems', '判断');
        await this.loadQuestionsByType(db, 'single_choice_problems', '选择');
        this.currentSection = this.sections[0];
      } catch (error) {
        console.error('Failed to load questions:', error);
      }
    },
    async loadQuestionsByType(db, tableName, type) {
      const questions = await db.getAll(tableName);
      const section = this.sections.find(sec => sec.name === type);
      if (section) {
        section.questions.push(...questions);
      }
    },
    startTimer() {
      this.timer = setInterval(() => {
        this.seconds++;
        if (this.seconds === 60) {
          this.minutes++;
          this.seconds = 0;
        }
      }, 1000);
    },
    returnToPreviousPage() {
      this.$router.back();
    },
    jumpToQuestion(sectionName, questionId) {
      if (this.currentSection && this.currentSection.name === '填空' && this.filledAnswer) {
        this.saveCurrentAnswer();
      }
      const section = this.sections.find(sec => sec.name === sectionName);
      if (section) {
        this.currentSection = section;
        this.currentQuestionIndex = section.questions.findIndex(q => q.id === questionId);
        this.restoreAnswer();
      } else {
        console.error('Section not found:', sectionName);
      }
    },
    saveCurrentAnswer() {
      if (!this.currentSection) return;

      const answer = this.currentSection.name === '选择' || this.currentSection.name === '判断'
        ? this.selectedOption
        : this.filledAnswer;

      this.currentSection.answers[this.currentQuestionIndex] = answer;

      if (!this.currentSection.done.includes(this.currentQuestionIndex)) {
        this.currentSection.done.push(this.currentQuestionIndex);
      }
    },
    restoreAnswer() {
      if (!this.currentSection) return;

      const answer = this.currentSection.answers[this.currentQuestionIndex];
      this.filledAnswer = ''; // Clear the filledAnswer by default
      this.selectedOption = null; // Clear the selectedOption by default
      if (answer !== undefined) {
        if (this.currentSection.name === '选择' || this.currentSection.name === '判断') {
          this.selectedOption = answer;
        } else if (this.currentSection.name === '填空') {
          this.filledAnswer = answer;
        }
      }
    },
    isQuestionDone(sectionName, questionId) {
      const section = this.sections.find(sec => sec.name === sectionName);
      if (section) {
        const questionIndex = section.questions.findIndex(q => q.id === questionId);
        return section.done.includes(questionIndex);
      }
      return false;
    },
    selectOption(option) {
      this.selectedOption = option;
      this.saveCurrentAnswer();
    },
    nextQuestion() {
      if (this.currentSection && this.currentSection.name === '填空' && this.filledAnswer) {
        this.saveCurrentAnswer();
      }
      if (this.currentSection && this.currentQuestionIndex < this.currentSection.questions.length - 1) {
        this.currentQuestionIndex++;
      } else {
        const currentSectionIndex = this.sections.indexOf(this.currentSection);
        if (currentSectionIndex < this.sections.length - 1) {
          this.currentSection = this.sections[currentSectionIndex + 1];
          this.currentQuestionIndex = 0;
        }
      }
      this.restoreAnswer();
    },
    previousQuestion() {
      if (this.currentSection && this.currentSection.name === '填空' && this.filledAnswer) {
        this.saveCurrentAnswer();
      }
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
      } else {
        const currentSectionIndex = this.sections.indexOf(this.currentSection);
        if (currentSectionIndex > 0) {
          this.currentSection = this.sections[currentSectionIndex - 1];
          this.currentQuestionIndex = this.currentSection.questions.length - 1;
        }
      }
      this.restoreAnswer();
    },
    async getIndexedDBData() {
      const db = await openDB('problemsDB', 1);
      const data = {
        single_choice_problems: await db.getAll('single_choice_problems'),
        fillin_problems: await db.getAll('fillin_problems'),
        judgement_problems: await db.getAll('judgement_problems')
      };
      return data;
    },
    async saveResponseToIndexedDB(responseData) {
      try {
        const db = await openDB('problemsDB', 1);
        for (const [tableName, problems] of Object.entries(responseData)) {
          console.log('tableName',tableName)
          for (const problem of problems) {
            await db.put(tableName, problem);
          }
        }
      } catch (error) {
        console.error('Failed to save response to IndexedDB:', error);
      }
    },
    async submitTest() {
      this.grading = true; // 显示“AI正在阅卷中...”弹窗

      async function clearTable(db, tableName) {
        const tx = db.transaction(tableName, 'readwrite');
        const store = tx.objectStore(tableName);
        await store.clear();
        await tx.done;
      }

      try {
        const db = await openDB('problemsDB', 1);
        for (const section of this.sections) {
          const tableName = this.getTableName(section.name);
          for (const question of section.questions) {
            const answer = section.answers[question.id - 1]; // Adjust index if necessary
            if (answer !== undefined) {
              const updatedQuestion = JSON.parse(JSON.stringify({ ...question, doneanswer: answer }));
              await db.put(tableName, updatedQuestion);
            }
          }
        }
        const useranswer = await this.getIndexedDBData();
        const response = await axios.post('/submit_test', useranswer);
        console.log('response.data', response.data);

        const tableNames = ['evaluation', 'dimension', 'score', 'shortcoming', 'suggestion'];
        for (const tableName of tableNames) {
          await clearTable(db, tableName);
        }
        const transaction = db.transaction(tableNames, 'readwrite');
        for (const [key, value] of Object.entries(response.data)) {
          console.log(key)
          if (key === 'knowledge_radar') {
            const store_dimension = transaction.objectStore('dimension');
            await Promise.all(value.dimension.map((dim, index) => store_dimension.put({ id: index + 1, dimension: dim })));
            const store_score = transaction.objectStore('score');
            await Promise.all(value.score.map((sc, index) => store_score.put({ id: index + 1, score: sc })));
          } else {
            const store = transaction.objectStore(key);
            await store.put({ id: 1, content: value });
          }
        }
        await transaction.done;
        // alert('测试已提交');
        this.$router.push('/evaluationpage');
      } catch (error) {
        console.error('Failed to submit test:', error);
      } finally {
        this.grading = false; // 隐藏“AI正在阅卷中...”弹窗
      }
    },
    getTableName(sectionName) {
      switch (sectionName) {
        case '选择':
          return 'single_choice_problems';
        case '填空':
          return 'fillin_problems';
        case '判断':
          return 'judgement_problems';
        default:
          throw new Error('Unknown section name: ' + sectionName);
      }
    }
  },
  async mounted() {
    await this.loadQuestions();
    this.startTimer();
    this.restoreAnswer();
    // this.setStarPositions();
    // this.starPositionInterval = setInterval(this.setStarPositions, 2000);
    this.setTitleStarPositions();
  },
  beforeUnmount() {
    clearInterval(this.timer);
    clearInterval(this.starPositionInterval);
  }
};
</script>

<style lang="scss" scoped>
.test-page {
  display: flex;
  flex-direction: column;
  height: 97vh;

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background-color: #f8f8f8;
    border-bottom: 1px solid #ddd;
    position:relative;

    .title {
      color:#1d8ade;
      flex: 1;
      text-align: center;
      font-size: 2em;
      font-weight: bolder;
    }

    .stars {
        position: absolute;
        top: 0px; /* 调整星星的位置 */
        left: 45%;
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

    .return-button {
      padding: 10px 10px;
      font-size: 1em;
      cursor: pointer;
      background-color: #1d8ade;
      color: #fff;
      border: none;
      border-radius: 5px;
    }
  }

  main {
    display: flex;
    flex: 1;
    position: relative; /* 为星光特效设置定位上下文 */
    .sidebar {
      width: 20%;
      padding: 20px;
      background-color: #f0f0f0;
      border-top: 3px solid transparent; 
      border-left: 3px solid transparent; 
      border-bottom: 3px solid transparent; /* 设置边框宽度和透明色作为基础 */
      border-right: 3px solid transparent;
      border-radius: 5px; /* 可选: 为边框添加圆角 */
      animation: border-rotation 5s linear infinite; /* 使用CSS动画 */
      overflow-y: auto;

      .timer-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20px; /* 增加间距 */
        .time {
          margin-bottom: 10px; /* 增加时间显示和按钮之间的间距 */
          font-weight: bold;
          font-size: 1.5em;
          color:#3f62ee;
        }

        .submit-button {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 10px 20px;
          font-size: 1em;
          cursor: pointer;
          background-color: #1d8ade;
          color: #fff;
          border: none;
          border-radius: 5px;
          transition: background-color 0.3s ease;
          i {
            margin-right: 5px; /* 图标和文字之间的间距 */
          }
          &:hover {
            background-color: #0d75c4;
          }
        }
      }

      .section-title {
        font-weight: bold;
        margin-bottom: 10px;
        color:#3f62ee;
      }

      .question-status-container {
        display: flex;
        flex-wrap: wrap;
      }

      .question-status {
        margin: 5px;
        padding: 5px;
        cursor: pointer;
        border: 1px solid #ccc;
        background-color: #fff;
        width: 30px;
        height: 30px;
        text-align: center;
        line-height: 30px;

        &.done {
          background-color: green;
          color: white;
        }

        &.not-done {
          background-color: rgb(157, 154, 154);
          color: white;
        }
      }
    }

    .content {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
      border: 3px solid transparent; /* 设置边框宽度和透明色作为基础 */
      border-radius: 5px; /* 可选: 为边框添加圆角 */
      animation: border-rotation 5s linear infinite; /* 使用CSS动画 */
      position: relative; /* 为星光特效设置定位上下文 */

      h2 {
        font-size: 2.0em;
        margin-bottom: 20px;
        color: #2389d7;
      }

      .question-content {
        font-size: 1.6em;
        margin-bottom: 10px;
      }

      .options {
        font-size: 1.3em;
        display: flex;
        flex-direction: column;

        .option {
          display: flex;
          align-items: center;
          cursor: pointer;
          margin-bottom: 5px;

          .circle {
            width: 20px;
            height: 20px;
            border: 1px solid #ccc;
            border-radius: 50%;
            margin-right: 10px;
          }

          .circle.selected {
            background-color: #1d8ade;
            border: 1px solid #168cac;
          }
        }
      }

      .input-box {
        width: 100%;
        height: 40px;
        padding: 5px;
        font-size: 1em;
        border: 1px solid #ccc;
        border-radius: 5px;
        margin-bottom: 10px;
      }

      .buttons {
        margin-top: 20px;

        .navigation-buttons {
          display: inline-flex; /* 使用 inline-flex */
          justify-content: center; /* 中间对齐 */

          button {
            padding: 10px 20px;
            font-size: 1em;
            cursor: pointer;
            background-color: #1d8ade;
            color: #fff;
            border: none;
            border-radius: 5px;
            margin: 0 5px; /* 左右各添加5px的间距 */
          }
        }
      }
    }

    /* 星光特效 */
    .star-effect-container {
      position: absolute;
      top: -10px;
      right: 0; /* Set container to the right */
      width: 100%;
      height: 103%;
      pointer-events: none;
      overflow: hidden;
      display: flex;
      justify-content: flex-end; /* Align stars to the right */
      align-items: center;
      border-radius: 5px;
      z-index: 9999;
    }

    .star {
      z-index: 9999;
      position: absolute;
      width: 15px;
      height: 15px;
      background: radial-gradient(circle, rgba(4, 158, 254, 1) 0%, rgba(0, 255, 255, 0) 70%);
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

    @keyframes sparkle {
      0%, 100% {
        transform: scale(1);
        opacity: 1;
      }
      50% {
        transform: scale(1.5);
        opacity: 0.5;
      }
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
}

.grading-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;

  .grading-content {
    background-color: #fff;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    // color: linear-gradient(90deg, #FF5733, #FFC300, #DAF7A6);
  }

  h2{
    color: linear-gradient(90deg, #FF5733, #FFC300, #DAF7A6);
  }
}
</style>
