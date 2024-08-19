<template>
  <div class="guide-modal" v-if="guidevisible">
    <div class="guide-modal-content">
      <button class="guide-close-button" @click="guidevisible=false">
        <i class="fas fa-times"></i>
      </button>
      <h3> <i class="fas fa-exclamation-circle"></i> 页面操作指南</h3>
      <textarea type="text" v-model="guidetext" class="guide-text" readonly />
      <slot></slot>
      <button class="guide-action-button" @click="guidevisible=false"><i class="fas fa-check"></i> 确认</button>
    </div>
  </div>
  <div class="online-test">
    <h1><i class="fas fa-pen"></i> 在线测试</h1>
    <button class="openguide-button" @click="guidevisible = true"> <i class="fas fa-exclamation-circle"></i> </button>

    <div class="block">
      <div class="block-title">
        科目
        <i class="fas fa-book"></i>
      </div>
      <div class="block-content flex-container">
        <!-- 学科 -->
        <div class="subject-section bordered-container flex-child">
          <div class="section-title">
            学科
            <input
              type="text"
              v-model="subjectSearch"
              class="text-box bordered"
              placeholder="自定义学科"
              @keyup.enter="addCustomSubject"
            />
          </div>
          <div class="button-group">
            <button
              v-for="subject in subjects"
              :key="subject.name"
              @click="openBranchesDialog(subject)"
              :class="{ selected: subject.name === selectedSubject }"
              class="bordered"
            >
              <i class="fas fa-chevron-right"></i> {{ subject.name }}
            </button>
            <!-- 动态渲染用户输入的学科按钮 -->
            <button
              v-if="customSubject"
              @click="openCustomSubjectDialog"
              :class="{ selected: customSubject === selectedSubject }"
              class="bordered"
            >
              <i class="fas fa-plus"></i> {{ customSubject }}
            </button>
          </div>
        </div>
        <!-- 已选 -->
        <div class="selected-section bordered-container flex-child">
          <div class="section-title">
            已选知识点
            <input
              type="text"
              v-model="knowledgeSearch"
              class="text-box bordered"
              placeholder="自定义知识点"
              @keyup.enter="addCustomKnowledge"
            />
          </div>
          <div class="selected-group">
            <div v-if="selectedSubjects.length === 0 && customKnowledges.length === 0" class="placeholder">
              请选择学科知识点
            </div>
            <button v-if="selectedSubjects.length === 0 && customKnowledges.length === 0" class="custom-subject-button" @click="getRecommendedSubjects">
              <i class="fas fa-lightbulb"></i> AI推荐知识点
            </button>
            <div
              v-for="selectedSubject in selectedSubjects"
              :key="selectedSubject"
              class="selected-item"
            >
              {{ selectedSubject }}
              <span
                class="delete-button"
                @click="removeSelectedSubject(selectedSubject)"
              ><i class="fas fa-times"></i></span>
            </div>
            <div
              v-for="knowledge in customKnowledges"
              :key="knowledge"
              class="selected-item"
            >
              {{ knowledge }}
              <span
                class="delete-button"
                @click="removeCustomKnowledge(knowledge)"
              ><i class="fas fa-times"></i></span>
            </div>
            <button v-if="selectedSubjects.length > 0 || customKnowledges.length > 0" class="custom-subject-button" @click="getRecommendedSubjects">
              <i class="fas fa-lightbulb"></i> AI推荐知识点
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 弹窗组件 -->
    <div v-if="isBranchesDialogOpen" class="dialog">
      <div class="dialog-content">
        <h2 class="dialog-title">
          选择学科知识点
          <button class="close-button" @click="closeBranchesDialog"><i class="fas fa-times"></i></button>
        </h2>
        <div class="button-group">
          <button
            v-for="branch in currentBranches"
            :key="branch"
            @click="addToSelected(branch)"
          >
            <i class="fas fa-check"></i> {{ branch }}
          </button>
        </div>
      </div>
    </div>

    <div class="block">
      <div class="block-title">
        时间 (0~120min)
        <i class="far fa-clock"></i>
      </div>
      <div class="block-content">
        <input
          type="range"
          min="0"
          max="120"
          v-model="timeValue"
          class="slider"
          step="5"
        />
        <input
          type="number"
          v-model.number="timeValue"
          min="0"
          max="120"
          step="5"
          class="input-box"
        />
      </div>
    </div>

    <div class="block">
      <div class="block-title">
        难度 (0~10)
        <i class="fas fa-signal"></i>
      </div>
      <div class="block-content">
        <input
          type="range"
          min="0"
          max="10"
          v-model="difficultyValue"
          class="slider"
          step="1"
        />
        <input
          type="number"
          v-model.number="difficultyValue"
          min="0"
          max="10"
          step="1"
          class="input-box"
        />
      </div>
    </div>

    <div class="block">
      <div class="block-title">
        其他要求
        <i class="fas fa-comment"></i>
      </div>
      <div class="block-content">
        <textarea class="text-input" v-model="otherInput"></textarea>
      </div>
    </div>

    <button class="start-button" @click="goTestPage">
      <i class="fas fa-play"></i> 开始测试
    </button>
    <button class="back-button" @click="goBack">
      <i class="fas fa-arrow-left"></i> 返回
    </button>
  </div>
  
  <div v-if="isRecommendedDialogOpen" class="recdialog">
    <div class="recdialog-content">
      <h2 class="recdialog-title">
        <i class="fas fa-book-open"></i> 推荐知识点
        <button class="recclose-button" @click="closeRecommendedDialog"><i class="fas fa-times"></i></button>
      </h2>
      <div class="recommended-list">
        <div class="recommended-column">
          <label v-for="(subject) in recommendedSubjects" :key="subject" class="recommended-item">
            <input type="checkbox" v-model="selectedRecommendedSubjects" :value="subject">
            {{ subject }}
          </label>
        </div>
      </div>
      <button @click="addSelectedRecommendedSubjects" class="recfinish-selection-button">
        <i class="fas fa-check"></i> 完成知识点选择
      </button>
    </div>
  </div>

  <!-- 加载中弹窗 -->
  <div v-if="loading" class="loading-dialog">
    <div class="loading-content">
      <h2><i class="fas fa-spinner fa-spin"></i> 题目生成中，请稍等...</h2>
    </div>
  </div>
