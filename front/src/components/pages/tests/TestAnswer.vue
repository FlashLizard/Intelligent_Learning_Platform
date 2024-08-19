<template>
  <div class="test-result-page">
    <header>
      <span class="title"><i class="fas fa-history"></i> 测试结果
        <!-- 星星装饰 -->
        <div class="stars">
          <div v-for="n in 6" :key="n" class="star" :ref="'starTitle' + n"></div>
        </div>
      </span>
      <button class="return-button" @click="returnToPreviousPage"><i class="fas fa-arrow-left"></i> 返回</button>
    </header>
    <main>
      <aside class="sidebar">
        <div class="section" v-for="section in sections" :key="section.name">
          <div class="section-title"><i class="fas fa-book"></i>  {{ section.name }}</div>
          <div class="question-status-container">
            <div
              class="question-status"
              v-for="(question, index) in section.questions"
              :key="question.id"
              :class="{ 'correct': isAnswerCorrect(section, index), 'incorrect': !isAnswerCorrect(section, index) }"
              @click="jumpToQuestion(section.name, index + 1)"
            >
              {{ index + 1 }}
            </div>
          </div>
        </div>
      </aside>
      <div class="content">
        <h2><i class="fas fa-question-circle"></i> {{ currentSection.name }}题 第{{ currentQuestion }}题</h2>
        <div v-if="currentSection.name === '选择' && currentQuestionContent" class="choice-question">
          <div class="question-content">{{ currentQuestionContent.problem }}</div>
          <div class="options">
            <!-- 选择题选项 -->
            <div
              v-for="(option, index) in currentQuestionContent.choices"
              :key="index"
              class="option"
              :class="{
                'selected': selectedOption === index,
                'correct': selectedOption === index && isCorrectOption(index),
                'incorrect': selectedOption === index && !isCorrectOption(index),
                'user-selected': selectedOption === index && !isCorrectOption(index)
              }"
            >
              <span>{{ convertToLetter(index) }}. {{ option }}</span>
              <span class="circle" :class="{ selected: selectedOption === index }">
                <span class="status-icon" v-if="selectedOption === index">
                  <i v-if="isCorrectOption(index)" class="fas fa-check"></i>
                  <i v-else-if="selectedOption === index" class="fas fa-times"></i>
                </span>
              </span>
            </div>
          </div>
        </div>
        <div v-if="currentSection.name === '填空' && currentQuestionContent" class="fill-blank-question">
          <div class="question-content">{{ currentQuestionContent.problem }}</div>
          <!-- <input type="text" class="input-box" v-model="filledAnswer" disabled /> -->
          <input type="text" 
            class="input-box" 
            v-model="filledAnswer" 
            disabled 
            v-bind:style="{
              backgroundColor: '#f5f5f5',
              color: isAnswerCorrect(currentSection, currentQuestion - 1) ? '#6fbf73' : 'red',
            }" 
          />
        </div>
        <div v-if="currentSection.name === '判断' && currentQuestionContent" class="judge-question">
          <div class="question-content">{{ currentQuestionContent.problem }}</div>
          <div class="options">
            <!-- 判断题选项 -->
            <div class="option"
              :class="{
                'selected': selectedOption === true,
                'correct': selectedOption === true && isCorrectJudge(true),
                'incorrect': selectedOption === true && !isCorrectJudge(true),
                'user-selected': selectedOption === true && !isCorrectOption(true),
              }"
            >
              <span>A. 正确</span>
              <span class="circle" :class="{ selected: selectedOption === true }">
                <span class="status-icon" v-if="selectedOption === true">
                  <i v-if="isCorrectJudge(true)" class="fas fa-check"></i>
                  <i v-else-if="!isCorrectJudge(true)" class="fas fa-times"></i>
                </span>
              </span>
            </div>
            <div class="option"
              :class="{
                'selected': selectedOption === false,
                'correct': selectedOption === false && isCorrectJudge(false),
                'incorrect': selectedOption === false && !isCorrectJudge(false),
                'user-selected': selectedOption === false && !isCorrectOption(false)
              }"
            >
              <span>B. 错误</span>
              <span class="circle" :class="{ selected: selectedOption === false }">
                <span class="status-icon" v-if="selectedOption === false">
                  <i v-if="isCorrectJudge(false)" class="fas fa-check"></i>
                  <i v-else-if="!isCorrectJudge(false)" class="fas fa-times"></i>
                </span>
              </span>
            </div>
          </div>
        </div>
        <div v-if="currentSection.name === '选择' && currentQuestionContent" class="result-details">
          <div :class="isAnswerCorrect(currentSection, currentQuestion-1) ? 'correct-result' : 'incorrect-result'">
            <i :class="isAnswerCorrect(currentSection, currentQuestion - 1) ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> 作答结果: {{ dealDoneAnswer(currentQuestionContent.doneanswer) }}
          </div>
          <div class="correct-answer">
            <i class="fas fa-check"></i> 正确答案: {{ convertToLetter(currentQuestionContent.answer[0]) }}
          </div>
        </div>

        <div v-if="currentSection.name === '判断' && currentQuestionContent" class="result-details">
          <div :class="isAnswerCorrect(currentSection, currentQuestion-1) ? 'correct-result' : 'incorrect-result'">
            <i :class="isAnswerCorrect(currentSection, currentQuestion - 1) ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> 作答结果: {{ dealDoneAnswer(currentQuestionContent.doneanswer) }}
          </div>
          <div class="correct-answer">
            <i class="fas fa-check"></i> 正确答案: {{ currentQuestionContent.answer }}
          </div>
        </div>

        <div v-if="currentSection.name === '填空' && currentQuestionContent" class="result-details">
          <div :class="isAnswerCorrect(currentSection, currentQuestion - 1) ? 'correct-result' : 'incorrect-result'">
            <i :class="isAnswerCorrect(currentSection, currentQuestion - 1) ? 'fas fa-check-circle' : 'fas fa-times-circle'"></i> 作答结果: {{ dealDoneAnswer(currentQuestionContent.doneanswer) }}
          </div>
          <div class="correct-answer">
            <i class="fas fa-check"></i> 正确答案: {{ currentQuestionContent.answer[0] }}
          </div>
        </div>
        <div v-if="currentQuestionContent" class="explanation">
          <div class="explanation-header">
            <h3><i class="fas fa-info-circle"></i> 解析</h3>  <button class="copy-button" @click="copyAnalysis">复制</button>
          </div>
          <p>{{ currentQuestionContent.analysis }}</p>
        </div>
        <div class="buttons">
          <div class="navigation-buttons">
            <button @click="previousQuestion"><i class="fas fa-arrow-left"></i> 上一题</button>
            <button @click="nextQuestion">下一题 <i class="fas fa-arrow-right"></i></button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { openDB } from 'idb';

