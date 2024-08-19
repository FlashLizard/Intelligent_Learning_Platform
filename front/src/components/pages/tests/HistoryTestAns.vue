<template>
  <div class="test-result-page">
    <header>
      <span class="title"><i class="fas fa-check-circle"></i>测试结果</span>
      <button class="return-button" @click="returnToPreviousPage">
        <i class="fas fa-arrow-left"></i> 返回
      </button>
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
              :class="{
                'correct': isAnswerCorrect(section, index),
                'incorrect': !isAnswerCorrect(section, index)
              }"
              @click="jumpToQuestion(section.name, index + 1)"
            >
              {{ index + 1 }}
            </div>
          </div>
        </div>
      </aside>
      <div class="content">
        <h2><i class="fas fa-question-circle"></i> {{ currentSection.name }}题 第{{ currentQuestion }}题</h2>
        <!-- 选择题 -->
        <div v-if="currentSection.name === '选择' && currentQuestionContent" class="choice-question">
          <div class="question-content">{{ currentQuestionContent.problem }}</div>
          <div class="options">
            <div
              v-for="(option, index) in currentQuestionContent.choices"
              :key="index"
              class="option"
              :class="{
                'correct': selectedOption === index && isCorrectOption(index),
                'incorrect': selectedOption === index && !isCorrectOption(index)
              }"
            >
              <span>{{ getOptionLetter(index) }}. {{ option }}</span>
              <span class="circle" :class="{ selected: selectedOption === index }"></span>
            </div>
          </div>
        </div>
        <div v-if="currentSection.name === '填空' && currentQuestionContent" class="fill-blank-question">
          <div class="question-content">{{ currentQuestionContent.problem }}</div>
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
            <div 
              class="option" 
              :class="{
                'correct': selectedOption === true && isCorrectJudge(true),
                'incorrect': selectedOption === true && !isCorrectJudge(true)
              }">
              <span>A. 正确</span>
              <span class="circle" :class="{ selected: selectedOption === true }"></span>
            </div>
            <div 
              class="option" 
              :class="{
                'correct': selectedOption === false && isCorrectJudge(false),
                'incorrect': selectedOption === false && !isCorrectJudge(false)
              }">
              <span>B. 错误</span>
              <span class="circle" :class="{ selected: selectedOption === false }"></span>
            </div>
          </div>
        </div>
        <div v-if="currentSection.name === '选择' && currentQuestionContent" class="result-details">
          <div :style="{ color: isAnswerCorrect(currentSection, currentQuestion - 1) ? 'green' : 'red' }">
            作答结果: {{ caluserans(this.currentSection,getUserAnswer()) }}
          </div>
          <div style="color: green;">
            正确答案: {{ getOptionLetter(currentQuestionContent.answer[0]) }}
          </div>
        </div>
        <div v-else-if="currentSection.name === '填空' && currentQuestionContent" class="result-details">
          <div :style="{ color: isAnswerCorrect(currentSection, currentQuestion - 1) ? 'green' : 'red' }">
            作答结果: {{ caluserans(this.currentSection,getUserAnswer()) }}
          </div>
          <div style="color: green;">
            正确答案: {{ currentQuestionContent.answer.join(' ') }}
          </div>
        </div>
        <div v-else-if="currentSection.name === '判断' && currentQuestionContent" class="result-details">
          <div :style="{ color: isAnswerCorrect(currentSection, currentQuestion - 1) ? 'green' : 'red' }">
            作答结果: {{ caluserans(this.currentSection,getUserAnswer()) }}
          </div>
          <div style="color: green;">
            正确答案: {{ currentQuestionContent.answer }}
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
            <button @click="previousQuestion">
              <i class="fas fa-arrow-left"></i> 上一题
            </button>
            <button @click="nextQuestion">
              下一题 <i class="fas fa-arrow-right"></i>
            </button>
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
      choiceAnswers: [],
      fillinAnswers: [],
      judgeAnswers: []
    };
  },
  computed: {
    currentQuestionContent() {
      return this.currentSection.questions[this.currentQuestion - 1] || null;
    },
    correctAnswer() {
      return this.currentQuestionContent?.answer || null;
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
    calrightans(section,right) {
      if(section.name==='填空'){
        console.log('fillinright:',right.length,right[0],right[1])
        return (this.formatAnswer(right)).slice(0,-1);
      }else{
        return this.formatAnswer(right);
      }
    },
    caluserans(section,userans) {
      if(section.name==='填空'){
        if(userans === '未作答'){
          return '未作答'
        }else{
          return (this.formatAnswer(userans));
        }
      }else{
        return this.formatAnswer(userans);
      }
    },
    async fetchData() {
      try {
        // Open the IndexedDB and read the test data
        const db = await this.openDatabase();
        const test = await this.getTestData(db);

        // Update sections with the fetched test data
        this.sections[0].questions = test.test_questions.filter(q => q.type === 'single_choice');
        this.sections[1].questions = test.test_questions.filter(q => q.type === 'fillin');
        this.sections[2].questions = test.test_questions.filter(q => q.type === 'judgement');

        // Set user answers
        const userAnswers = JSON.parse(test.user_answers);
        this.choiceAnswers = [];
        this.fillinAnswers = [];
        this.judgeAnswers = [];

        // 分配 userAnswers 到对应的数组中
        test.test_questions.forEach((question, index) => {
          if (question.type === 'single_choice') {
            this.choiceAnswers.push(userAnswers[index]);
          } else if (question.type === 'fillin') {
            this.fillinAnswers.push(userAnswers[index]);
          } else if (question.type === 'judgement') {
            this.judgeAnswers.push(userAnswers[index]);
          }
        });

        // Set the initial current section and restore the answers
        this.currentSection = this.sections[0];
        if(this.currentSection.name === '选择'){
          this.selectedOption = (this.choiceAnswers)[this.currentQuestion-1];
        }
        else if(this.currentSection.name === '填空'){
          this.filledAnswer = (this.fillinAnswers)[this.currentQuestion-1];
          console.log(this.filledAnswer);
        }
        else if(this.currentSection.name === '判断'){
          this.selectedOption = (this.judgeAnswers)[this.currentQuestion-1];
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
      }
    },
    async openDatabase() {
      return openDB('HistoryTestDB', 1, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('tests')) {
            db.createObjectStore('tests', { keyPath: 'id', autoIncrement: true });
          }
        }
      });
    },
    async getTestData(db) {
      const tx = db.transaction('tests', 'readonly');
      const store = tx.objectStore('tests');
      const allTests = await store.getAll();
      return allTests.length ? allTests[0] : null;  // Assuming there's only one test
    },
    returnToPreviousPage() {
      this.$router.back();
    },
    jumpToQuestion(sectionName, questionNumber) {
      this.currentSection = this.sections.find((section) => section.name === sectionName);
      this.currentQuestion = questionNumber;
      if(this.currentSection.name === '选择'){
        this.selectedOption = (this.choiceAnswers)[this.currentQuestion-1];
      }
      else if(this.currentSection.name === '填空'){
        this.filledAnswer = (this.fillinAnswers)[this.currentQuestion-1];
        console.log(this.filledAnswer);
      }
      else if(this.currentSection.name === '判断'){
        this.selectedOption = (this.judgeAnswers)[this.currentQuestion-1];
      }
    },
    restoreAnswer() {
      let answer = null;
      if (this.currentSection.name === '选择') {
        answer = this.choiceAnswers[this.currentQuestion - 1];
        this.selectedOption = answer !== undefined ? answer : null;
      } else if (this.currentSection.name === '填空') {
        answer = this.fillinAnswers[this.currentQuestion - 1];
        this.filledAnswer = answer !== undefined ? answer : '';
      } else if (this.currentSection.name === '判断') {
        answer = this.judgeAnswers[this.currentQuestion - 1];
        this.selectedOption = answer !== undefined ? answer : null;
      }
    },
    getUserAnswer() {
      let answer = null;
      if (this.currentSection.name === '选择') {
        answer = this.choiceAnswers[this.currentQuestion - 1];
      } else if (this.currentSection.name === '填空') {
        answer = this.fillinAnswers[this.currentQuestion - 1];
      } else if (this.currentSection.name === '判断') {
        answer = this.judgeAnswers[this.currentQuestion - 1];
      }
      if (answer === undefined || answer === null || answer === '') {
        return "未作答";
      }
      return answer;
    },
    isAnswerCorrect(section, index) {
      let answer = null;
      if (section.name === '选择') {
        answer = this.choiceAnswers[index];
      } else if (section.name === '填空') {
        answer = this.fillinAnswers[index];
      } else if (section.name === '判断') {
        answer = this.judgeAnswers[index];
      }
      if (answer === undefined || answer === null || answer === '') {
        answer = "未作答";
        return false;
      }

      let right = section.questions[index] || null
      
      if(section.name ==='填空'){
        let stringright= this.formatAnswer(right.answer)
        let stringans = this.formatAnswer(answer)
        if(stringans==='未作答'){
          return false;
        }else{
          return stringright.slice(0,-1) === stringans.slice(0,-1)
        }
      }
      else if(section.name ==='判断' || section.name ==='选择'){
        return this.formatAnswer(right.answer) ===  this.formatAnswer(answer)
      }
    },
    isCorrectOption(index) {
      return this.currentQuestionContent.answer.includes(index);
    },
    isCorrectJudge(answer) {
      return this.currentQuestionContent.answer === answer;
    },
    getOptionLetter(index) {
      const letters = ['A', 'B', 'C', 'D'];
      return letters[index] || index + 1;
    },
    formatAnswer(answer) {
      // console.log('format',typeof(answer))
      if (typeof answer === 'number') {
        return this.getOptionLetter(answer);
      } else if (Array.isArray(answer)) {
        return answer.map(this.getOptionLetter).join(', ');
      } 
      return answer;
    },
    previousQuestion() {
      if (this.currentQuestion > 1) {
        this.currentQuestion--;
      } else {
        const currentSectionIndex = this.sections.indexOf(this.currentSection);
        if (currentSectionIndex > 0) {
          this.currentSection = this.sections[currentSectionIndex - 1];
          this.currentQuestion = this.currentSection.questions.length ;
        }
      }
      if(this.currentSection.name === '选择'){
        this.selectedOption = (this.choiceAnswers)[this.currentQuestion-1];
      }
      else if(this.currentSection.name === '填空'){
        this.filledAnswer = (this.fillinAnswers)[this.currentQuestion-1];
      }
      else if(this.currentSection.name === '判断'){
        this.selectedOption = (this.judgeAnswers)[this.currentQuestion-1];
      }
    },
    nextQuestion() {
      if (this.currentSection && this.currentQuestion < this.currentSection.questions.length) {
        this.currentQuestion++;
      } else {
        const currentSectionIndex = this.sections.indexOf(this.currentSection);
        if (currentSectionIndex < this.sections.length - 1) {
          this.currentSection = this.sections[currentSectionIndex + 1];
          this.currentQuestion = 1;
        }
      }
      // console.log(this.currentSection)
      if(this.currentSection.name === '选择'){
        this.selectedOption = (this.choiceAnswers)[this.currentQuestion-1];
      }
      else if(this.currentSection.name === '填空'){
        this.filledAnswer = (this.fillinAnswers)[this.currentQuestion-1];
      }
      else if(this.currentSection.name === '判断'){
        this.selectedOption = (this.judgeAnswers)[this.currentQuestion-1];
      }
      console.log(this.selectedOption);
    }
  },
  async mounted() {
    await this.fetchData();
  }
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
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  font-weight: bold;
  color: #0474de;
  margin-left: 45%;
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

