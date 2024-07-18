<template>
  <div class="home">
    <!-- Sidebar Menu -->
    <SidebarMenu />

    <div class="main-content">
      <!-- Page Title -->
      <div class="page-title">
        <h1>讯飞智教</h1>
      </div>

      <!-- Application Switch Tabs -->
      <div class="switch-tabs">
        <div class="tab" :class="{ active: activeTab === 'teacher' }" @click="switchTab('teacher')">教师应用</div>
        <div class="tab" :class="{ active: activeTab === 'student' }" @click="switchTab('student')">学生应用</div>
      </div>

      <!-- Teacher Application Section -->
      <div v-if="activeTab === 'teacher'">
        <!-- Top Section: Teacher Assistant -->
        <div class="top-section">
          <h2 class="section-title">教学助手</h2>
          <div class="button-container">
            <div class="button" @click="handleClick('/coursehelper')">
              <i class="fas fa-book-open"></i>
              <h3 class="button-title">随堂助手</h3>
              <p class="button-description">记录教师的课程信息，方便管理和回顾。</p>
            </div>
            <div class="button" @click="handleClick('/homeworkmanagement')">
              <i class="fas fa-tasks"></i>
              <h3 class="button-title">背诵批改</h3>
              <p class="button-description">管理学生的背诵作业，包括布置、查看和反馈。</p>
            </div>
            <div class="button" @click="handleClick('/pptgenerator')">
              <i class="fas fa-chalkboard-teacher"></i>
              <h3 class="button-title">PPT生成</h3>
              <p class="button-description">创建和编辑教学用的幻灯片，简化制作过程。</p>
            </div>
          </div>
        </div>

        <!-- Middle Section: Intelligent Q&A -->
        <div class="middle-section">
          <h2 class="section-title">迅捷备课</h2>
          <div class="button-container">
            <div class="button" @click="handleClick('/teacherrecording')">
              <i class="fas fa-video"></i>
              <h3 class="button-title">教师备课</h3>
              <p class="button-description">帮助教师轻松备课的AI助手。</p>
            </div>
            <!-- 新增的试卷下载按钮 -->
            <div class="button" @click="handleClick('/paperdownload')">
              <i class="fas fa-download"></i>
              <h3 class="button-title">智教出卷</h3>
              <p class="button-description">讯飞智教根据教学需求快速出卷。</p>
            </div>
          </div>
        </div>

        <!-- Course Management Section -->
        <div class="course-management-section">
          <h2 class="section-title">智教问答</h2>
          <div class="button-container">
            <div class="button" @click="handleClick('/translationpage')">
              <i class="fas fa-user-astronaut"></i>
              <h3 class="button-title">即时翻译</h3>
              <p class="button-description">讯飞智教随时为您提供翻译功能。</p>
            </div>
            <div class="button" @click="handleClick('/aiqa')">
              <i class="fas fa-comments"></i>
              <h3 class="button-title">问答咨询</h3>
              <p class="button-description">获取教育相关的咨询和建议。</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Student Application Section -->
      <div v-if="activeTab === 'student'">
        <!-- Bottom Section: Online Testing -->
        <div class="bottom-section">
          <h2 class="section-title">在线自测</h2>
          <div class="button-container">
            <button class="button" @click="startTest" title="进入选择不同测试">
              <i class="fas fa-pencil-alt"></i>
              <h3 class="button-title">开始测试</h3>
              <p class="button-description">选择不同的测试要求以开始测试。</p>
            </button>
            <button class="button" @click="viewHistory" title="回顾最近的测试情况">
              <i class="fas fa-history"></i>
              <h3 class="button-title">测试历史</h3>
              <p class="button-description">查看在线测试的测试历史与结果。</p>
            </button>
          </div>
        </div>

        <!-- Middle Section: Intelligent Q&A -->
        <div class="middle-section">
          <h2 class="section-title">智能问答</h2>
          <div class="button-container">
            <div class="button" @click="handleClick('/translationpage')">
              <i class="fas fa-user-astronaut"></i>
              <h3 class="button-title">即时翻译</h3>
              <p class="button-description">讯飞智教随时为您提供翻译功能。</p>
            </div>
            <div class="button" @click="handleClick('/aiqa')">
              <i class="fas fa-comments"></i>
              <h3 class="button-title">智教解惑</h3>
              <p class="button-description">讯飞智教为学生答疑解惑。</p>
            </div>
          </div>
        </div>

        <!-- Course Learning Section -->
        <!-- Course Learning Section -->
        <div class="course-learning-section">
          <h2 class="section-title">智学资源</h2>
          <div class="button-container">
            <div class="button" @click="handleClick('/classselect')">
              <i class="fas fa-play-circle"></i>
              <h3 class="button-title">环球网课</h3>
              <p class="button-description">讯飞智教环球检索符合用户需求的网课。</p>
            </div>
            <!-- 新增的试卷下载按钮 -->
            <div class="button" @click="handleClick('/paperdownload')">
              <i class="fas fa-download"></i>
              <h3 class="button-title">量身密卷</h3>
              <p class="button-description">讯飞智教生成符合学生需求的试卷以供练习。</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Logout Button -->
      <div class="top-right">
        <button class="logout-button" @click="logout">
          <i class="fas fa-sign-out-alt"></i><span>退出登录</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import SidebarMenu from '../../component/SidebarMenu.vue';