export default {
  data() {
    return {
      sections: [
        { name: '选择', correct: [], questions: [], answers: {} },
        { name: '填空', correct: [], questions: [], answers: {} },
        { name: '判断', correct: [], questions: [], answers: {} },
      ],
      currentSection: { name: '选择', correct: [], questions: [], answers: {} },
      currentQuestion: 1,
      selectedOption: null,
      filledAnswer: '',
    };
  },
  computed: {
    currentQuestionContent() {
      return this.currentSection.questions[this.currentQuestion - 1] || null;
    },
    correctAnswer() {
      const answer = this.currentQuestionContent.answer;
      console.log(this.currentQuestionContent)
      console.log('correctAnswer:',answer)
      return Array.isArray(answer) ? answer : [answer];
    }
  },
  methods: {
    copyAnalysis() {
      const analysisText = this.currentQuestionContent.analysis;

      if (!navigator.clipboard) {
        const textArea = document.createElement("textarea");
        textArea.value = analysisText;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
          document.execCommand('copy');
          this.showCopySuccess();
        } catch (err) {
          console.error("复制失败", err);
        }
        document.body.removeChild(textArea);
      } else {
        navigator.clipboard.writeText(analysisText).then(() => {
          this.showCopySuccess();
        }, err => {
          console.error("复制失败", err);
        });
      }
    },
    showCopySuccess() {
      const button = document.querySelector('.copy-button');
      button.textContent = '复制成功';
      setTimeout(() => {
        button.textContent = '复制';
      }, 2000);
    },
    async fetchData() {
      try {
        const singleChoiceQuestions = await this.getAllData('single_choice_problems');
        const judgementQuestions = await this.getAllData('judgement_problems');
        const fillinQuestions = await this.getAllData('fillin_problems');

        this.sections[0].questions = singleChoiceQuestions;
        this.sections[1].questions = fillinQuestions;
        this.sections[2].questions = judgementQuestions;

        this.currentSection = this.sections[0];
        this.selectedOption =this.currentSection.questions[this.currentQuestion-1].doneanswer;
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    },
    async openDatabase() {
      return openDB('problemsDB', 1, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('single_choice_problems')) {
            db.createObjectStore('single_choice_problems', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('judgement_problems')) {
            db.createObjectStore('judgement_problems', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('fillin_problems')) {
            db.createObjectStore('fillin_problems', { keyPath: 'id', autoIncrement: true });
          }
        }
      });
    },
    async getAllData(storeName) {
      const db = await this.openDatabase();
      return db.getAll(storeName);
    },
    returnToPreviousPage() {
      this.$router.back();
    },
    jumpToQuestion(sectionName, questionNumber) {
      this.currentSection = this.sections.find((section) => section.name === sectionName);
      this.currentQuestion = questionNumber;
      // console.log(this.currentSection.questions[this.currentQuestion-1]);
      this.selectedOption =this.currentSection.questions[this.currentQuestion-1].doneanswer;
      // console.log(this.selectedOption);
      if(this.currentSection.name==='填空'){
        this.filledAnswer = this.currentSection.questions[this.currentQuestion-1].doneanswer;
      }
    },
    isAnswerCorrect(section, index) {
      const question = section.questions[index];
      if(question.doneanswer===''){
        return false;
      }
      if(section.name === '选择' || section.name === '填空'){
        console.log('isAnswerCorrect',(question.answer)[0],question.doneanswer);
        return (question.doneanswer === (question.answer)[0]);
      }
      console.log('isAnswerCorrect',question.answer,question.doneanswer);
      return (question.doneanswer === question.answer);
    },
    isCorrectOption(index) {
      return this.correctAnswer.includes(index);
    },
    isCorrectFillBlank() {
      return this.correctAnswer.every((answer, index) => answer === this.filledAnswer[index]);
    },
    isCorrectJudge(answer) {
      let RealAnswer = Array.isArray(this.correctAnswer) ? (this.correctAnswer)[0] : this.correctAnswer;
      return RealAnswer === answer;
    },
    previousQuestion() {
      if (this.currentQuestion > 1) {
        this.currentQuestion--;
        console.log(this.currentSection.questions[this.currentQuestion-1]);
        this.selectedOption =this.currentSection.questions[this.currentQuestion-1].doneanswer;
        console.log(this.selectedOption);
      } else {
        const currentSectionIndex = this.sections.indexOf(this.currentSection);
        if (currentSectionIndex > 0) {
          this.currentSection = this.sections[currentSectionIndex - 1];
          this.currentQuestion = this.currentSection.questions.length ;
          this.selectedOption =this.currentSection.questions[this.currentQuestion-1].doneanswer;
          console.log(this.selectedOption);
        }
      }
      if(this.currentSection.name==='填空'){
        this.filledAnswer = this.currentSection.questions[this.currentQuestion-1].doneanswer;
      }
    },
    nextQuestion() {
      if (this.currentSection && this.currentQuestion < this.currentSection.questions.length) {
        this.currentQuestion++;
        console.log(this.currentSection.questions[this.currentQuestion-1])
        this.selectedOption =this.currentSection.questions[this.currentQuestion-1].doneanswer;
        console.log(this.selectedOption);
      } else {
        const currentSectionIndex = this.sections.indexOf(this.currentSection);
        if (currentSectionIndex < this.sections.length - 1) {
          this.currentSection = this.sections[currentSectionIndex + 1];
          this.currentQuestion = 1;
          this.selectedOption =this.currentSection.questions[this.currentQuestion-1].doneanswer;
          console.log(this.selectedOption);
        }
      }
      if(this.currentSection.name==='填空'){
        this.filledAnswer = this.currentSection.questions[this.currentQuestion-1].doneanswer;
      }
    },
    dealDoneAnswer(ans) {
      if(ans === ""){
        return '未作答';
      }
      if(Array.isArray(ans)){
        if(this.currentSection.name==='选择'){
          return this.convertToLetter(ans);
        }
        return ans[0];
      }
      if(this.currentSection.name==='选择'){
        return this.convertToLetter(ans);
      }
      return ans;
    },
    convertToLetter(ans) {
      return String.fromCharCode(65 + ans); // Convert 0, 1, 2, ... to A, B, C, ...
    },
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
  },
  mounted() {
    this.fetchData();
    this.setTitleStarPositions();
  },
};
</script>

