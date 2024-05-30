<template>
  <div class="test-page">
    <header>
      <span class="title">测试</span>
      <button class="return-button" @click="returnToPreviousPage">返回</button>
    </header>
    <main>
      <aside class="sidebar">
        <div class="timer-container">
          <div class="time">考试时间：{{ formattedMinutes }}:{{ formattedSeconds }}</div>
          <button @click="submitTest" class="submit-button">交卷</button>
        </div>
        <div class="section" v-for="section in sections" :key="section.name">
          <div class="section-title">{{ section.name }}</div>
          <div class="question-status-container">
            <div
              class="question-status"
              v-for="n in 15"
              :key="n"
              :class="{ 'done': section.done.includes(n), 'not-done': !section.done.includes(n) }"
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
            <div v-for="(option, index) in choiceOptions" :key="index" class="option" @click="selectOption(index)">
              <span>{{ option.label }}. {{ option.text }}</span>
              <span class="circle" :class="{ selected: selectedOption === index }"></span>
            </div>
          </div>
        </div>
        <div v-if="currentSection.name === '填空'" class="fill-blank-question">
          <div class="question-content">{{ currentQuestion }}. {{ currentQuestionContent }}</div>
          <input type="text" class="input-box" placeholder="请输入答案" v-model="filledAnswer" />
        </div>
        <div v-if="currentSection.name === '判断'" class="judge-question">
          <div class="question-content">{{ currentQuestion }}. {{ currentQuestionContent }}</div>
          <div class="options">
            <div class="option" @click="selectOption(true)">
              <span>正确</span>
              <span class="circle" :class="{ selected: selectedOption === true }"></span>
            </div>
            <div class="option" @click="selectOption(false)">
              <span>错误</span>
              <span class="circle" :class="{ selected: selectedOption === false }"></span>
            </div>
          </div>
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
      timer: null,
      minutes: 0,
      seconds: 0,
      sections: [
        { name: '选择', done: [1, 2, 3], answers: {} },
        { name: '填空', done: [1, 2], answers: {} },
        { name: '判断', done: [], answers: {} },
      ],
      currentSection: { name: '选择', done: [1, 2, 3], answers: {} },
      currentQuestion: 1,
      selectedOption: null,
      filledAnswer: '', // 新增填空题答案绑定
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
      choiceOptions: [
        { label: 'A', text: '选项A' },
        { label: 'B', text: '选项B' },
        { label: 'C', text: '选项C' },
        { label: 'D', text: '选项D' },
      ],
    };
  },
  computed: {
    formattedMinutes() {
      return this.minutes.toString().padStart(2, '0');
    },
    formattedSeconds() {
      return this.seconds.toString().padStart(2, '0');
    },
    currentQuestionContent() {
      return this.questionContents[this.currentSection.name][this.currentQuestion - 1];
    },
  },
  methods: {
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
    jumpToQuestion(sectionName, questionNumber) {
      this.saveAnswer();
      this.currentSection = this.sections.find((section) => section.name === sectionName);
      this.currentQuestion = questionNumber;
      this.restoreAnswer();
    },
    saveAnswer() {
    if (this.currentSection.name === '选择') {
      this.currentSection.answers = {
        ...this.currentSection.answers,
        [this.currentQuestion]: this.selectedOption,
      };
    } else if (this.currentSection.name === '填空') {
      this.currentSection.answers = {
        ...this.currentSection.answers,
        [this.currentQuestion]: this.filledAnswer,
      };
    } else if (this.currentSection.name === '判断') {
      this.currentSection.answers = {
        ...this.currentSection.answers,
        [this.currentQuestion]: this.selectedOption,
      };
    }
  },
    restoreAnswer() {
      if (this.currentSection.answers) {
        const answer = this.currentSection.answers[this.currentQuestion];
        if (answer !== undefined) {
          if (this.currentSection.name === '选择' || this.currentSection.name === '判断') {
            this.selectedOption = answer;
          } else if (this.currentSection.name === '填空') {
            this.filledAnswer = answer;
          }
        }
      }
    },
    selectOption(option) {
      this.selectedOption = option;
    },
    nextQuestion() {
      const currentSectionIndex = this.sections.indexOf(this.currentSection);
      if (this.currentQuestion < 15) {
        this.currentQuestion++;
      } else if (currentSectionIndex < this.sections.length - 1) {
        this.currentSection = this.sections[currentSectionIndex + 1];
        this.currentQuestion = 1;
      }
      this.selectedOption = null;
      this.filledAnswer = '';
    },
    previousQuestion() {
      if (this.currentQuestion > 1) {
        this.currentQuestion--;
      } else {
        const currentSectionIndex = this.sections.indexOf(this.currentSection);
        if (currentSectionIndex > 0) {
          this.currentSection = this.sections[currentSectionIndex - 1];
          this.currentQuestion = 15;
        }
      }
      this.selectedOption = null;
      this.filledAnswer = '';
    },
    submitTest() {
      alert('测试已提交');
    },
  },
  mounted() {
    this.startTimer();
  },
  beforeUnmount() {
    clearInterval(this.timer);
  },
};
</script>