</template>


<script>
import axios from 'axios';
import { openDB } from 'idb';

export default {
  data() {
    return {
      subjects: [
        {
          name: '数学',
          branches: ['代数', '几何', '微积分', '概率', '统计', '离散数学'],
        },
        {
          name: '计算机',
          branches: ['编程基础', '数据结构', '算法', '操作系统', '数据库', '计算机网络'],
        },
        {
          name: '物理',
          branches: ['力学', '电磁学', '热学', '光学', '量子物理', '相对论'],
        },
        {
          name: '化学',
          branches: ['有机化学', '无机化学', '物理化学', '分析化学', '生物化学', '环境化学'],
        },
        {
          name: '生物',
          branches: ['细胞生物学', '遗传学', '生态学', '进化生物学', '分子生物学', '生物化学'],
        },
        {
          name: '地理',
          branches: ['自然地理', '人文地理', '经济地理', '地质学', '气象学', '环境科学'],
        },
        {
          name: '历史',
          branches: ['中国历史', '世界历史', '古代史', '近现代史', '史学理论', '考古学'],
        },
      ],
      selectedSubjects: [],
      isBranchesDialogOpen: false,
      isRecommendedDialogOpen: false,
      timeValue: 60,
      difficultyValue: 5,
      subjectSearch: '',
      selectedSubjectSearch: '',
      customSubject: '',
      currentBranches: [],
      selectedSubject: '',
      recommendedSubjects: [],
      selectedRecommendedSubjects: [],
      otherInput: '无',
      loading: false,
      isCustomKnowledgeDialogOpen: false,
      knowledgeSearch: '',
      customKnowledge: '',
      customKnowledges: [],
      guidetext: "1. 用户可以选择默认的学科，也可以自定义学科作为考试的主题\n\n2. 在用户选定学科后，可以在右侧“已选知识点”框中选择更加精细的知识点\n\n3. 用户自定义考试的时间以及难度\n\n4. 用户输入对题目的特殊要求（可以是特殊知识点，特殊题型要求等）",
      guidevisible:false,
    };
  },
  methods: {
    addCustomKnowledge() {
      if (this.knowledgeSearch && !this.customKnowledges.includes(this.knowledgeSearch)) {
        this.customKnowledges.push(this.knowledgeSearch);
        this.knowledgeSearch = '';
      }
    },
    removeCustomKnowledge(knowledge) {
      this.customKnowledges = this.customKnowledges.filter(k => k !== knowledge);
    },
    addToSelected(branch) {
      if (!this.selectedSubjects.includes(branch)) {
        this.selectedSubjects.push(branch);
      }
    },
    openBranchesDialog(subject) {
      if (this.selectedSubjects.length > 0 && this.selectedSubject !== subject.name) {
        this.selectedSubjects = [];
      }
      this.currentBranches = subject.branches;
      this.isBranchesDialogOpen = true;
      this.selectedSubject = subject.name;
    },
    closeBranchesDialog() {
      this.isBranchesDialogOpen = false;
    },
    goBack() {
      this.$router.back();
    },
    addSelectedSubject() {
      if (this.selectedSubjectSearch && !this.selectedSubjects.includes(this.selectedSubjectSearch)) {
        this.selectedSubjects.push(this.selectedSubjectSearch);
        this.selectedSubjectSearch = '';
      }
    },
    removeSelectedSubject(subject) {
      this.selectedSubjects = this.selectedSubjects.filter((s) => s !== subject);
    },
    addCustomSubject() {
      this.customSubject = this.subjectSearch;
      this.selectedSubject = this.customSubject;
      this.subjectSearch = '';
    },
    closeRecommendedDialog() {
      this.isRecommendedDialogOpen = false;
    },
    async getRecommendedSubjects() {
      try {
        const response = await axios.post('/get_subjects', {
          parent_subjects: [this.selectedSubject],
          already_subjects: this.selectedSubjects,
        });
        this.recommendedSubjects = response.data.subjects;
        this.isRecommendedDialogOpen = true;
      } catch (error) {
        console.error('Error fetching recommended subjects:', error);
      }
    },
    addSelectedRecommendedSubjects() {
      this.selectedSubjects = this.selectedSubjects.concat(this.selectedRecommendedSubjects);
      this.isRecommendedDialogOpen = false;
      this.selectedRecommendedSubjects = [];
    },
    async openCustomSubjectDialog() {
      try {
        const response = await axios.post('/get_subjects', {
          parent_subjects: [this.customSubject],
          already_subjects: this.selectedSubjects,
        });
        this.currentBranches = response.data.subjects;
        this.isBranchesDialogOpen = true;
        this.selectedSubject = this.customSubject;
      } catch (error) {
        console.error('Error fetching custom branches:', error);
      }
    },
    async storeProblems(problems) {
      const db = await openDB('problemsDB', 1, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('single_choice_problems')) {
            db.createObjectStore('single_choice_problems', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('judgement_problems')) {
            db.createObjectStore('judgement_problems', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('fillin_problems')) {
            db.createObjectStore('fillin_problems', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('evaluation')) {
            console.log("create evaluation")
            db.createObjectStore('evaluation', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('dimension')) {
            db.createObjectStore('dimension', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('score')) {
            db.createObjectStore('score', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('shortcoming')) {
            db.createObjectStore('shortcoming', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('suggestion')) {
            console.log("create suggestion")
            db.createObjectStore('suggestion', { keyPath: 'id', autoIncrement: true });
          }
          if (!db.objectStoreNames.contains('subjects')) {
            db.createObjectStore('subjects', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
          if (!db.objectStoreNames.contains('knowledge_points')) {
            db.createObjectStore('knowledge_points', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
        },
      });

      // 开始新的事务，先清空所有存储的数据
      const tx = db.transaction(['single_choice_problems', 'judgement_problems', 'fillin_problems','subjects','knowledge_points'], 'readwrite');
      await Promise.all([
        tx.objectStore('single_choice_problems').clear(),
        tx.objectStore('judgement_problems').clear(),
        tx.objectStore('fillin_problems').clear(),
        tx.objectStore('subjects').clear(),
        tx.objectStore('knowledge_points').clear(),
      ]);
      await tx.done;

      // 重新创建数据库，确保ID从1开始
      const txNew = db.transaction(['single_choice_problems', 'judgement_problems', 'fillin_problems'], 'readwrite');
      let singleChoiceId = 1;
      let judgementId = 1;
      let fillinId = 1;

      problems.forEach((problem) => {
        const problemWithDoneanswer = { ...problem, doneanswer: '' };
        if (problem.type === 'single_choice') {
          txNew.objectStore('single_choice_problems').put({ ...problemWithDoneanswer, id: singleChoiceId++ });
        } else if (problem.type === 'judgement') {
          txNew.objectStore('judgement_problems').put({ ...problemWithDoneanswer, id: judgementId++ });
        } else if (problem.type === 'fillin') {
          txNew.objectStore('fillin_problems').put({ ...problemWithDoneanswer, id: fillinId++ });
        }
      });
      await txNew.done;
      const txSubjects = db.transaction(['subjects', 'knowledge_points'], 'readwrite');
      console.log('学科：',this.selectedSubject)
      console.log('this.selectedSubjects:',this.selectedSubjects)
      let selectedsubject = [this.selectedSubject]
      selectedsubject.forEach((subject) => {
        txSubjects.objectStore('subjects').put({ name: subject });
      });
      this.selectedSubjects.forEach((knowledge) => {
        txSubjects.objectStore('knowledge_points').put({ name: knowledge });
      });
      await txSubjects.done;
    },
    async goTestPage() {
      this.loading = true;
      try {
        const time = parseInt(this.timeValue, 10);
        const difficultyValue  = parseInt(this.difficultyValue, 10);
        const response = await axios.post('/get_problems', {
            subjects: this.selectedSubjects,
            time: time,
            min_difficulty: difficultyValue,
            max_difficulty: difficultyValue,
            type: ['single_choice', 'judgement', 'fillin'],
            others: this.otherInput,
          }).then((response) => {
            return response;
          });
        const data = response.data;
        await this.storeProblems(data.problems);
      } catch (error) {
        console.error('Error starting test:', error);
      } finally {
        this.loading = false;
        this.$router.push('/testpage');
      }
    },
  },
};
</script>
<style scoped>
.online-test {
  padding: 20px;
  /* background-color: #d0eefe; */
  color: #333;
  background-image: url('../../../assets/PPTbackground.jpg'); /* 背景图片的路径 */
  background-size: cover; /* 让背景图片充满容器 */
  background-position: center; /* 居中显示背景图片 */
  background-repeat: no-repeat; /* 禁止背景图片重复 */
}

h1 {
  text-align: center;
  margin-bottom: 20px;
  color:rgb(171, 238, 253);
}

.openguide-button {
  text-align: center;
  justify-self: center;
  padding: 0.5rem;
  display: inline-block; 
  vertical-align: middle;
  background-color: transparent;
  color:rgb(171, 238, 253);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  position: absolute; 
  font-weight: bold;
  font-size: 1.5em;
  top:50px;
  right:140px;
}
.openguide-button:hover {
  color:rgb(27, 193, 230);
}
.block {
  margin-bottom: 11px;
  /* border: 1px solid #ccc; */
  border-radius: 8px;
  padding: 10px;
  /* background-color: #fff; */
  background-color: rgba(164, 230, 247, 0.8);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.block-title {
  font-weight: bold;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #030bed;
  font-size: 1.2em;
  font-weight: bold;
}

.block-content {
  display: flex;
  align-items: center;
}

.subject-section,
.selected-section {
  flex: 1;
  margin-right: 10px;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-weight: bold;
  margin-bottom: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #007bff;
}

.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  height: 100%;
  width: 90%;
}

.button-group button {
  position: relative;
  padding-right: 20px; /* 增加右侧内边距给小圆圈留空间 */
  background-color: #1a86df;
  color: #fefefe;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
  font-weight: bold;
}

.button-group button:hover {
  background-color: #2da1fa;
  color: #fff;
}

.button-group button::after {
  content: "";
  position: absolute;
  top: 50%;
  right: 5px; /* 调整圆圈与按钮的距离 */
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1px solid #f9f7f7; /* 设置边框样式 */
  background-color: transparent; /* 设置背景色为透明 */
}

.selected {
  background-color: #28a745 !important; /* Green color when selected */
  color: white !important; /* White text color when selected */
}

.selected::after {
  background-color: white !important; /* White color for the circle when selected */
}

.selected-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.selected-item {
  padding: 8px 16px;
  background-color: #28a745;
  color: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.delete-button {
  margin-left: 10px;
  cursor: pointer;
  font-weight: bold;
}

.dialog {
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

.dialog-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dialog .dialog-title {
  position: relative;
  color: #007bff;
}

.dialog button.close-button {
  position: absolute;
  top: 1px;
  right: 1px;
  padding: 5px 10px;
  background-color: #ccc;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.dialog button {
  margin: 5px;
}

.placeholder {
  padding: 8px 16px;
  background-color: #f5f5f5;
  border-radius: 4px;
  color: #606060;
}

.slider {
  width: 100%;
}

.input-box {
  width: 60px;
  margin-left: 10px;
  text-align: center;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 5px;
}

.text-box {
  width: 20%;
  padding: 8px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.text-input {
  width: 100%;
  height: 100px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: none;
}

.start-button {
  display: block;
  margin: 0 auto;
  padding: 10px 20px;
  background-color: rgb(27, 193, 230);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  text-align: center;
  font-size:1.2em;
  font-weight:bold;
}

.start-button:hover {
  background-color: rgb(3, 184, 224);
}

.back-button {
  position: absolute;
  top: 50px;
  right: 50px;
  padding: 8px 16px;
  /* background-color: #007bff; */
  background-color:rgb(171, 238, 253);
  color: #077fd4;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.0em;
  font-weight: bold;
}
.back-button:hover{
  background-color:rgb(39, 204, 241);
}

.bordered {
  border: 1px solid #ccc;
  padding: 5px;
  border-radius: 4px;
}

.bordered-container {
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 8px;
  background-color: #e3fbfd;
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

.dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-title {
  font-size: 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  color: #007bff;
}

.text-box {
  width: 20%;
  padding: 8px;
  margin-top: 5px;
}

.finish-selection-button {
  margin-top: 20px;
  padding: 10px 20px;
  background: #007bff;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.close-button {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 20px;
}

.flex-container {
  display: flex;
  align-items: stretch;
}

.flex-child {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.custom-subject-button {
  background-color: #ff9800;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
  padding: 8px 16px;
  font-weight: bold;
  letter-spacing: 0.8px; 
}

.custom-subject-button:hover {
  background-color: #e68900;
  color: #fff;
  font-weight: bold;
}

.recdialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  padding: 20px;
  width: 400px;
  background: linear-gradient(45deg, #4A90E2, #50E3C2, #9013FE);
  background-size: 300% 300%;
  animation: gradientAnimation 6s ease infinite;
}

@keyframes gradientAnimation {
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

.recdialog-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.recdialog-title {
  color:#2d0398;
  font-size: 1.6em;
  font-weight: bold;
  text-align: center;
  margin-bottom: 20px;
  position: relative;
  width: 100%;
}

.recclose-button {
  position: absolute;
  top: 0;
  right: 0;
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.recommended-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.recommended-column {
  display: flex;
  flex-direction: column;
}

.recommended-item {
  margin: 10px 0;
  font-size: 1.4em;
  font-weight: bold;
  color: #2d0398;
}

.recfinish-selection-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.recfinish-selection-button:hover {
  background-color: #45a049;
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
  width: 80%;
  max-width: 500px;
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
  text-align: center;
  margin: 0;
  color:#007bff;
  font-size: 1.5em;
}
</style>