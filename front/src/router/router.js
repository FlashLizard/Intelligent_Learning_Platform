import { createRouter, createWebHistory } from 'vue-router';
import LoginPage from '../components/pages/login/LoginPage.vue';
import IndexPage from '../components/pages/index/IndexPage.vue';
import PPTGeneratorPage from '@/components/pages/teacher/PPTGeneratorPage.vue';
import HomeworkManagement from '@/components/pages/teacher/HomeworkManagement.vue';
import TestHome from '@/components/pages/tests/TestHome.vue';
import TestPage from '@/components/pages/tests/TestPage.vue';
import EvaluationPage from '@/components/pages/tests/EvaluationPage.vue';
import TestAnswer from '@/components/pages/tests/TestAnswer.vue';
import TestHistory from '@/components/pages/tests/TestHistory.vue';
import HexagonChart from '@/components/component/HexagonChart.vue';
import HistoryHexagonChart from '@/components/component/HistoryHexagonChart.vue';
import SidebarMenu from '@/components/component/SidebarMenu.vue';
import AiQa from '@/components/pages/aiqa/AiQa.vue';
import TeacherRecording from '@/components/pages/classrecord/TeacherRecording.vue';
import ClassSelect from '@/components/pages/classrecord/ClassSelect.vue'
import CourseHelper from '@/components/pages/teacher/CourseHelper.vue';
import ClassTest from '@/components/pages/teacher/ClassTest.vue'
import ClassTestEvaluation from '@/components/pages/teacher/ClassTestEvaluation.vue'
import TranslationPage from '@/components/pages/aiqa/TranslationPage.vue';
import PaperDownload from '@/components/pages/tests/PaperDownload.vue';
import HistoryTestAns from '@/components/pages/tests/HistoryTestAns.vue';
import HistoryEvaluationPage from '@/components/pages/tests/HistoryEvaluationPage.vue';

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/index',
    name: 'Index',
    component: IndexPage,
  },
  {
    path: '/pptgenerator',
    name: 'PPTGenerator',
    component: PPTGeneratorPage,
  },
  {
    path: '/testhome',
    name: 'TestHome',
    component: TestHome,
  },
  {
    path: '/testpage',
    name: 'TestPage',
    component: TestPage,
  },
  {
    path: '/testhistory',
    name: 'TestHistory',
    component: TestHistory,
  },
  {
    path: '/testanswer',
    name: 'TestAnswer',
    component: TestAnswer,
  },
  {
    path: '/evaluationpage',
    name: 'EvaluationPage',
    component: EvaluationPage,
  },
  {
    path: '/hexagonchart',
    name: 'HexagonChart',
    component: HexagonChart,
  },
  {
    path: '/historyhexagonchart',
    name: 'HistoryHexagonChart',
    component: HistoryHexagonChart,
  },
  {
    path: '/homeworkmanagement',
    name: 'HomeworkManagement',
    component: HomeworkManagement,
  },
  {
    path: '/sidebarmenu',
    name: 'SidebarMenu',
    component: SidebarMenu,
  },
  {
    path: '/aiqa',
    name: 'AiQa',
    component: AiQa,
  },
  {
    path: '/teacherrecording',
    name: 'TeacherRecording',
    component: TeacherRecording,
  },
  {
    path: '/classselect',
    name: 'ClassSelect',
    component: ClassSelect,
  },
  {
    path: '/coursehelper',
    name: 'CourseHelper',
    component: CourseHelper,
  },
  {
    path: '/classtest',
    name: 'ClassTest',
    component: ClassTest,
  },
  {
    path: '/classtestevaluation',
    name: 'ClassTestEvaluation',
    component: ClassTestEvaluation,
  },
  {
    path: '/translationpage',
    name: 'TranslationPage',
    component: TranslationPage,
  },
  {
    path: '/paperdownload',
    name: 'PaperDownload',
    component: PaperDownload,
  },
  {
    path: '/historytestans',
    name: HistoryTestAns,
    component: HistoryTestAns,
  },
  {
    path: '/historyevaluationpage',
    name: 'HistoryEvaluationPage',
    component: HistoryEvaluationPage,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
