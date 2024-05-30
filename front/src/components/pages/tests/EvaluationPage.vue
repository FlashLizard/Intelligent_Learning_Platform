<template>
    <div class="evaluation-page">
      <header>
        <h1>测试评估</h1>
        <button @click="goBack">返回</button>
      </header>
      <div class="content">
        <div class="left-panel">
          <div class="evaluation-section">
            <h2>评价</h2>
            <textarea placeholder="请输入评价内容"></textarea>
          </div>
          <div class="evaluation-section">
            <h2>不足</h2>
            <textarea placeholder="请输入不足内容"></textarea>
          </div>
          <div class="evaluation-section">
            <h2>建议</h2>
            <textarea placeholder="请输入建议内容"></textarea>
          </div>
        </div>
        <div class="right-panel">
          <hexagon-chart :data="userAbilities"></hexagon-chart>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import HexagonChart from '../../component/HexagonChart.vue';
  
  export default {
    components: {
      HexagonChart,
    },
    data() {
      return {
        userAbilities: [80, 70, 60, 100, 50, 85],
      };
    },
    methods: {
      goBack() {
        this.$router.back();
      },
    },
  };
  </script>
  
  <style lang="scss">
  .evaluation-page {
    padding: 20px;

    header {
      display: flex;
      justify-content: center;
      align-items: center;
      position: relative; // 添加相对定位

      h1 {
        margin: 0;
        flex: 1;
        text-align: center; // 居中对齐文本
      }

      button {
        padding: 5px 10px;
        cursor: pointer;
        position: absolute; // 绝对定位按钮
        right: 0; // 靠右对齐
      }
    }

    .content {
      display: flex;
      margin-top: 20px;
      height: 100%;

      .left-panel {
        border: 1px solid black;
        padding: 10px;
        width: 50%;
        margin-top: 40px;
        height: 90%;
        .evaluation-section {
          margin-bottom: 20px;

          h2 {
            margin-bottom: 5px;
          }

          textarea {
            width: 100%;
            height: 100px;
          }
        }
      }

      .right-panel {
        width: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
      }
    }
  }
  </style>
  