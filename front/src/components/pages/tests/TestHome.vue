<template>
  <div class="online-test">
    <h1>在线测试</h1>
    
    <div class="block">
      <div class="block-title">科目</div>
      <div class="block-content">
        <!-- 学科 -->
        <div class="subject-section bordered-container">
          <div class="section-title">
            学科
            <input type="text" v-model="subjectSearch" class="text-box bordered" placeholder="搜索学科">
          </div>
          <div class="button-group">
            <button v-for="subject in subjects" :key="subject" @click="openBranchesDialog(subject)" class="bordered">
              {{ subject }}
            </button>
          </div>
        </div>
        <!-- 已选 -->
        <div class="selected-section bordered-container">
          <div class="section-title">
            已选知识点
            <input type="text" v-model="selectedSubjectSearch" class="text-box" placeholder="自定义知识点" @keyup.enter="addSelectedSubject">
          </div>
          <div class="selected-group">
            <div v-if="selectedSubjects.length === 0" class="placeholder">请选择学科知识点</div>
            <div v-for="selectedSubject in selectedSubjects" :key="selectedSubject" class="selected-item">
              {{ selectedSubject }}
              <span class="delete-button" @click="removeSelectedSubject(selectedSubject)">×</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 弹窗组件 -->
    <div v-if="isBranchesDialogOpen" class="dialog">
      <div class="dialog-content">
        <h2 class="dialog-title">选择分支领域<button class="close-button" @click="closeBranchesDialog">X</button></h2>
        <div class="button-group">
          <button v-for="branch in branches" :key="branch" @click="addToSelected(branch)">{{ branch }}</button>
        </div>
      </div>
    </div>
    
    <div class="block">
      <div class="block-title">
        时间(0~120min)
        <input type="number" v-model.number="timeValue" min="0" max="120" step="5" class="input-box">
      </div>
      <div class="block-content">
        <input type="range" min="0" max="120" v-model="timeValue" class="slider" step="5">
      </div>
    </div>
    
    <div class="block">
      <div class="block-title">
        难度(0~10)
        <input type="number" v-model.number="difficultyValue" min="0" max="10" step="1" class="input-box">
      </div>
      <div class="block-content">
        <input type="range" min="0" max="10" v-model="difficultyValue" class="slider" step="1">
      </div>
    </div>
    
    <div class="block">
      <div class="block-title">其他</div>
      <div class="block-content">
        <textarea class="text-input"></textarea>
      </div>
    </div>
    
    <button class="start-button" @click="goTestPage">开始测试</button>
    <button class="back-button" @click="goBack">返回</button>
  </div>
</template>
<script>
export default {
  data() {
    return {
      subjects: ['数学', '语文', '英语', '物理', '化学', '生物', '地理', '历史', '政治'],
      branches: ['分支1', '分支2', '分支3', '分支4', '分支5', '分支6'],
      selectedSubjects: [],
      isBranchesDialogOpen: false,
      timeValue: 60,
      difficultyValue: 5,
      subjectSearch: '',
      selectedSubjectSearch: ''
    };
  },
  methods: {
    addToSelected(subject) {
      if (!this.selectedSubjects.includes(subject)) {
        this.selectedSubjects.push(subject);
      }
    },
    openBranchesDialog(subject) {
      console.log(subject)
      this.isBranchesDialogOpen = true;
    },
    closeBranchesDialog() {
      this.isBranchesDialogOpen = false;
    },
    goBack() {
      this.$router.back();
    },
    goTestPage(){
      console.log("Into goTestPage")
      this.$router.push('/testpage');
    },
    addSelectedSubject() {
      if (this.selectedSubjectSearch && !this.selectedSubjects.includes(this.selectedSubjectSearch)) {
        this.selectedSubjects.push(this.selectedSubjectSearch);
        this.selectedSubjectSearch = '';
      }
    },
    removeSelectedSubject(subject) {
      this.selectedSubjects = this.selectedSubjects.filter(s => s !== subject);
    }
  }
};
</script>
<style scoped>
.online-test {
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

.block {
  margin-bottom: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 10px;
}

.block-title {
  font-weight: bold;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.block-content {
  display: flex;
  align-items: center;
}

.subject-section, .selected-section {
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
  border: 1px solid black; /* 设置边框样式 */
  background-color: transparent; /* 设置背景色为透明 */
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
}

.dialog .dialog-title {
  position: relative;
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
  background-color: #f0f0f0;
  border-radius: 4px;
}

.slider {
  width: 100%;
}

.input-box {
  width: 60px;
  margin-left: 10px;
  text-align: center;
}

.text-box {
  width: 150px;
  margin-left: 10px;
  padding: 5px;
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
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  text-align: center;
}

.start-button:hover {
  background-color: #0056b3;
}

.back-button {
  position: absolute;
  top: 50px;
  right: 50px;
  padding: 8px 16px;
  background-color: #ccc;
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.bordered {
  border: 1px solid black;
  padding: 5px;
  border-radius: 4px;
}

.bordered-container {
  border: 1px solid black;
  padding: 10px;
  border-radius: 8px;
  height: 80px;
}
</style>
