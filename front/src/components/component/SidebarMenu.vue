<template>
    <div class="sidebar-menu">
      <div class="app-title">智慧书苑</div>
      <ul>
        <li @click="toggleMenu('home')">首页</li>
        
        <li>
          <div @click="toggleMenu('teacherAssistant')">教师助手</div>
          <ul v-if="isActiveMenu('teacherAssistant')" class="submenu">
            <li @click="navigate('/pptgenerator')">PPT生成</li>
            <li @click="navigate('/homeworkmanagement')">作业管理</li>
          </ul>
        </li>
  
        <li>
          <div @click="toggleMenu('intelligentQA')">智能问答</div>
          <ul v-if="isActiveMenu('intelligentQA')" class="submenu">
            <li @click="navigate('/virtualperson')">虚拟人</li>
            <li @click="navigate('/educationalconsulting')">教育咨询</li>
          </ul>
        </li>
  
        <li>
          <div @click="toggleMenu('onlineTesting')">在线测试</div>
          <ul v-if="isActiveMenu('onlineTesting')" class="submenu">
            <li @click="navigate('/testhome')">开始测试</li>
            <li @click="navigate('/evaluationpage')">测试历史</li>
          </ul>
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        activeMenus: [], // Track active menus
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
    width: 200px;
    background-color: #1a8dec;
    color: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    font-family: 'Arial, sans-serif';
  
    .app-title {
      font-size: 1.5rem;
      font-weight: bold;
      margin-bottom: 20px;
      text-align: center;
      color: #fff;
    }
  
    ul {
      list-style-type: none;
      padding: 0;
  
      li {
        padding: 10px 15px;
        margin: 5px 0;
        cursor: pointer;
        background-color: #2a9df4;
        border-radius: 5px;
        transition: background-color 0.3s, color 0.3s, transform 0.3s;
        position: relative;
  
        &:hover {
          background-color: #0056b3;
          color: #fff;
          transform: translateY(-2px);
        }
  
        .submenu {
          margin-top: 10px;
  
          li {
            background-color: #4fa3f7;
            border-radius: 5px; /* Added border-radius */
  
            &:hover {
              background-color: #0056b3;
            }
          }
        }
      }
    }
  }
  </style>
  