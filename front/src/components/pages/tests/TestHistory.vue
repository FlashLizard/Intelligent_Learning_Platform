<template>
  <div class="self-test-history">
    <header class="header">
      <h1>自测历史</h1>
      <button class="back-button" @click="goBack">
        <i class="fas fa-arrow-left"></i>
      </button>
    </header>
    <main class="main">
      <div class="scroll-panel">
        <div class="history-item title-row">
          <div class="item-info">
            <span class="item-date">测试时间</span>
            <span class="item-subject">测试学科</span>
            <span class="item-topic">测试知识点</span>
            <span class="item-score">测试评分</span>
          </div>
        </div>
        <div
          class="history-item"
          v-for="item in history"
          :key="item.id"
          @mouseenter="highlightItem(item.id)"
          @mouseleave="unhighlightItem()"
          @click="fetchTestDetail(item.id)"
        >
          <div class="item-info">
            <span class="item-date">{{ formatDateTime(item.test_time) }}</span>
            <span class="item-subject">{{ item.test_name }}</span>
            <span class="item-topic">{{ removeQuotes(item.test_subjects) }}</span>
            <span class="item-score">{{ item.test_score }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';
import { openDB } from 'idb';

export default {
  data() {
    return {
      history: [],
      highlightedItemId: null,
    };
  },
  async mounted() {
    try {
      // Open UserDatabase and get the userId
      const db = await openDB('UserDatabase', 1);
      const tx = db.transaction('users', 'readonly');
      const store = tx.objectStore('users');
      const allUsers = await store.getAll();
      await tx.done;
      if (allUsers.length > 0) {
        const { userId } = allUsers[0];
        console.log('Retrieved userId:', userId);

        // Fetch user tests from the backend
        const response = await axios.post('/get_user_tests', 
          { user_id: userId }
        ).then((response) => {
          return response;
        });

        const data = response.data;
        if (data.status === 'success') {
          this.history = data.tests;
          console.log('this.history:', this.history);
        } else {
          console.error('Failed to fetch user tests');
        }
      } else {
        console.error('No user found in UserDatabase');
      }
    } catch (error) {
      console.error('Error retrieving user tests:', error);
    }
  },
  methods: {
    goBack() {
      // Implement your back functionality here
      this.$router.back();
    },
    highlightItem(id) {
      this.highlightedItemId = id;
    },
    unhighlightItem() {
      this.highlightedItemId = null;
    },
    async fetchTestDetail(testId) {
  try {
    // Fetch test details from the backend
    const response = await axios.post('/get_test', { test_id: testId }).then((response) => {
      return response;
    });

    const data = response.data;
    console.log('Received response:', data);

    if (data['status'] === 'success') {
      this.test = {
        id: data.id,
        user_id: data.user_id,
        test_name: data.test_name,
        test_time: data.test_time,
        test_questions: data.test_questions,
        test_score: data.test_score,
        test_subjects: data.test_subjects,
        user_answers: data.user_answers,
        test_result_analysis: data.test_result_analysis,
      };

      // Open (or create) the IndexedDB
      const db = await openDB('HistoryTestDB', 1, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('tests')) {
            db.createObjectStore('tests', { keyPath: 'id', autoIncrement: true });
          }
        },
      });

      // Clear the database before adding new test details
      const tx = db.transaction('tests', 'readwrite');
      const store = tx.objectStore('tests');
      await store.clear();
      await store.add(this.test);
      await tx.done;

      console.log('Test details saved to IndexedDB:', this.test);
      this.$router.push('/historytestans');
    } else {
      console.error('Failed to fetch test data:', data.msg);
    }
  } catch (error) {
    console.error('Error fetching test details:', error);
  }
},
    removeQuotes(str) {
      return str.replace(/"/g, '');
    },
    formatDateTime(dateTimeStr) {
      return dateTimeStr.replace(' GMT', '');
    },
  },
};
</script>

<style lang="scss">
.self-test-history {
  font-family: Arial, sans-serif;
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    background-color: #3498db;
    color: #fff;
    h1 {
      font-size: 24px;
      margin: 0;
    }
    .back-button {
      background: none;
      border: none;
      cursor: pointer;
      color: #fff;
      font-size: 24px;
    }
  }
  .main {
    padding: 20px;
  }
  .scroll-panel {
    max-height: 400px;
    overflow-y: auto;
    .history-item {
      padding: 10px;
      cursor: pointer;
      transition: background-color 0.3s ease;
      &:hover {
        background-color: #f0f0f0;
      }
      &:not(:last-child) {
        border-bottom: 1px solid #ccc;
      }
      .item-info {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr;
        gap: 10px;
        .item-date, .item-subject, .item-topic, .item-score {
          white-space: nowrap; /* Prevent line break */
        }
      }
    }
    .title-row {
      background-color: #3498db;
      color: #fff;
      font-weight: bold;
    }
  }
}
</style>