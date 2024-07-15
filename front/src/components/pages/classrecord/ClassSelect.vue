<template>
  <div class="course-selection" @click="hideDropdown">
    <header class="header">
      <h1>AI荐课</h1>
      <div class="tabs">
        <div
          v-for="tab in tabs"
          :key="tab"
          :class="['tab', { active: tab === selectedTab }]"
          @click="selectTab(tab)"
        >
          <i class="fas fa-book"></i> {{ tab }}
        </div>
        <div
          class="tab"
          @mouseenter="showMoreMenu"
          @mouseleave="hideMoreMenu"
        >
          <i class="fas fa-ellipsis-h"></i> 更多
          <div class="more-menu" v-if="isMoreMenuVisible" @click.stop>
            <div class="more-items">
              <div v-for="(item, index) in moreTabs" :key="index" class="more-item" @click="selectTab(item)">
                <i class="fas fa-book-open"></i> {{ item }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="search-and-back">
        <input type="text" placeholder="搜索学科" v-model="searchQuery" @input="filterCourses" @keyup.enter="handleEnter" />
        <input type="text" class="keyword-input" placeholder="搜索关键词" v-model="keywordQuery" @keyup.enter="handleEnter" />
        <button class="back-button" @click="goBack">
          <i class="fas fa-arrow-left"></i> 返回
        </button>
      </div>
    </header>

    <!-- 加载中弹窗 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-message">
        <i class="fas fa-spinner fa-spin"></i> 课程加载中...
      </div>
    </div>
    <div class="recommendations">
      <h2>推荐课程</h2>
      <!-- 这里是推荐课程列表的渲染 -->
      <div v-for="(course, index) in recommendations" :key="index" class="recommended-course" @click="openUrl(course.url)">
        <div class="recommended-content">
          <p><strong><i class="fas fa-chalkboard"></i> 课程名称:</strong> {{ course.course }}</p>
          <p><strong><i class="fas fa-info-circle"></i> 课程简介:</strong> {{ course.content }}</p>
          <p><strong><i class="fas fa-star"></i> 课程评价:</strong> {{ course.star }}</p>
          <p><strong><i class="fas fa-video"></i> 观看课程:</strong> <a :href="course.url" target="_blank">{{ course.url }}</a></p>
        </div>
      </div>
    </div>

    <!-- 新增：首次进入页面时弹出的提示弹窗 -->
    <div v-if="showWelcomePopup" class="welcome-popup-overlay" @click="showWelcomePopup = false">
      <div class="welcome-popup" @click.stop>
        <h3>欢迎使用AI荐课</h3>
        <p>AI荐课功能根据您指定的学科、关键词为您推荐各大平台上的课程，您可以通过本应用推荐的路径找到您感兴趣的课程。</p>
        <button @click="showWelcomePopup = false">我知道了</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      searchQuery: '',
      selectedTab: '数学',
      tabs: ['数学', '英语', '计算机', '化学', '物理', '历史'],
      moreTabs: ['文学', '医学', '生物'],
      courses: [],
      filteredCourses: [],
      recommendations: [{'url': 'https://www.coursera.org/learn/complex-analysis', 'course': 'Introduction to Complex Analysis free Course by Wesleyan University', 'star': '4.8 stars', 'content': 'by 1K reviews,  provide skills Algebra,  Calculus,  Mathematical Theory & Analysis etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/basicmathematics', 'course': 'Basic Mathematics free Course by Birla Institute of Technology & Science', 'star': 'Pilani', 'content': '4.1 stars,  by 38 reviews,  provide skills Differential Equations,  Mathematics etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/logic-introduction', 'course': 'Introduction to Logic free Course by Stanford University', 'star': '4.4 stars', 'content': 'by 627 reviews,  provide skills Computational Logic,  Mathematics,  Problem Solving etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/mathematics-for-machine-learning-and-data-science', 'course': 'Mathematics for Machine Learning and Data Science Specialization by DeepLearning.AI', 'star': '4.6 stars', 'content': 'by 2K reviews,  provide skills Machine Learning,  Calculus,  Differential Equations etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/mathematical-thinking', 'course': 'Introduction to Mathematical Thinking free Course by Stanford University', 'star': '4.8 stars', 'content': 'by 2.7K reviews,  provide skills Critical Thinking,  Mathematical Theory & Analysis,  Mathematics etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/mathematics-engineers', 'course': 'Mathematics for Engineers Specialization by The Hong Kong University of Science and Technology', 'star': '4.8 stars', 'content': 'by 7.1K reviews,  provide skills Mathematics,  Calculus,  Linear Algebra etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/specializations/algebra-elementary-to-advanced', 'course': 'Algebra: Elementary to Advanced Specialization by Johns Hopkins University', 'star': '4.8 stars', 'content': 'by 561 reviews,  provide skills Algebra,  Mathematics,  Problem Solving etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/introduction-to-calculus', 'course': 'Introduction to Calculus free Course by The University of Sydney', 'star': '4.8 stars', 'content': 'by 3.6K reviews,  provide skills Algebra,  Calculus,  Mathematical Theory & Analysis etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/stanford-statistics', 'course': 'Introduction to Statistics free Course by Stanford University', 'star': '4.6 stars', 'content': 'by 3.1K reviews,  provide skills General Statistics,  Probability & Statistics,  Statistical Analysis etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/mathematics-machine-learning', 'course': 'Mathematics for Machine Learning Specialization by Imperial College London', 'star': '4.6 stars', 'content': 'by 14K reviews,  provide skills Algebra,  Linear Algebra,  Mathematics etc... Beginner level 3 - 6 Months'}],  
      isMoreMenuVisible: false,
      currentPage: 1,
      itemsPerPage: 6,
      isLoading: false,  // 新增：用于加载状态
      keywordQuery: '',  // 新增：用于搜索关键词输入框
      showWelcomePopup: true  // 新增：用于控制欢迎弹窗显示
    };
  },
  computed: {
    paginatedCourses() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredCourses.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.filteredCourses.length / this.itemsPerPage);
    }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    selectTab(tab) {
      if (tab !== '更多') {
        this.selectedTab = tab;
        this.submitForm();
      }
    },
    showMoreMenu() {
      this.isMoreMenuVisible = true;
    },
    hideMoreMenu() {
      this.isMoreMenuVisible = false;
    },
    handleClickOutside(event) {
      if (this.$el && !this.$el.contains(event.target)) {
        this.hideMoreMenu();
      }
    },
    hideDropdown() {
      this.isMoreMenuVisible = false;
    },
    goBack() {
      this.$router.back();
    },
    async submitForm() {
      this.isLoading = true;  // 显示加载状态
      try {
        let request = {
          course: this.selectedTab,
          limit: `推荐不少于10门课，包含关键词: ${this.keywordQuery}`,
        }
        const response = await axios.post('http://localhost:5000/recommand', request);
        let recommendation = response.data;
        this.recommendations = recommendation;  // 更新推荐课程列表
      } catch (error) {
        console.error('Error fetching recommendation:', error);
      } finally {
        this.isLoading = false;  // 隐藏加载状态
      }
    },
    async handleEnter() {
      this.isLoading = true;  // 显示加载状态
      try {
        let courseQuery = this.searchQuery || this.selectedTab;
        let request = {
          course: courseQuery,
          limit: `推荐不少于10门课，包含关键词: ${this.keywordQuery}`,
        }
        const response = await axios.post('http://localhost:5000/recommand', request);
        let recommendation = response.data;
        this.recommendations = recommendation;  // 更新推荐课程列表
      } catch (error) {
        console.error('Error fetching recommendation:', error);
      } finally {
        this.isLoading = false;  // 隐藏加载状态
      }
    },
    openUrl(url) {
      window.open(url, '_blank');
    }
  }
};
</script>