.section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #0474de;
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
  background-color: #6fbf73; /* Changed to a clear green color */
  border-color: #6fbf73;
}

.question-status.incorrect {
  background-color: #e57373; /* Changed to a clear red color */
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
  font-weight: bold;
  margin-bottom: 20px;
  color: #0474de;
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
  width:40%;
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 10px;
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
  background-color: #6fbf73;
  border-color: #6fbf73;
}

.option.incorrect {
  background-color: #e57373;
  border-color: #e57373;
}

.circle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #007bff;
  margin-left: 10px;
  display: inline-block;
  transition: background-color 0.3s;
}

.circle.selected {
  background-color: #007bff;
}

.input-box {
  padding: 5px;
  font-size: 16px;
  border-radius: 5px;
  border: 1px solid #999999;
  margin-bottom: 10px;
}

.explanation {
  font-size: 16px;
  margin-bottom: 13px;
  p {
    margin-top: -10px;;
  }
}
.explanation-header {
  display: flex;
  align-items: center;
  margin-bottom: 0px;
  font-size: 20px;
  font-weight: bolder;
  color:#2389d7;

  h3{
    font-size: 1.5em;
    margin-top: 20px;
    margin-bottom: 20px;
    margin-right: 10px;
  }
}

.result-details {
  margin-top: 20px;
  font-size: 16px;
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
  margin-right: 10px;
}

.navigation-buttons button:hover {
  background-color: #0056b3;
}
</style>