export default {
  name: 'TeacherManagement',
  components: {
    SidebarMenu
  },
  data() {
    return {
      activeTab: 'teacher' // 默认显示教师应用内容
    };
  },
  methods: {
    handleClick(buttonroute) {
      this.$router.push(buttonroute);
      console.log(`go to ${buttonroute}`);
    },
    startTest() {
      this.$router.push('/testhome');
    },
    viewHistory() {
      this.$router.push('/testhistory');
    },
    logout() {
      this.$router.back();
    },
    switchTab(tab) {
      this.activeTab = tab;
    }
  }
};
</script>

<style scoped lang="scss">
/* Styles for Home Component */
.home {
  display: flex;
  position: relative;
  text-align: center;
  padding: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  color: #333;
  font-family: 'Arial, sans-serif';

  .main-content {
    flex: 1;
    margin-left: 20px; /* Adjust this value based on the sidebar width */
  }

  .page-title {
    margin-top: 5px;
    margin-bottom: 20px;

    h1 {
      font-size: 2.5rem;
      color: #333;
      margin: 0;
    }
  }

  .switch-tabs {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
    border-radius: 10px;
    background-color: #5aa0e6; /* 调整背景颜色变深 */
    overflow: hidden;
    width: 60%; /* 缩短水平宽度 */
    margin: 0 auto 20px; /* 水平居中 */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);

    .tab {
      flex: 1;
      padding: 10px 0;
      font-size: 1.2rem;
      cursor: pointer;
      text-align: center;
      transition: background-color 0.3s, color 0.3s;
      color: #fff; /* 文字颜色变白 */

      &.active {
        background-color: #1a75d2; /* 选中颜色变深 */
        font-weight: bold;
      }

      &:hover:not(.active) {
        background-color: #3b8edb; /* 未选中颜色变深 */
      }
    }
  }

  .top-section,
  .middle-section,
  .bottom-section,
  .course-management-section,
  .course-learning-section {
    margin-bottom: 20px;
    padding: 20px;
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
  }

  .section-title {
    font-size: 2rem;
    margin-bottom: 20px;
    margin-top: 3px;
    color: #555;
  }

  .button-container {
    display: flex;
    justify-content: center;
    gap: 20px;
  }

  .button {
    flex: 1;
    padding: 20px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s, color 0.3s, transform 0.3s;
    background: #1a8dec;
    color: #fff;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    
    &:hover {
      background: #584eec;
      transform: translateY(-5px);
    }

    i {
      font-size: 2rem;
    }

    h3 {
      display: flex;
      align-items: center;
      font-size: 1.4rem;
      margin-bottom: 10px;

      i {
        margin-right: 8px;
      }
    }

    p {
      font-size: 1rem;
      margin-top: 10px;
    }
  }

  .top-right {
    position: absolute;
    top: 30px;
    right: 20px;
  }

  .logout-button {
    display: flex;
    align-items: center;
    padding: 10px 20px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.3s, transform 0.3s;
    background: #3778e0;
    color: #fff;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);

    &:hover {
      background: #584eec;
      transform: translateY(-5px);
    }

    i {
      margin-right: 8px;
    }

    span {
      margin-left: 8px;
    }
  }
}
</style>