<style lang="scss">
.course-selection {
  padding: 20px;
  font-family: Arial, sans-serif;
  position: relative;
  min-height: 92vh;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h1 {
      margin: 0;
      font-size: 32px;
      color: #333;
      display: flex;
      align-items: center;

      i {
        margin-right: 10px;
      }
    }

    .tabs {
      display: flex;
      gap: 10px;
      position: relative;

      .tab {
        padding: 10px 20px;
        background-color: #1a8dec;
        color: #fff;
        border-radius: 5px;
        cursor: pointer;
        position: relative;
        display: flex;
        align-items: center;

        &.active {
          background-color: #584eec;
        }

        &:hover {
          background-color: #3399ff;
        }

        i {
          margin-right: 5px;
        }

        .more-menu {
          position: absolute;
          top: 100%;
          left: 0;
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          background-color: #1199e2;
          border: 1px solid #ddd;
          border-radius: 5px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          padding: 10px;
          z-index: 1000;
          width: auto;

          .more-items {
            width: 100%;
            display: grid;
            grid-template-columns: repeat(3, 1fr);

            .more-item {
              padding: 10px;
              cursor: pointer;
              display: flex;
              align-items: center;
              justify-content: center;
              white-space: nowrap;

              i {
                margin-right: 5px;
              }

              &:hover {
                background-color: #2317c4;
              }
            }
          }
        }
      }
    }

    .search-and-back {
      display: flex;
      gap: 10px;

      input {
        padding: 5px;
        font-size: 16px;
        border: 1px solid #ccc;
        border-radius: 5px;
      }

      .keyword-input {
        padding: 5px;
        font-size: 16px;
        border: 1px solid #ccc;
        border-radius: 5px;
      }

      .back-button {
        padding: 5px 10px;
        background-color: #1a8dec;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        display: flex;
        align-items: center;

        &:hover {
          background-color: #584eec;
        }

        i {
          margin-right: 5px;
        }
      }
    }
  }

  .recommendations {
    margin-top: 20px;

    h2 {
      margin-bottom: 10px;
      font-size: 28px;
      color: #333;
    }

    .recommended-course {
      margin-bottom: 10px;
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 5px;
      background-color: #c4e6f4;
      cursor: pointer;
      transition: background-color 0.3s;

      &:hover {
        background-color: #9ed2f3;
      }

      .recommended-content {
        p {
          margin: 5px 0;
          font-size: 16px;
          color: #333;
        }

        a {
          color: #04477f;
          text-decoration: none;

          &:hover {
            text-decoration: underline;
          }
        }
      }
    }
  }

  .pagination {
    position: absolute;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;

    button {
      padding: 5px 10px;
      background-color: #1a8dec;
      color: #fff;
      border: none;
      border-radius: 5px;
      cursor: pointer;

      &:disabled {
        background-color: #ddd;
        cursor: not-allowed;
      }
    }
  }

  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;

    .loading-message {
      font-size: 24px;
      color: #1a8dec;
      display: flex;
      align-items: center;

      i {
        margin-right: 10px;
      }
    }
  }

  .welcome-popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2000;

    .welcome-popup {
      background: #fff;
      padding: 20px;
      border-radius: 10px;
      text-align: center;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);

      h3 {
        margin-top: 0;
        font-size: 24px;
        color: #333;
      }

      p {
        font-size: 18px;
        color: #666;
        margin: 10px 0;
      }

      button {
        padding: 10px 20px;
        background-color: #1a8dec;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;

        &:hover {
          background-color: #584eec;
        }
      }
    }
  }
}
</style>
