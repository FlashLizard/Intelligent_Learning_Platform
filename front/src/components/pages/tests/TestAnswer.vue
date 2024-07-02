<template>
    <div class="test-result-page">
      <header>
        <span class="title">测试结果</span>
        <button class="return-button" @click="returnToPreviousPage">返回</button>
      </header>
      <main>
        <aside class="sidebar">
          <div class="section" v-for="section in sections" :key="section.name">
            <div class="section-title">{{ section.name }}</div>
            <div class="question-status-container">
              <div
                class="question-status"
                v-for="n in 15"
                :key="n"
                :class="{ 'correct': section.correct.includes(n), 'incorrect': !section.correct.includes(n) }"
                @click="jumpToQuestion(section.name, n)"
              >
                {{ n }}
              </div>
            </div>
          </div>
        </aside>
        <div class="content">
          <h2>{{ currentSection.name }}题 第{{ currentQuestion }}题</h2>
          <div v-if="currentSection.name === '选择'" class="choice-question">
            <div class="question-content">{{ currentQuestion }}. {{ currentQuestionContent }}</div>
            <div class="options">
              <div
                v-for="(option, index) in choiceOptions"
                :key="index"
                class="option"
                :class="{ 'selected': selectedOption === index, 'correct': isCorrectOption(index), 'incorrect': !isCorrectOption(index) && selectedOption === index }"
              >
                <span>{{ option.label }}. {{ option.text }}</span>
                <span class="circle" :class="{ selected: selectedOption === index }"></span>
              </div>
            </div>
          </div>
          <div v-if="currentSection.name === '填空'" class="fill-blank-question">
            <div class="question-content">{{ currentQuestion }}. {{ currentQuestionContent }}</div>
            <input type="text" class="input-box" v-model="filledAnswer" disabled />
            <div :class="{ 'correct': isCorrectFillBlank(), 'incorrect': !isCorrectFillBlank() }">
              正确答案: {{ correctAnswer }}
            </div>
          </div>
          <div v-if="currentSection.name === '判断'" class="judge-question">
            <div class="question-content">{{ currentQuestion }}. {{ currentQuestionContent }}</div>
            <div class="options">
              <div class="option" :class="{ 'selected': selectedOption === true, 'correct': selectedOption === true && isCorrectJudge(true), 'incorrect': selectedOption === true && !isCorrectJudge(true) }">
                <span>正确</span>
                <span class="circle" :class="{ selected: selectedOption === true }"></span>
              </div>
              <div class="option" :class="{ 'selected': selectedOption === false, 'correct': selectedOption === false && isCorrectJudge(false), 'incorrect': selectedOption === false && !isCorrectJudge(false) }">
                <span>错误</span>
                <span class="circle" :class="{ selected: selectedOption === false }"></span>
              </div>
            </div>
          </div>
          <div class="explanation">
            <h3>解析</h3>
            <p>{{ explanation }}</p>
          </div>
          <div class="buttons">
            <div class="navigation-buttons">
              <button @click="previousQuestion">上一题</button>
              <button @click="nextQuestion">下一题</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        sections: [
          { name: '选择', correct: [1, 2, 3], answers: {} },
          { name: '填空', correct: [1, 2], answers: {} },
          { name: '判断', correct: [], answers: {} },
        ],
        currentSection: { name: '选择', correct: [1, 2, 3], answers: {} },
        currentQuestion: 1,
        selectedOption: null,
        filledAnswer: '',
        questionContents: {
          选择: [
            '选择题内容1',
            '选择题内容2',
            '选择题内容3',
            '选择题内容4',
            '选择题内容5',
            '选择题内容6',
            '选择题内容7',
            '选择题内容8',
            '选择题内容9',
            '选择题内容10',
            '选择题内容11',
            '选择题内容12',
            '选择题内容13',
            '选择题内容14',
            '选择题内容15',
          ],
          填空: [
            '填空题内容1',
            '填空题内容2',
            '填空题内容3',
            '填空题内容4',
            '填空题内容5',
            '填空题内容6',
            '填空题内容7',
            '填空题内容8',
            '填空题内容9',
            '填空题内容10',
            '填空题内容11',
            '填空题内容12',
            '填空题内容13',
            '填空题内容14',
            '填空题内容15',
          ],
          判断: [
            '判断题内容1',
            '判断题内容2',
            '判断题内容3',
            '判断题内容4',
            '判断题内容5',
            '判断题内容6',
            '判断题内容7',
            '判断题内容8',
            '判断题内容9',
            '判断题内容10',
            '判断题内容11',
            '判断题内容12',
            '判断题内容13',
            '判断题内容14',
            '判断题内容15',
          ],
        },
        explanations: {
          选择: [
            '选择题解析1',
            '选择题解析2',
            '选择题解析3',
            '选择题解析4',
            '选择题解析5',
            '选择题解析6',
            '选择题解析7',
            '选择题解析8',
            '选择题解析9',
            '选择题解析10',
            '选择题解析11',
            '选择题解析12',
            '选择题解析13',
            '选择题解析14',
            '选择题解析15',
          ],
          填空: [
            '填空题解析1',
            '填空题解析2',
            '填空题解析3',
            '填空题解析4',
            '填空题解析5',
            '填空题解析6',
            '填空题解析7',
            '填空题解析8',
            '填空题解析9',
            '填空题解析10',
            '填空题解析11',
            '填空题解析12',
            '填空题解析13',
            '填空题解析14',
            '填空题解析15',
          ],
          判断: [
            '判断题解析1',
            '判断题解析2',
            '判断题解析3',
            '判断题解析4',
            '判断题解析5',
            '判断题解析6',
            '判断题解析7',
            '判断题解析8',
            '判断题解析9',
            '判断题解析10',
            '判断题解析11',
            '判断题解析12',
            '判断题解析13',
            '判断题解析14',
            '判断题解析15',
          ],
        },
        correctAnswers: {
          选择: [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2],
          填空: ['答案1', '答案2', '答案3', '答案4', '答案5', '答案6', '答案7', '答案8', '答案9', '答案10', '答案11', '答案12', '答案13', '答案14', '答案15'],
          判断: [true, false, true, false, true, false, true, false, true, false, true, false, true, false, true],
        },
        choiceOptions: [
          { label: 'A', text: '选项A' },
          { label: 'B', text: '选项B' },
          { label: 'C', text: '选项C' },
          { label: 'D', text: '选项D' },
        ],
      };
    },
    computed: {
      currentQuestionContent() {
        return this.questionContents[this.currentSection.name][this.currentQuestion - 1];
      },
      correctAnswer() {
        return this.correctAnswers[this.currentSection.name][this.currentQuestion - 1];
      },
      explanation() {
        return this.explanations[this.currentSection.name][this.currentQuestion - 1];
      },
    },
    methods: {
      returnToPreviousPage() {
        this.$router.back();
      },
      jumpToQuestion(sectionName, questionNumber) {
        this.currentSection = this.sections.find((section) => section.name === sectionName);
        this.currentQuestion = questionNumber;
        this.restoreAnswer();
      },
      restoreAnswer() {
        const answer = this.currentSection.answers[this.currentQuestion];
        if (this.currentSection.name === '选择') {
          this.selectedOption = answer !== undefined ? answer : null;
        } else if (this.currentSection.name === '填空') {
          this.filledAnswer = answer !== undefined ? answer : '';
        } else if (this.currentSection.name === '判断') {
          this.selectedOption = answer !== undefined ? answer : null;
        }
      },
      isCorrectOption(index) {
        return this.correctAnswers[this.currentSection.name][this.currentQuestion - 1] === index;
      },
      isCorrectFillBlank() {
        return this.correctAnswers[this.currentSection.name][this.currentQuestion - 1] === this.filledAnswer;
      },
      isCorrectJudge(answer) {
        return this.correctAnswers[this.currentSection.name][this.currentQuestion - 1] === answer;
      },
      previousQuestion() {
        if (this.currentQuestion > 1) {
          this.currentQuestion--;
          this.restoreAnswer();
        }
      },
      nextQuestion() {
        if (this.currentQuestion < 15) {
          this.currentQuestion++;
          this.restoreAnswer();
        }
      },
    },
    mounted() {
      this.restoreAnswer();
    },
  };
  </script>