<style lang="scss" scoped>
.test-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  .title {
    flex: 1; /* 让标题占据剩余空间 */
    text-align: center; /* 居中标题文本 */
    font-size: 2em;
    font-weight: bolder;
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background-color: #f8f8f8;
    border-bottom: 1px solid #ddd;
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

  main {
    display: flex;
    flex: 1;
  }

  .sidebar {
    width: 20%;
    padding: 20px;
    background-color: #f0f0f0;
    border-right: 1px solid #ddd;
    display: flex;
    flex-direction: column;
    align-items: center;

    .timer-container {
      display: flex;
      align-items: center;
      margin-bottom: 20px;

      .time {
        font-size: 1.5em;
        margin-right: 20px;
      }

      .submit-button {
        padding: 10px 20px;
        font-size: 1em;
        margin-left: 10px;
        cursor: pointer;
        background-color: #28a745;
        color: #fff;
        border: none;
        border-radius: 5px;
      }
    }

    .section {
      margin-bottom: 20px;

      .section-title {
        font-weight: bold;
        margin-bottom: 10px;
      }

      .question-status-container {
        display: flex;
        flex-wrap: wrap;

        .question-status {
          width: 30px;
          height: 30px;
          line-height: 30px;
          text-align: center;
          margin: 5px;
          cursor: pointer;

          &.done {
            background-color: #4caf50;
            color: white;
          }
          &.not-done {
            background-color: #ddd;
          }
        }
      }
    }
  }

  .content {
    flex: 1;
    padding: 60px;

    h2 {
      margin-bottom: 20px;
    }

    .choice-question {
      .question-content {
        font-size: 1.2em;
        margin-bottom: 20px;
      }

      .options {
        .option {
          display: flex;
          align-items: center;
          margin-bottom: 10px;
          cursor: pointer;

          .circle {
            width: 20px;
            height: 20px;
            border: 2px solid #000;
            border-radius: 50%;
            margin-left: 10px;
          }

          .circle.selected {
            background-color: #3c6bec;
          }
        }
      }
    }

    .fill-blank-question,
    .judge-question {
      .question-content {
        font-size: 1.2em;
        margin-bottom: 20px;
      }

      .input-box {
        width: 100%;
        padding: 8px;
        font-size: 1em;
        border: 1px solid #ddd;
        border-radius: 5px;
      }

      .options {
        .option {
          display: flex;
          align-items: center;
          margin-bottom: 10px;
          cursor: pointer;

          .circle {
            width: 20px;
            height: 20px;
            border: 2px solid #000;
            border-radius: 50%;
            margin-left: 10px;
          }

          .circle.selected {
            background-color: #3c6bec;
          }
        }
      }
    }

    .buttons {
      display: flex;
      justify-content: center;
      margin-top: 100px;

      .navigation-buttons {
        display: flex;
        gap: 10px;

        button {
          padding: 10px 20px;
          font-size: 1em;
          cursor: pointer;
          background-color: #007bff;
          color: #fff;
          border: none;
          border-radius: 5px;
        }
      }
    }
  }
}
</style>