<style scoped>
.test-result-page {
  display: flex;
  flex-direction: column;
  height: 98vh;
  font-family: Arial, sans-serif;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

.title {
  margin-left: 45%;
  font-size: 30px;
  font-weight: bold;
  color: #0474de;
  .stars {
        position: absolute;
        top: 0px;
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
}

.return-button {
  padding: 5px 10px;
  font-size: 16px;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

.return-button:hover {
  background-color: #0056b3;
}

main {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 200px;
  background-color: #e9e9e9;
  padding: 10px;
  /* border-right: 1px solid #ddd; */
  border: 3px solid transparent;
  border-radius: 5px;
  animation: border-rotation 5s linear infinite; 
}

.section {
  margin-bottom: 20px;
}

.section-title {
  color:#3f62ee;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px;
}

.question-status-container {
  display: flex;
  flex-wrap: wrap;
}

.question-status {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #a8a8a8;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 5px;
  cursor: pointer;
  transition: background-color 0.3s, border 0.3s;
}

.question-status.correct {
  background-color: #a8d8a8;
  border-color: #6fbf73;
}

.question-status.incorrect {
  background-color: #f8a8a8;
  border-color: #e57373;
}

.question-status:hover {
  background-color: #ddd;
}

.content {
  flex: 1;
  padding: 20px;
  border: 3px solid transparent;
  border-radius: 5px;
  animation: border-rotation 5s linear infinite; 
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

h2 {
  font-size: 2.0em;
  margin-bottom: 20px;
  color: #2389d7;
}

.choice-question,
.fill-blank-question,
.judge-question {
  margin-bottom: 20px;
}

.question-content {
  font-size: 18px;
  margin-bottom: 10px;
}

.options {
  display: flex;
  flex-direction: column;
}

.option {
  width:30%;
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 10px;
  margin-left: 10px;
  cursor: pointer;
  transition: background-color 0.3s, border 0.3s;
}

.option:hover {
  background-color: #ddd;
}

.option.selected {
  background-color: #a8d8a8;
}

.option.correct {
  background-color: #a8d8a8;
  border-color: #6fbf73;
}

.option.incorrect {
  background-color: #ffffff;
}
.option.incorrect.user-selected {
  background-color: #f8a8a8;
  border-color: #e57373;
  color: red;
}

.option.selected {
  background-color: #a8d8a8;
}


.circle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #007bff;
  margin-left: 10px;
  display: inline-block;
  transition: background-color 0.3s;
  display: flex; /* 使用flexbox布局 */
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
}

.circle.selected {
  background-color: #007bff;
}

.status-icon {
  font-size: 16px;
  color: white;
}

.input-box {
  padding: 5px;
  font-size: 16px;
  border-radius: 5px;
  border: 1px solid #ddd;
  margin-bottom: 10px;
}

.explanation {
  font-size: 16px;
  margin-bottom: 20px;

  p{
    margin-top: -15px;
    margin-left: 30px;
  }
}

.explanation-header {
  display: flex;
  align-items: center;
  margin-top:10px;
  margin-bottom: 30px;
  font-size: 17px;
  font-weight: bolder;
  color:#2389d7;

  h3{
    margin-right: 10px;
  }
}

.copy-button {
  background-color: white;
  color: gray;
  border: 1px solid #ccc;
  padding: 5px 10px;
  margin-right: 10px;
  cursor: pointer;
  border-radius: 5px;
  font-size: 14px;
  transition: background-color 0.3s, color 0.3s;
}

.copy-button:hover {
  background-color: #f0f0f0;
  color: #007bff;
}


.result-details {
  margin-top: 20px;
  font-size: 20px;
}

.correct-answer {
  color: rgb(2, 166, 2);
}

.correct-result {
  color: rgb(2, 166, 2);
}

.incorrect-result {
  color: rgb(253, 77, 77);
}

.buttons {
  display: flex;
  justify-content: space-between;
}

.navigation-buttons {
  display: flex;
}

.navigation-buttons button {
  padding: 5px 10px;
  font-size: 16px;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  border-radius: 5px;
  margin-left: 60px;
  margin-right: 80px;
}

.navigation-buttons button:hover {
  background-color: #0056b3;
}
</style>
