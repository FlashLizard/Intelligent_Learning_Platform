<template>
  <div class="sidebar-menu">
    <div class="app-title"><i class="fas fa-school"></i> 讯飞智教</div>
    <ul>
      
      <!-- 教师应用 -->
      <li>
        <div @click="toggleMenu('teacherApplication')">
          <i class="fas fa-chalkboard-teacher"></i> 教师应用
        </div>
        <ul v-if="isActiveMenu('teacherApplication')" class="submenu">
          <li>
            <div @click="toggleMenu('teachingAssistant')">
              <i :class="isActiveMenu('teachingAssistant') ? 'fas fa-chevron-down' : 'fas fa-chevron-right'"></i> 教学助手
            </div>
            <ul v-if="isActiveMenu('teachingAssistant')" class="submenu">
              <li @click="navigate('/coursehelper')"><i class="fas fa-chalkboard"></i> 随堂助手</li>
              <li @click="navigate('/homeworkmanagement')"><i class="fas fa-check-circle"></i> 背诵批改</li>
              <li @click="navigate('/pptgenerator')"><i class="fas fa-file-powerpoint"></i> PPT生成</li>
            </ul>
          </li>
          <li>
            <div @click="toggleMenu('rapidPreparation')">
              <i :class="isActiveMenu('rapidPreparation') ? 'fas fa-chevron-down' : 'fas fa-chevron-right'"></i> 迅捷备课
            </div>
            <ul v-if="isActiveMenu('rapidPreparation')" class="submenu">
              <li @click="navigate('/teacherrecording')"><i class="fas fa-book-open"></i> 教师备课</li>
              <li @click="navigate('/paperdownload')"><i class="fas fa-file-alt"></i> 智教出卷</li>
              <li @click="navigate('/docclassify')"><i class="fas fa-book-open"></i> 文档归类</li>
            </ul>
          </li>
          <li>
            <div @click="toggleMenu('smartQandA')">
              <i :class="isActiveMenu('smartQandA') ? 'fas fa-chevron-down' : 'fas fa-chevron-right'"></i> 智能问答
            </div>
            <ul v-if="isActiveMenu('smartQandA')" class="submenu">
              <li @click="navigate('/translationpage')"><i class="fas fa-language"></i> 即时翻译</li>
              <li @click="navigate('/aiqa')"><i class="fas fa-info-circle"></i> 问答咨询</li>
            </ul>
          </li>
        </ul>
      </li>

      <!-- 学生应用 -->
      <li>
        <div @click="toggleMenu('studentApplication')">
          <i class="fas fa-user-graduate"></i>学生应用
        </div>
        <ul v-if="isActiveMenu('studentApplication')" class="submenu">
          <li>
            <div @click="toggleMenu('onlineSelfTest')">
              <i :class="isActiveMenu('onlineSelfTest') ? 'fas fa-chevron-down' : 'fas fa-chevron-right'"></i> 在线自测
            </div>
            <ul v-if="isActiveMenu('onlineSelfTest')" class="submenu">
              <li @click="navigate('/testhome')"><i class="fas fa-play-circle"></i> 开始测试</li>
              <li @click="navigate('/testhistory')"><i class="fas fa-history"></i> 测试历史</li>
            </ul>
          </li>
          <li>
            <div @click="toggleMenu('smartResources')">
              <i :class="isActiveMenu('smartResources') ? 'fas fa-chevron-down' : 'fas fa-chevron-right'"></i> 智学资源
            </div>
            <ul v-if="isActiveMenu('smartResources')" class="submenu">
              <li @click="navigate('/classselect')"><i class="fas fa-globe"></i> 环球网课</li>
              <li @click="navigate('/paperdownload')"><i class="fas fa-file-alt"></i> 量身密卷</li>
            </ul>
          </li>
          <li>
            <div @click="toggleMenu('smartQandAStudent')">
              <i :class="isActiveMenu('smartQandAStudent') ? 'fas fa-chevron-down' : 'fas fa-chevron-right'"></i> 智能问答
            </div>
            <ul v-if="isActiveMenu('smartQandAStudent')" class="submenu">
              <li @click="navigate('/translationpage')"><i class="fas fa-language"></i> 即时翻译</li>
              <li @click="navigate('/aiqa')"><i class="fas fa-question-circle"></i> 智教解惑</li>
            </ul>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      activeMenus: ['teacherApplication', 'studentApplication'], // 初始展开的菜单项
    };
  },
  methods: {
    navigate(route) {
      this.$router.push(route);
    },
    toggleMenu(menu) {
      if (this.isActiveMenu(menu)) {
        this.activeMenus = this.activeMenus.filter(item => item !== menu); // Close the menu if it's already open
      } else {
        this.activeMenus.push(menu); // Open the clicked menu
      }
    },
    isActiveMenu(menu) {
      return this.activeMenus.includes(menu);
    },
  },
};
</script>

<style scoped lang="scss">
.sidebar-menu {
  width: 250px;
  background-color: #2c3e50;
  color: #ecf0f1;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  font-family: 'Arial, sans-serif';

  .app-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 20px;
    text-align: center;
    color: #ecf0f1;
  }

  ul {
    list-style-type: none;
    padding: 0;

    li {
      padding: 10px 15px;
      margin: 5px 0;
      cursor: pointer;
      background-color: #34495e;
      border-radius: 5px;
      transition: background-color 0.3s, color 0.3s, transform 0.3s;
      position: relative;

      &:hover {
        background-color: #3498db;
        color: #fff;
        transform: translateY(-2px);
      }

      .submenu {
        margin-top: 10px;

        li {
          background-color: #2980b9;
          border-radius: 5px;

          &:hover {
            background-color: #3498db;
          }
        }
      }
    }
  }
}
</style>