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
  <div class="course-selection" @click="hideDropdown">
    <header class="header">
      <h1><i class="fas fa-graduation-cap"></i> AI荐课</h1>
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
        <i class="fas fa-spinner fa-spin"></i> 星火大模型正在筛选最适合您的课程...
      </div>
    </div>
    <!-- 报错弹窗 -->
    <div v-if="iswrong" class="loading-overlay">
      <div class="loading-message">
        <i class="fas fa-spinner fa-spin"></i> 网络出错了，请您重新检索...
      </div>
    </div>
    <div class="recommendations">
      <h2><i class="fas fa-book"></i> 推荐课程</h2>
      <button class="openguide-button" @click="guidevisible = true"> <i class="fas fa-exclamation-circle"></i> </button>
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
        <h3><i class="fas fa-handshake"></i>  欢迎使用AI荐课</h3>
        <p>AI荐课功能根据您指定的学科和关键词为您推荐各大平台上的课程，您可以通过本应用推荐的路径找到您感兴趣的课程。</p>
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
      showWelcomePopup: true,  // 新增：用于控制欢迎弹窗显示
      iswrong:false,
      guidetext: "1. 用户可以选择默认的学科，也可以自定义学科作为搜索的主题\n\n2. 在用户选定学科后，可以在右侧“搜索关键词”框中选择更加精细的知识点\n\n3. AI会根据用户需求，自动推荐适合用户的课程\n\n4. 点击页面中的课程条目，即可直接跳转到课程相应页面",
      guidevisible:false,
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
        const response = await axios.post('/recommand', request);
        console.log("recommend_request.data:",request.data)
        let recommendation = response.data;
        this.recommendations = recommendation;  // 更新推荐课程列表
      } catch (error) {
        console.log("err",this.selectedTab)
        if(this.selectedTab === '化学'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/intro-chemistry', 'course': 'Introduction to Chemistry:  Reactions and Ratios free Course by Duke University', 'star': '4.7 stars', 'content': 'by 1.2K reviews,  provide skills etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/thermodynamics-intro', 'course': 'Introduction to Thermodynamics: Transferring Energy from Here to There Course by University of Michigan', 'star': '4.8 stars', 'content': 'by 3.4K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/chemtherm1', 'course': 'Chemical Engineering Thermodynamics 1 free Course by Korea Advanced Institute of Science and Technology(KAIST)', 'star': '4.5 stars', 'content': 'by 28 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/general-chemistry', 'course': 'General Chemistry: Concept Development and Application free Course by Rice University', 'star': '4.6 stars', 'content': 'by 992 reviews,  provide skills Mathematics,  Problem Solving etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/chemicals-health', 'course': 'Chemicals and Health free Course by Johns Hopkins University', 'star': '4.7 stars', 'content': 'by 1.3K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/forensic-science', 'course': 'Introduction to Forensic Science free Course by Nanyang Technological University', 'star': 'Singapore', 'content': '4.9 stars,  by 2.4K reviews,  provide skills Critical Thinking etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/advanced-chemistry', 'course': 'Advanced Chemistry free Course by University of Kentucky', 'star': '4.7 stars', 'content': 'by 1.4K reviews,  provide skills Problem Solving etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/spectroscopy', 'course': 'Introduction to Molecular Spectroscopy free Course by University of Manchester   ', 'star': '4.7 stars', 'content': 'by 2.5K reviews,  provide skills Problem Solving,  Critical Thinking etc... Intermediate level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/basic-chemistry', 'course': 'Introduction to Chemistry:  Structures and Solutions free Course by Duke University', 'star': '4.6 stars', 'content': 'by 495 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/chemistry-1', 'course': 'Chemistry free Course by University of Kentucky', 'star': '4.7 stars', 'content': 'by 2.2K reviews,  provide skills Problem Solving etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/chemical-biology', 'course': 'Chemical Biology free Course by University of Geneva', 'star': '4.7 stars', 'content': 'by 122 reviews,  provide skills  etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/physical-chemistry', 'course': 'Introduction to Physical Chemistry free Course by University of Manchester   ', 'star': '4.7 stars', 'content': 'by 697 reviews,  provide skills  etc... Mixed level 1 - 3 Months'}];
        }
        else if(this.selectedTab === '计算机'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/introduction-to-hardware-and-operating-systems', 'course': 'Introduction to Hardware and Operating Systems Course by IBM', 'star': '4.8 stars', 'content': 'by 1.2K reviews,  provide skills Operating Systems,  Computer Networking,  IBM Cloud etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/degrees/bachelor-of-science-computer-science-london', 'course': 'Bachelor of Science in Computer Science Degree by University of London', 'star': 'provide skills Algorithms', 'content': 'Computer Graphics,  Computer Programming etc... 1 - 4 Years'}, {'url': 'https://www.coursera.org/professional-certificates/google-it-support', 'course': 'Google IT Support Professional Certificate by Google', 'star': '4.8 stars', 'content': 'by 190K reviews,  provide skills Computer Networking,  Network Architecture,  Network Model etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/cybersecurity-for-everyone', 'course': 'Cybersecurity for Everyone free Course by University of Maryland', 'star': 'College Park', 'content': '4.7 stars,  by 1.9K reviews,  provide skills Cyberattacks,  Human Computer Interaction,  Network Security etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/cs-programming-java', 'course': 'Computer Science: Programming with a Purpose free Course by Princeton University', 'star': '4.7 stars', 'content': 'by 1.2K reviews,  provide skills Computer Programming,  Java Programming,  Programming Principles etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/professional-certificates/google-cybersecurity', 'course': 'Google Cybersecurity Professional Certificate by Google', 'star': '4.8 stars', 'content': 'by 35K reviews,  provide skills Network Security,  Python Programming,  Linux etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/specializations/microsoft-365-fundamentals', 'course': 'Microsoft 365 Fundamentals Specialization by Microsoft', 'star': '4.7 stars', 'content': 'by 3.8K reviews,  provide skills Visual Design,  Communication,  Microsoft Excel etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/introduction-to-computers-and-office-productivity-software', 'course': 'Introduction to Computers and Office Productivity Software Course by The Hong Kong University of Science and Technology', 'star': '4.7 stars', 'content': 'by 1.7K reviews,  provide skills Computer Graphics,  Computer Programming,  Graphics Software etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/projects/business-analysis-process-management', 'course': 'Business Analysis & Process Management Guided Project by Coursera Project Network', 'star': '4.4 stars', 'content': 'by 4.1K reviews,  provide skills Business Analysis,  Business Process Management etc... Beginner level Less Than 2 Hours'}, {'url': 'https://www.coursera.org/learn/comparch', 'course': 'Computer Architecture free Course by Princeton University', 'star': '4.7 stars', 'content': 'by 2.8K reviews,  provide skills Computer Architecture,  Computer Programming,  Critical Thinking etc... Advanced level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/illinois-tech-computer-and-peripheral-hardware', 'course': 'Computer and Peripheral Hardware Course by Illinois Tech', 'star': '4.6 stars', 'content': 'by 33 reviews,  provide skills  etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/introduction-to-computers', 'course': 'Introduction to Computers new Course by Microsoft', 'star': '4.8 stars', 'content': 'by 165 reviews,  provide skills Computer Architecture,  Operating Systems etc... Beginner level 1 - 4 Weeks'}]
        }
        else if(this.selectedTab === '英语'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/glasscock', 'course': 'English and Academic Preparation - Pre-Collegiate free Course by Rice University', 'star': '4.7 stars', 'content': 'by 419 reviews,  provide skills  etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/english-for-interactions-in-the-workplace-intermediate-level', 'course': 'English for Interactions in the Workplace Intermediate Level free Course by Pontificia Universidad CatÃ³lica de Chile', 'star': '4.7 stars', 'content': 'by 81 reviews,  provide skills  etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/american-english-pronunciation', 'course': 'The Pronunciation of American English Specialization by University of California', 'star': 'Irvine', 'content': '4.8 stars,  by 1.1K reviews,  provide skills Communication etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/enpublicspeaking', 'course': 'Training and Practicing in English Public Speaking free Course by Shanghai Jiao Tong University', 'star': '4.6 stars', 'content': 'by 229 reviews,  provide skills Communication etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/english-common-interactions-workplace-basic-level', 'course': 'English for Common Interactions in the Workplace: Basic Level free Course by Pontificia Universidad CatÃ³lica de Chile', 'star': '4.7 stars', 'content': 'by 2.1K reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/learning-how-to-learn', 'course': 'Learning How to Learn: Powerful mental tools to help you master tough subjects free Course by Deep Teaching Solutions', 'star': '4.8 stars', 'content': 'by 90K reviews,  provide skills Adaptability etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/english-lower-intermediateb1', 'course': 'English Lower Intermediate B1.1 Course by UniversitÃ\xa0 di Napoli Federico II', 'star': '4.4 stars', 'content': 'by 77 reviews,  provide skills etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/learn-english-beginning-grammar', 'course': 'Learn English: Beginning Grammar Specialization by University of California', 'star': 'Irvine', 'content': '4.9 stars,  by 3.6K reviews,  provide skills Writing,  Communication etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/business-english', 'course': 'Business English Communication Skills Specialization by University of Washington', 'star': '4.8 stars', 'content': 'by 4.5K reviews,  provide skills Business Communication,  Communication,  Leadership and Management etc... Intermediate level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/stem', 'course': 'English for Science', 'star': 'Technology', 'content': 'Engineering,  and Mathematics free Course by University of Pennsylvania,  4.8 stars,  by 2.7K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/english-intermediate-b1-2', 'course': 'English Intermediate B1.2 new free Course by UniversitÃ\xa0 di Napoli Federico II', 'star': '4.7 stars', 'content': 'by 79 reviews,  provide skills  etc... Intermediate level 1 - 3 Months'}]
        }
        else if(this.selectedTab === '物理'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/engineering-mechanics-statics', 'course': 'Introduction to Engineering Mechanics free Course by Georgia Institute of Technology', 'star': '4.8 stars', 'content': 'by 4.9K reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/introduction-to-electricity-magnetism', 'course': 'Introduction to Electricity and Magnetism Specialization by Rice University', 'star': '4.7 stars', 'content': 'by 94 reviews,  provide skills Problem Solving etc... Intermediate level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/quantum-physics', 'course': 'Exploring Quantum Physics free Course by University of Maryland', 'star': 'College Park', 'content': '4.1 stars,  by 58 reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/introduction-to-mechanics', 'course': 'Introduction to Mechanics Specialization by Rice University', 'star': '4.6 stars', 'content': 'by 197 reviews,  provide skills Mathematics,  Problem Solving etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/waves-optics', 'course': 'Physics of Waves and Optics Specialization by Rice University', 'star': '4.9 stars', 'content': 'by 5 reviews,  provide skills Problem Solving etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/einstein-relativity', 'course': 'Understanding Einstein: The Special Theory of Relativity free Course by Stanford University', 'star': '4.9 stars', 'content': 'by 3K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/thermodynamics-intro', 'course': 'Introduction to Thermodynamics: Transferring Energy from Here to There Course by University of Michigan', 'star': '4.8 stars', 'content': 'by 3.4K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/mechanics-particles-planets', 'course': 'Mechanics: Motion', 'star': 'Forces', 'content': 'Energy and Gravity,  from Particles to Planets free Course by UNSW Sydney (The University of New South Wales),  4.7 stars,  by 1K reviews,  provide skills Problem Solving etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/particle-physics', 'course': 'Particle Physics: an Introduction free Course by University of Geneva', 'star': '4.4 stars', 'content': 'by 917 reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/understanding-modern-physics-1-relativity-and-cosmology', 'course': 'Understanding Modern Physics I: Relativity and Cosmology free Course by The Hong Kong University of Science and Technology', 'star': '4.7 stars', 'content': 'by 129 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/how-things-work', 'course': 'How Things Work: An Introduction to Physics free Course by University of Virginia', 'star': '4.8 stars', 'content': 'by 2.9K reviews,  provide skills Critical Thinking,  Experiment,  Problem Solving etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/big-bang', 'course': 'From the Big Bang to Dark Energy free Course by The University of Tokyo', 'star': '4.8 stars', 'content': 'by 3.5K reviews,  provide skills  etc... Beginner level 1 - 4 Weeks'}] 
        }
        else if(this.selectedTab === '历史'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/astro', 'course': 'Astronomy: Exploring Time and Space free Course by University of Arizona', 'star': '4.8 stars', 'content': 'by 3.7K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/magic-middle-ages', 'course': 'Magic in the Middle Ages free Course by Universitat de Barcelona', 'star': '4.6 stars', 'content': 'by 1.6K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/modern-world', 'course': 'The Modern World', 'star': 'Part One: Global History from 1760 to 1910 free Course by University of Virginia', 'content': '4.8 stars,  by 2.9K reviews,  provide skills Critical Thinking,  Human Learning etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/western-christianity-200-1650', 'course': 'A Journey through Western Christianity: from Persecuted Faith to Global Religion (200 - 1650)  free Course by Yale University', 'star': '4.8 stars', 'content': 'by 642 reviews,  provide skills Human Learning etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/bighistory', 'course': 'Big History - From the Big Bang until Today free Course by University of Amsterdam', 'star': '4.6 stars', 'content': 'by 240 reviews,  provide skills Critical Thinking etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/our-earth', 'course': 'Our Earth: Its Climate', 'star': 'History', 'content': 'and Processes free Course by University of Manchester   ,  4.7 stars,  by 364 reviews,  provide skills Critical Thinking etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/russian-history-lenin-putin', 'course': 'Russian History: from Lenin to Putin free Course by University of California', 'star': 'Santa Cruz', 'content': '4.7 stars,  by 769 reviews,  provide skills Critical Thinking etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/modern-postmodern-1', 'course': 'The Modern and the Postmodern (Part 1) free Course by Wesleyan University', 'star': '4.8 stars', 'content': 'by 989 reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/modern-world-2', 'course': 'The Modern World', 'star': 'Part Two: Global History since 1910 free Course by University of Virginia', 'content': '4.8 stars,  by 1.6K reviews,  provide skills Critical Thinking etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/ancient-greeks', 'course': 'The Ancient Greeks free Course by Wesleyan University', 'star': '4.7 stars', 'content': 'by 2K reviews,  provide skills  etc... Mixed level 1 - 3 Months'}]
        }
        else if(this.selectedTab === '生物'){
          this.recommendations = [{'url': 'https://www.coursera.org/specializations/introduction-to-biology', 'course': 'Introduction to Biology: Ecology', 'star': 'Evolution', 'content': '& Biodiversity Specialization by Rice University,  4.8 stars,  by 138 reviews,  provide skills  etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/forensic-science', 'course': 'Introduction to Forensic Science free Course by Nanyang Technological University', 'star': 'Singapore', 'content': '4.9 stars,  by 2.4K reviews,  provide skills Critical Thinking etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/anatomy', 'course': 'Anatomy Specialization by University of Michigan', 'star': '4.8 stars', 'content': 'by 3.7K reviews,  provide skills Human Learning etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/marine-biology', 'course': 'Marine Biology free Course by American Museum of Natural History', 'star': '4.8 stars', 'content': 'by 247 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/stem-cells', 'course': 'The Science of Stem Cells free Course by American Museum of Natural History', 'star': '4.7 stars', 'content': 'by 2.9K reviews,  provide skills  etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/astrobiology-exploring-other-worlds', 'course': 'Astrobiology: Exploring Other Worlds free Course by University of Arizona', 'star': '4.9 stars', 'content': 'by 463 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/genetics-evolution', 'course': 'Introduction to Genetics and Evolution free Course by Duke University', 'star': '4.8 stars', 'content': 'by 1.6K reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/physiology', 'course': 'Introductory Human Physiology free Course by Duke University', 'star': '4.8 stars', 'content': 'by 4.9K reviews,  provide skills Health etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/bioinformatics', 'course': 'Biology Meets Programming: Bioinformatics for Beginners free Course by University of California San Diego', 'star': '4.2 stars', 'content': 'by 1.5K reviews,  provide skills Bioinformatics,  Computational Thinking,  Problem Solving etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/neurobiology', 'course': 'Understanding the Brain: The Neurobiology of Everyday Life free Course by The University of Chicago', 'star': '4.9 stars', 'content': 'by 2.9K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}]
        }
        else if(this.selectedTab === '医学'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/biomedvis', 'course': 'Biomedical Visualisation free Course by University of Glasgow ', 'star': '4.6 stars', 'content': 'by 442 reviews,  provide skills Computer Graphic Techniques,  Interactive Data Visualization,  Scientific Visualization etc... Intermediate level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/diabetes-essential-facts', 'course': 'Diabetes â\x80\x93 the Essential Facts free Course by University of Copenhagen', 'star': '4.7 stars', 'content': 'by 2.2K reviews,  provide skills Leadership and Management etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/specializations/cancer-biology', 'course': 'Cancer Biology Specialization by Johns Hopkins University', 'star': '4.8 stars', 'content': 'by 9.3K reviews,  provide skills  etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/history-of-medicine', 'course': 'The History of Medicine: Philosophy', 'star': 'Science', 'content': 'and Psychology free Course by University of California,  Santa Cruz,  4.8 stars,  by 49 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/medical-neuroscience', 'course': 'Medical Neuroscience free Course by Duke University', 'star': '4.9 stars', 'content': 'by 2.7K reviews,  provide skills Health etc... Advanced level 3 - 6 Months'}, {'url': 'https://www.coursera.org/specializations/ai-for-medicine', 'course': 'AI for Medicine Specialization by DeepLearning.AI', 'star': '4.7 stars', 'content': 'by 2.3K reviews,  provide skills Machine Learning,  Machine Learning Algorithms,  Deep Learning etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/physiology', 'course': 'Introductory Human Physiology free Course by Duke University', 'star': '4.8 stars', 'content': 'by 4.9K reviews,  provide skills Health etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/space-medicine-duke', 'course': 'Space Medicine free Course by Duke University', 'star': '4.8 stars', 'content': 'by 393 reviews,  provide skills Critical Thinking etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/vital-signs', 'course': 'Vital Signs: Understanding What the Body Is Telling Us free Course by University of Pennsylvania', 'star': '4.8 stars', 'content': 'by 6.3K reviews,  provide skills Health etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/anatomy', 'course': 'Anatomy Specialization by University of Michigan', 'star': '4.8 stars', 'content': 'by 3.7K reviews, provide skills Human Learning etc... Beginner level 3 - 6 Months'}]
        }
        else if(this.selectedTab === '文学'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/historical-fiction', 'course': 'Plagues', 'star': 'Witches', 'content': 'and War: The Worlds of Historical Fiction free Course by University of Virginia,  4.6 stars,  by 583 reviews,  provide skills Writing etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/sciwrite', 'course': 'Writing in the Sciences free Course by Stanford University', 'star': '4.9 stars', 'content': 'by 8.6K reviews,  provide skills Writing etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/modpo', 'course': 'Modern & Contemporary American Poetry (â\x80\x9cModPoâ\x80\x9d) free Course by University of Pennsylvania', 'star': '4.9 stars', 'content': 'by 577 reviews,  provide skills  etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/etudier-en-france', 'course': 'Ã\x89tudier en France: French Intermediate course B1-B2 free Course by Ã\x89cole Polytechnique', 'star': '4.8 stars', 'content': 'by 4.8K reviews,  provide skills Communication,  Writing etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/interactive-media-gaming', 'course': 'Online Games: Literature', 'star': 'New Media', 'content': 'and Narrative free Course by Vanderbilt University,  4.6 stars,  by 185 reviews,  provide skills Storytelling etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/modern-postmodern-2', 'course': 'The Modern and the Postmodern (Part 2) free Course by Wesleyan University', 'star': '4.8 stars', 'content': 'by 359 reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/learning-how-to-learn', 'course': 'Learning How to Learn: Powerful mental tools to help you master tough subjects free Course by Deep Teaching Solutions', 'star': '4.8 stars', 'content': 'by 90K reviews,  provide skills Adaptability etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/craft-of-plot', 'course': 'Creative Writing: The Craft of Plot Course by Wesleyan University', 'star': '4.7 stars', 'content': 'by 4.8K reviews,  provide skills Storytelling etc... Mixed level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/research-methods', 'course': 'Understanding Research Methods free Course by University of London', 'star': 'SOAS University of London', 'content': '4.6 stars,  by 7.5K reviews,  provide skills Critical Thinking,  Planning,  Writing etc... Mixed level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/visual-literary-culture-in-japan', 'course': 'Words Spun Out of Images: Visual and Literary Culture in Nineteenth Century Japan free Course by The University of Tokyo', 'star': '4.8 stars', 'content': 'by 730 reviews,  provide skills  etc... Beginner level 1 - 4 Weeks'}]
        }
        else if(this.selectedTab === '数学'){
          this.recommendations = [{'url': 'https://www.coursera.org/specializations/mathematics-machine-learning', 'course': 'Mathematics for Machine Learning Specialization by Imperial College London', 'star': '4.6 stars', 'content': 'by 14K reviews,  provide skills Algebra,  Linear Algebra,  Mathematics etc... Beginner level 3 - 6 Months'},{'url': 'https://www.coursera.org/learn/logic-introduction', 'course': 'Introduction to Logic free Course by Stanford University', 'star': '4.4 stars', 'content': 'by 627 reviews,  provide skills Computational Logic,  Mathematics,  Problem Solving etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/mathematics-for-machine-learning-and-data-science', 'course': 'Mathematics for Machine Learning and Data Science Specialization by DeepLearning.AI', 'star': '4.6 stars', 'content': 'by 2K reviews,  provide skills Machine Learning,  Calculus,  Differential Equations etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/mathematical-thinking', 'course': 'Introduction to Mathematical Thinking free Course by Stanford University', 'star': '4.8 stars', 'content': 'by 2.7K reviews,  provide skills Critical Thinking,  Mathematical Theory & Analysis,  Mathematics etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/mathematics-engineers', 'course': 'Mathematics for Engineers Specialization by The Hong Kong University of Science and Technology', 'star': '4.8 stars', 'content': 'by 7.1K reviews,  provide skills Mathematics,  Calculus,  Linear Algebra etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/specializations/algebra-elementary-to-advanced', 'course': 'Algebra: Elementary to Advanced Specialization by Johns Hopkins University', 'star': '4.8 stars', 'content': 'by 561 reviews,  provide skills Algebra,  Mathematics,  Problem Solving etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/introduction-to-calculus', 'course': 'Introduction to Calculus free Course by The University of Sydney', 'star': '4.8 stars', 'content': 'by 3.6K reviews,  provide skills Algebra,  Calculus,  Mathematical Theory & Analysis etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/stanford-statistics', 'course': 'Introduction to Statistics free Course by Stanford University', 'star': '4.6 stars', 'content': 'by 3.1K reviews,  provide skills General Statistics,  Probability & Statistics,  Statistical Analysis etc... Beginner level 1 - 3 Months'},{'url': 'https://www.coursera.org/learn/basicmathematics', 'course': 'Basic Mathematics free Course by Birla Institute of Technology & Science', 'star': 'Pilani', 'content': '4.1 stars,  by 38 reviews,  provide skills Differential Equations,  Mathematics etc... Beginner level 1 - 3 Months'},  {'url': 'https://www.coursera.org/specializations/mathematics-machine-learning', 'course': 'Mathematics for Machine Learning Specialization by Imperial College London', 'star': '4.6 stars', 'content': 'by 14K reviews,  provide skills Algebra,  Linear Algebra,  Mathematics etc... Beginner level 3 - 6 Months'}];
        }
        else{
          this.recommendations = [{'url': 'https://www.coursera.org/learn/astro', 'course': 'Astronomy: Exploring Time and Space free Course by University of Arizona', 'star': '4.8 stars', 'content': 'by 3.7K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/magic-middle-ages', 'course': 'Magic in the Middle Ages free Course by Universitat de Barcelona', 'star': '4.6 stars', 'content': 'by 1.6K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/modern-world', 'course': 'The Modern World', 'star': 'Part One: Global History from 1760 to 1910 free Course by University of Virginia', 'content': '4.8 stars,  by 2.9K reviews,  provide skills Critical Thinking,  Human Learning etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/western-christianity-200-1650', 'course': 'A Journey through Western Christianity: from Persecuted Faith to Global Religion (200 - 1650)  free Course by Yale University', 'star': '4.8 stars', 'content': 'by 642 reviews,  provide skills Human Learning etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/bighistory', 'course': 'Big History - From the Big Bang until Today free Course by University of Amsterdam', 'star': '4.6 stars', 'content': 'by 240 reviews,  provide skills Critical Thinking etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/our-earth', 'course': 'Our Earth: Its Climate', 'star': 'History', 'content': 'and Processes free Course by University of Manchester   ,  4.7 stars,  by 364 reviews,  provide skills Critical Thinking etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/russian-history-lenin-putin', 'course': 'Russian History: from Lenin to Putin free Course by University of California', 'star': 'Santa Cruz', 'content': '4.7 stars,  by 769 reviews,  provide skills Critical Thinking etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/modern-postmodern-1', 'course': 'The Modern and the Postmodern (Part 1) free Course by Wesleyan University', 'star': '4.8 stars', 'content': 'by 989 reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/modern-world-2', 'course': 'The Modern World', 'star': 'Part Two: Global History since 1910 free Course by University of Virginia', 'content': '4.8 stars,  by 1.6K reviews,  provide skills Critical Thinking etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/ancient-greeks', 'course': 'The Ancient Greeks free Course by Wesleyan University', 'star': '4.7 stars', 'content': 'by 2K reviews,  provide skills  etc... Mixed level 1 - 3 Months'}]
        }
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
        if(courseQuery === '生物'){
          this.recommendations = [{'url': 'https://www.coursera.org/specializations/introduction-to-biology', 'course': 'Introduction to Biology: Ecology', 'star': 'Evolution', 'content': '& Biodiversity Specialization by Rice University,  4.8 stars,  by 138 reviews,  provide skills  etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/forensic-science', 'course': 'Introduction to Forensic Science free Course by Nanyang Technological University', 'star': 'Singapore', 'content': '4.9 stars,  by 2.4K reviews,  provide skills Critical Thinking etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/anatomy', 'course': 'Anatomy Specialization by University of Michigan', 'star': '4.8 stars', 'content': 'by 3.7K reviews,  provide skills Human Learning etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/marine-biology', 'course': 'Marine Biology free Course by American Museum of Natural History', 'star': '4.8 stars', 'content': 'by 247 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/stem-cells', 'course': 'The Science of Stem Cells free Course by American Museum of Natural History', 'star': '4.7 stars', 'content': 'by 2.9K reviews,  provide skills  etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/astrobiology-exploring-other-worlds', 'course': 'Astrobiology: Exploring Other Worlds free Course by University of Arizona', 'star': '4.9 stars', 'content': 'by 463 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/genetics-evolution', 'course': 'Introduction to Genetics and Evolution free Course by Duke University', 'star': '4.8 stars', 'content': 'by 1.6K reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/physiology', 'course': 'Introductory Human Physiology free Course by Duke University', 'star': '4.8 stars', 'content': 'by 4.9K reviews,  provide skills Health etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/bioinformatics', 'course': 'Biology Meets Programming: Bioinformatics for Beginners free Course by University of California San Diego', 'star': '4.2 stars', 'content': 'by 1.5K reviews,  provide skills Bioinformatics,  Computational Thinking,  Problem Solving etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/neurobiology', 'course': 'Understanding the Brain: The Neurobiology of Everyday Life free Course by The University of Chicago', 'star': '4.9 stars', 'content': 'by 2.9K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}]
        }
        else if(courseQuery === '医学'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/biomedvis', 'course': 'Biomedical Visualisation free Course by University of Glasgow ', 'star': '4.6 stars', 'content': 'by 442 reviews,  provide skills Computer Graphic Techniques,  Interactive Data Visualization,  Scientific Visualization etc... Intermediate level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/diabetes-essential-facts', 'course': 'Diabetes â\x80\x93 the Essential Facts free Course by University of Copenhagen', 'star': '4.7 stars', 'content': 'by 2.2K reviews,  provide skills Leadership and Management etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/specializations/cancer-biology', 'course': 'Cancer Biology Specialization by Johns Hopkins University', 'star': '4.8 stars', 'content': 'by 9.3K reviews,  provide skills  etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/history-of-medicine', 'course': 'The History of Medicine: Philosophy', 'star': 'Science', 'content': 'and Psychology free Course by University of California,  Santa Cruz,  4.8 stars,  by 49 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/medical-neuroscience', 'course': 'Medical Neuroscience free Course by Duke University', 'star': '4.9 stars', 'content': 'by 2.7K reviews,  provide skills Health etc... Advanced level 3 - 6 Months'}, {'url': 'https://www.coursera.org/specializations/ai-for-medicine', 'course': 'AI for Medicine Specialization by DeepLearning.AI', 'star': '4.7 stars', 'content': 'by 2.3K reviews,  provide skills Machine Learning,  Machine Learning Algorithms,  Deep Learning etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/physiology', 'course': 'Introductory Human Physiology free Course by Duke University', 'star': '4.8 stars', 'content': 'by 4.9K reviews,  provide skills Health etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/space-medicine-duke', 'course': 'Space Medicine free Course by Duke University', 'star': '4.8 stars', 'content': 'by 393 reviews,  provide skills Critical Thinking etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/vital-signs', 'course': 'Vital Signs: Understanding What the Body Is Telling Us free Course by University of Pennsylvania', 'star': '4.8 stars', 'content': 'by 6.3K reviews,  provide skills Health etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/anatomy', 'course': 'Anatomy Specialization by University of Michigan', 'star': '4.8 stars', 'content': 'by 3.7K reviews, provide skills Human Learning etc... Beginner level 3 - 6 Months'}]
        }
        else if(courseQuery === '文学'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/historical-fiction', 'course': 'Plagues', 'star': 'Witches', 'content': 'and War: The Worlds of Historical Fiction free Course by University of Virginia,  4.6 stars,  by 583 reviews,  provide skills Writing etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/sciwrite', 'course': 'Writing in the Sciences free Course by Stanford University', 'star': '4.9 stars', 'content': 'by 8.6K reviews,  provide skills Writing etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/modpo', 'course': 'Modern & Contemporary American Poetry (â\x80\x9cModPoâ\x80\x9d) free Course by University of Pennsylvania', 'star': '4.9 stars', 'content': 'by 577 reviews,  provide skills  etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/etudier-en-france', 'course': 'Ã\x89tudier en France: French Intermediate course B1-B2 free Course by Ã\x89cole Polytechnique', 'star': '4.8 stars', 'content': 'by 4.8K reviews,  provide skills Communication,  Writing etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/interactive-media-gaming', 'course': 'Online Games: Literature', 'star': 'New Media', 'content': 'and Narrative free Course by Vanderbilt University,  4.6 stars,  by 185 reviews,  provide skills Storytelling etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/modern-postmodern-2', 'course': 'The Modern and the Postmodern (Part 2) free Course by Wesleyan University', 'star': '4.8 stars', 'content': 'by 359 reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/learning-how-to-learn', 'course': 'Learning How to Learn: Powerful mental tools to help you master tough subjects free Course by Deep Teaching Solutions', 'star': '4.8 stars', 'content': 'by 90K reviews,  provide skills Adaptability etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/craft-of-plot', 'course': 'Creative Writing: The Craft of Plot Course by Wesleyan University', 'star': '4.7 stars', 'content': 'by 4.8K reviews,  provide skills Storytelling etc... Mixed level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/research-methods', 'course': 'Understanding Research Methods free Course by University of London', 'star': 'SOAS University of London', 'content': '4.6 stars,  by 7.5K reviews,  provide skills Critical Thinking,  Planning,  Writing etc... Mixed level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/visual-literary-culture-in-japan', 'course': 'Words Spun Out of Images: Visual and Literary Culture in Nineteenth Century Japan free Course by The University of Tokyo', 'star': '4.8 stars', 'content': 'by 730 reviews,  provide skills  etc... Beginner level 1 - 4 Weeks'}]
        }
        else if(courseQuery === '化学'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/intro-chemistry', 'course': 'Introduction to Chemistry:  Reactions and Ratios free Course by Duke University', 'star': '4.7 stars', 'content': 'by 1.2K reviews,  provide skills etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/thermodynamics-intro', 'course': 'Introduction to Thermodynamics: Transferring Energy from Here to There Course by University of Michigan', 'star': '4.8 stars', 'content': 'by 3.4K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/chemtherm1', 'course': 'Chemical Engineering Thermodynamics 1 free Course by Korea Advanced Institute of Science and Technology(KAIST)', 'star': '4.5 stars', 'content': 'by 28 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/general-chemistry', 'course': 'General Chemistry: Concept Development and Application free Course by Rice University', 'star': '4.6 stars', 'content': 'by 992 reviews,  provide skills Mathematics,  Problem Solving etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/chemicals-health', 'course': 'Chemicals and Health free Course by Johns Hopkins University', 'star': '4.7 stars', 'content': 'by 1.3K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/forensic-science', 'course': 'Introduction to Forensic Science free Course by Nanyang Technological University', 'star': 'Singapore', 'content': '4.9 stars,  by 2.4K reviews,  provide skills Critical Thinking etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/advanced-chemistry', 'course': 'Advanced Chemistry free Course by University of Kentucky', 'star': '4.7 stars', 'content': 'by 1.4K reviews,  provide skills Problem Solving etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/spectroscopy', 'course': 'Introduction to Molecular Spectroscopy free Course by University of Manchester   ', 'star': '4.7 stars', 'content': 'by 2.5K reviews,  provide skills Problem Solving,  Critical Thinking etc... Intermediate level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/basic-chemistry', 'course': 'Introduction to Chemistry:  Structures and Solutions free Course by Duke University', 'star': '4.6 stars', 'content': 'by 495 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/chemistry-1', 'course': 'Chemistry free Course by University of Kentucky', 'star': '4.7 stars', 'content': 'by 2.2K reviews,  provide skills Problem Solving etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/chemical-biology', 'course': 'Chemical Biology free Course by University of Geneva', 'star': '4.7 stars', 'content': 'by 122 reviews,  provide skills  etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/physical-chemistry', 'course': 'Introduction to Physical Chemistry free Course by University of Manchester   ', 'star': '4.7 stars', 'content': 'by 697 reviews,  provide skills  etc... Mixed level 1 - 3 Months'}];
        }
        else if(courseQuery === '计算机'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/introduction-to-hardware-and-operating-systems', 'course': 'Introduction to Hardware and Operating Systems Course by IBM', 'star': '4.8 stars', 'content': 'by 1.2K reviews,  provide skills Operating Systems,  Computer Networking,  IBM Cloud etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/degrees/bachelor-of-science-computer-science-london', 'course': 'Bachelor of Science in Computer Science Degree by University of London', 'star': 'provide skills Algorithms', 'content': 'Computer Graphics,  Computer Programming etc... 1 - 4 Years'}, {'url': 'https://www.coursera.org/professional-certificates/google-it-support', 'course': 'Google IT Support Professional Certificate by Google', 'star': '4.8 stars', 'content': 'by 190K reviews,  provide skills Computer Networking,  Network Architecture,  Network Model etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/cybersecurity-for-everyone', 'course': 'Cybersecurity for Everyone free Course by University of Maryland', 'star': 'College Park', 'content': '4.7 stars,  by 1.9K reviews,  provide skills Cyberattacks,  Human Computer Interaction,  Network Security etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/cs-programming-java', 'course': 'Computer Science: Programming with a Purpose free Course by Princeton University', 'star': '4.7 stars', 'content': 'by 1.2K reviews,  provide skills Computer Programming,  Java Programming,  Programming Principles etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/professional-certificates/google-cybersecurity', 'course': 'Google Cybersecurity Professional Certificate by Google', 'star': '4.8 stars', 'content': 'by 35K reviews,  provide skills Network Security,  Python Programming,  Linux etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/specializations/microsoft-365-fundamentals', 'course': 'Microsoft 365 Fundamentals Specialization by Microsoft', 'star': '4.7 stars', 'content': 'by 3.8K reviews,  provide skills Visual Design,  Communication,  Microsoft Excel etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/introduction-to-computers-and-office-productivity-software', 'course': 'Introduction to Computers and Office Productivity Software Course by The Hong Kong University of Science and Technology', 'star': '4.7 stars', 'content': 'by 1.7K reviews,  provide skills Computer Graphics,  Computer Programming,  Graphics Software etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/projects/business-analysis-process-management', 'course': 'Business Analysis & Process Management Guided Project by Coursera Project Network', 'star': '4.4 stars', 'content': 'by 4.1K reviews,  provide skills Business Analysis,  Business Process Management etc... Beginner level Less Than 2 Hours'}, {'url': 'https://www.coursera.org/learn/comparch', 'course': 'Computer Architecture free Course by Princeton University', 'star': '4.7 stars', 'content': 'by 2.8K reviews,  provide skills Computer Architecture,  Computer Programming,  Critical Thinking etc... Advanced level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/illinois-tech-computer-and-peripheral-hardware', 'course': 'Computer and Peripheral Hardware Course by Illinois Tech', 'star': '4.6 stars', 'content': 'by 33 reviews,  provide skills  etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/introduction-to-computers', 'course': 'Introduction to Computers new Course by Microsoft', 'star': '4.8 stars', 'content': 'by 165 reviews,  provide skills Computer Architecture,  Operating Systems etc... Beginner level 1 - 4 Weeks'}]
        }
        else if(courseQuery === '英语'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/glasscock', 'course': 'English and Academic Preparation - Pre-Collegiate free Course by Rice University', 'star': '4.7 stars', 'content': 'by 419 reviews,  provide skills  etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/english-for-interactions-in-the-workplace-intermediate-level', 'course': 'English for Interactions in the Workplace Intermediate Level free Course by Pontificia Universidad CatÃ³lica de Chile', 'star': '4.7 stars', 'content': 'by 81 reviews,  provide skills  etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/american-english-pronunciation', 'course': 'The Pronunciation of American English Specialization by University of California', 'star': 'Irvine', 'content': '4.8 stars,  by 1.1K reviews,  provide skills Communication etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/enpublicspeaking', 'course': 'Training and Practicing in English Public Speaking free Course by Shanghai Jiao Tong University', 'star': '4.6 stars', 'content': 'by 229 reviews,  provide skills Communication etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/english-common-interactions-workplace-basic-level', 'course': 'English for Common Interactions in the Workplace: Basic Level free Course by Pontificia Universidad CatÃ³lica de Chile', 'star': '4.7 stars', 'content': 'by 2.1K reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/learning-how-to-learn', 'course': 'Learning How to Learn: Powerful mental tools to help you master tough subjects free Course by Deep Teaching Solutions', 'star': '4.8 stars', 'content': 'by 90K reviews,  provide skills Adaptability etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/english-lower-intermediateb1', 'course': 'English Lower Intermediate B1.1 Course by UniversitÃ\xa0 di Napoli Federico II', 'star': '4.4 stars', 'content': 'by 77 reviews,  provide skills etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/learn-english-beginning-grammar', 'course': 'Learn English: Beginning Grammar Specialization by University of California', 'star': 'Irvine', 'content': '4.9 stars,  by 3.6K reviews,  provide skills Writing,  Communication etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/business-english', 'course': 'Business English Communication Skills Specialization by University of Washington', 'star': '4.8 stars', 'content': 'by 4.5K reviews,  provide skills Business Communication,  Communication,  Leadership and Management etc... Intermediate level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/stem', 'course': 'English for Science', 'star': 'Technology', 'content': 'Engineering,  and Mathematics free Course by University of Pennsylvania,  4.8 stars,  by 2.7K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/english-intermediate-b1-2', 'course': 'English Intermediate B1.2 new free Course by UniversitÃ\xa0 di Napoli Federico II', 'star': '4.7 stars', 'content': 'by 79 reviews,  provide skills  etc... Intermediate level 1 - 3 Months'}]
        }
        else if(courseQuery === '物理'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/engineering-mechanics-statics', 'course': 'Introduction to Engineering Mechanics free Course by Georgia Institute of Technology', 'star': '4.8 stars', 'content': 'by 4.9K reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/introduction-to-electricity-magnetism', 'course': 'Introduction to Electricity and Magnetism Specialization by Rice University', 'star': '4.7 stars', 'content': 'by 94 reviews,  provide skills Problem Solving etc... Intermediate level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/quantum-physics', 'course': 'Exploring Quantum Physics free Course by University of Maryland', 'star': 'College Park', 'content': '4.1 stars,  by 58 reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/introduction-to-mechanics', 'course': 'Introduction to Mechanics Specialization by Rice University', 'star': '4.6 stars', 'content': 'by 197 reviews,  provide skills Mathematics,  Problem Solving etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/waves-optics', 'course': 'Physics of Waves and Optics Specialization by Rice University', 'star': '4.9 stars', 'content': 'by 5 reviews,  provide skills Problem Solving etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/einstein-relativity', 'course': 'Understanding Einstein: The Special Theory of Relativity free Course by Stanford University', 'star': '4.9 stars', 'content': 'by 3K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/thermodynamics-intro', 'course': 'Introduction to Thermodynamics: Transferring Energy from Here to There Course by University of Michigan', 'star': '4.8 stars', 'content': 'by 3.4K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/mechanics-particles-planets', 'course': 'Mechanics: Motion', 'star': 'Forces', 'content': 'Energy and Gravity,  from Particles to Planets free Course by UNSW Sydney (The University of New South Wales),  4.7 stars,  by 1K reviews,  provide skills Problem Solving etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/particle-physics', 'course': 'Particle Physics: an Introduction free Course by University of Geneva', 'star': '4.4 stars', 'content': 'by 917 reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/understanding-modern-physics-1-relativity-and-cosmology', 'course': 'Understanding Modern Physics I: Relativity and Cosmology free Course by The Hong Kong University of Science and Technology', 'star': '4.7 stars', 'content': 'by 129 reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/how-things-work', 'course': 'How Things Work: An Introduction to Physics free Course by University of Virginia', 'star': '4.8 stars', 'content': 'by 2.9K reviews,  provide skills Critical Thinking,  Experiment,  Problem Solving etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/big-bang', 'course': 'From the Big Bang to Dark Energy free Course by The University of Tokyo', 'star': '4.8 stars', 'content': 'by 3.5K reviews,  provide skills  etc... Beginner level 1 - 4 Weeks'}] 
        }
        else if(courseQuery === '数学'){
          this.recommendations = [{'url': 'https://www.coursera.org/learn/complex-analysis', 'course': 'Introduction to Complex Analysis free Course by Wesleyan University', 'star': '4.8 stars', 'content': 'by 1K reviews,  provide skills Algebra,  Calculus,  Mathematical Theory & Analysis etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/basicmathematics', 'course': 'Basic Mathematics free Course by Birla Institute of Technology & Science', 'star': 'Pilani', 'content': '4.1 stars,  by 38 reviews,  provide skills Differential Equations,  Mathematics etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/logic-introduction', 'course': 'Introduction to Logic free Course by Stanford University', 'star': '4.4 stars', 'content': 'by 627 reviews,  provide skills Computational Logic,  Mathematics,  Problem Solving etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/mathematics-for-machine-learning-and-data-science', 'course': 'Mathematics for Machine Learning and Data Science Specialization by DeepLearning.AI', 'star': '4.6 stars', 'content': 'by 2K reviews,  provide skills Machine Learning,  Calculus,  Differential Equations etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/mathematical-thinking', 'course': 'Introduction to Mathematical Thinking free Course by Stanford University', 'star': '4.8 stars', 'content': 'by 2.7K reviews,  provide skills Critical Thinking,  Mathematical Theory & Analysis,  Mathematics etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/mathematics-engineers', 'course': 'Mathematics for Engineers Specialization by The Hong Kong University of Science and Technology', 'star': '4.8 stars', 'content': 'by 7.1K reviews,  provide skills Mathematics,  Calculus,  Linear Algebra etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/specializations/algebra-elementary-to-advanced', 'course': 'Algebra: Elementary to Advanced Specialization by Johns Hopkins University', 'star': '4.8 stars', 'content': 'by 561 reviews,  provide skills Algebra,  Mathematics,  Problem Solving etc... Beginner level 3 - 6 Months'}, {'url': 'https://www.coursera.org/learn/introduction-to-calculus', 'course': 'Introduction to Calculus free Course by The University of Sydney', 'star': '4.8 stars', 'content': 'by 3.6K reviews,  provide skills Algebra,  Calculus,  Mathematical Theory & Analysis etc... Intermediate level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/stanford-statistics', 'course': 'Introduction to Statistics free Course by Stanford University', 'star': '4.6 stars', 'content': 'by 3.1K reviews,  provide skills General Statistics,  Probability & Statistics,  Statistical Analysis etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/specializations/mathematics-machine-learning', 'course': 'Mathematics for Machine Learning Specialization by Imperial College London', 'star': '4.6 stars', 'content': 'by 14K reviews,  provide skills Algebra,  Linear Algebra,  Mathematics etc... Beginner level 3 - 6 Months'}];
        }
        else{
          this.recommendations = [{'url': 'https://www.coursera.org/learn/astro', 'course': 'Astronomy: Exploring Time and Space free Course by University of Arizona', 'star': '4.8 stars', 'content': 'by 3.7K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/magic-middle-ages', 'course': 'Magic in the Middle Ages free Course by Universitat de Barcelona', 'star': '4.6 stars', 'content': 'by 1.6K reviews,  provide skills  etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/modern-world', 'course': 'The Modern World', 'star': 'Part One: Global History from 1760 to 1910 free Course by University of Virginia', 'content': '4.8 stars,  by 2.9K reviews,  provide skills Critical Thinking,  Human Learning etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/western-christianity-200-1650', 'course': 'A Journey through Western Christianity: from Persecuted Faith to Global Religion (200 - 1650)  free Course by Yale University', 'star': '4.8 stars', 'content': 'by 642 reviews,  provide skills Human Learning etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/bighistory', 'course': 'Big History - From the Big Bang until Today free Course by University of Amsterdam', 'star': '4.6 stars', 'content': 'by 240 reviews,  provide skills Critical Thinking etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/our-earth', 'course': 'Our Earth: Its Climate', 'star': 'History', 'content': 'and Processes free Course by University of Manchester   ,  4.7 stars,  by 364 reviews,  provide skills Critical Thinking etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/russian-history-lenin-putin', 'course': 'Russian History: from Lenin to Putin free Course by University of California', 'star': 'Santa Cruz', 'content': '4.7 stars,  by 769 reviews,  provide skills Critical Thinking etc... Beginner level 1 - 4 Weeks'}, {'url': 'https://www.coursera.org/learn/modern-postmodern-1', 'course': 'The Modern and the Postmodern (Part 1) free Course by Wesleyan University', 'star': '4.8 stars', 'content': 'by 989 reviews,  provide skills  etc... Mixed level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/modern-world-2', 'course': 'The Modern World', 'star': 'Part Two: Global History since 1910 free Course by University of Virginia', 'content': '4.8 stars,  by 1.6K reviews,  provide skills Critical Thinking etc... Beginner level 1 - 3 Months'}, {'url': 'https://www.coursera.org/learn/ancient-greeks', 'course': 'The Ancient Greeks free Course by Wesleyan University', 'star': '4.7 stars', 'content': 'by 2K reviews,  provide skills  etc... Mixed level 1 - 3 Months'}]
        }
        const response = await axios.post('/recommand', request);
        let recommendation = response.data;
        this.recommendations = recommendation;  // 更新推荐课程列表
      } catch (error) {
        this.isLoading = false;
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
      color: #0084ef;
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

    .openguide-button {
      text-align: center;
      justify-self: center;
      padding: 0.5rem;
      display: inline-block; 
      vertical-align: middle;
      background-color: transparent;
      color: #007bff;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      position: absolute; 
      font-weight: bold;
      font-size: 1.5em;
      top:83px;
      left:170px;
    }
    .openguide-button:hover {
      color: #4ca0fa;
    }

    h2 {
      margin-bottom: 10px;
      font-size: 28px;
      color: #0084ef;
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
      width: 40%;
      background: #fff;
      padding: 20px;
      border-radius: 10px;
      text-align: center;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);

      h3 {
        margin-top: 0;
        font-size: 24px;
        font-weight: bold;
        color: #297af4;
      }

      p {
        font-size: 18px;
        color: #666;
        margin: 10px 0;
      }
      p {
        white-space: normal; /* 确保文本自动换行 */
        word-wrap: break-word; /* 长单词换行 */
        word-break: break-word; /* 对超长词进行强制换行 */
        max-width: 100%; /* 限制宽度以确保适应弹窗 */
        margin: 10px 0;
        line-height: 1.5;
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