<style scoped>
.test-result-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
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
  font-size: 24px;
  font-weight: bold;
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
  border-right: 1px solid #ddd;
}

.section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
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
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 5px;
  border-radius: 5px;
  cursor: pointer;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
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
  overflow-y: auto;
}

.choice-question, .fill-blank-question, .judge-question {
  margin-bottom: 20px;
}

.question-content {
  font-size: 20px;
  margin-bottom: 10px;
}

.options {
  display: flex;
  flex-direction: column;
}

.option {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s, border 0.3s;
}

.option:hover {
  background-color: #f5f5f5;
}

.option .circle {
  width: 20px;
  height: 20px;
  border: 2px solid #000;
  border-radius: 50%;
  margin-left: 10px;
  transition: background-color 0.3s;
}

.option.correct {
  background-color: #a8d8a8;
  border-color: #6fbf73;
}

.option.incorrect {
  background-color: #f8a8a8;
  border-color: #e57373;
}

.option.selected .circle {
  background-color: #000;
}

.input-box {
  padding: 5px;
  font-size: 16px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.explanation {
  margin-bottom: 20px;
}

.explanation h3 {
  margin-bottom: 10px;
}

.buttons {
  display: flex;
  justify-content: space-between;
}

.navigation-buttons {
  display: flex;
  gap: 10px;
}

.navigation-buttons button {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.navigation-buttons button:hover {
  background-color: #0056b3;
}
</style>
  