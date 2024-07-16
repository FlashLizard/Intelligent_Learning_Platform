<template>
  <div class="login-page">
    <div class="login-container">
      <h1>智能教育系统</h1>
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="username">用户名</label>
          <input type="text" id="username" v-model="username" required />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <div class="button-group">
          <button type="submit" class="animated-button">登录</button>
          <button @click="register" class="animated-button register-button">注册</button>
        </div>
      </form>
      <!-- 自定义弹窗 -->
      <div v-if="dialogVisible" class="dialog-overlay">
        <div class="dialog-content">
          <h2>{{ dialogMessage }}</h2>
          <button @click="handleDialogClose">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { openDB } from 'idb';

export default {
  data() {
    return {
      username: '',
      password: '',
      dialogMessage: '',
      dialogVisible: false,
      loading: false,
    };
  },
  methods: {
    async login() {
      try {
        const response = await fetch('http://localhost:5000/get_user_id', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username: this.username }),
        });

        const data = await response.json();

        if (data.status === 'success') {
          const userId = data.user_id;
          await this.saveUserToIndexedDB(this.username, userId);
          this.$router.push('/index');
        } else {
          this.dialogMessage = '用户不存在，请先注册';
          this.dialogVisible = true;
        }
      } catch (error) {
        console.error('登录失败:', error);
      }
    },
    async register() {
      console.log('注册用户名:', this.username);
      console.log('注册密码:', this.password);

      try {
        this.loading = true;
        const response = await axios.post('http://localhost:5000/create_user', {
          username: this.username,
          password: this.password,
        });

        this.loading = false;

        if (response.data.status === 'success') {
          this.dialogMessage = '注册成功';
          const userId = response.data.user_id;
          await this.saveUserToIndexedDB(this.username, userId);
          this.dialogVisible = true;
        } else {
          this.dialogMessage = '注册失败: ' + response.data.msg;
          this.dialogVisible = true;
        }
      } catch (error) {
        this.loading = false;
        console.error('注册请求失败:', error);
        this.dialogMessage = '注册请求失败';
        this.dialogVisible = true;
      }
    },
    async saveUserToIndexedDB(username, userId) {
      const db = await openDB('UserDatabase', 1, {
        upgrade(db) {
          if (!db.objectStoreNames.contains('users')) {
            db.createObjectStore('users', {
              keyPath: 'id',
              autoIncrement: true,
            });
          }
        },
      });

      const tx = db.transaction('users', 'readwrite');
      const store = tx.objectStore('users');
      await store.clear();
      await store.put({ username, userId });
      await tx.done;
      console.log('用户数据已保存到 IndexedDB');
    },
    handleDialogClose() {
      this.dialogVisible = false;
    }
  },
};
</script>

<style lang="scss" scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
  font-family: 'Arial', sans-serif;
}

.login-container {
  background-color: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 75%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

h1 {
  margin-top: 5px;
  margin-bottom: 40px;
  color: #2e83df;
  font-size: 2.5em;
}

.form-group {
  margin-bottom: 30px;
  text-align: left;
  width: 100%;
}

label {
  display: block;
  margin-bottom: 10px;
  color: #4facfe;
  font-weight: bold;
  font-size: 1.2em;
}

input[type='text'],
input[type='password'] {
  width: 100%;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
  font-size: 1.1em;
}

.button-group {
  width: 100%;
  display: flex;
  justify-content: space-between;
}

button {
  width: calc(50% - 10px); /* 计算按钮宽度，减去间距 */
  padding: 15px;
  background-color: rgba(10, 132, 238, 0.8); /* 变淡的背景颜色 */
  border: none;
  border-radius: 5px;
  color: white;
  font-size: 1.2em;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: rgba(36, 168, 234, 0.8); /* 悬停时变淡的背景颜色 */
}

.animated-button {
  position: relative;
  overflow: hidden;
}

.animated-button span {
  position: absolute;
  display: block;
}

.animated-button span.border-top {
  top: 0;
  left: -100%;
  width: 100%;
  height: 4px;
  animation: animate-top 2s linear infinite;
  animation-delay: 0.0s;
  background: linear-gradient(90deg, transparent, #03e9f4);
}

.animated-button span.border-right {
  top: -100%;
  right: 0;
  width: 4px;
  height: 100%;
  animation: animate-right 2s linear infinite;
  animation-delay: 0.5s;
  background: linear-gradient(180deg, transparent, #03e9f4);
}

.animated-button span.border-bottom {
  bottom: 0;
  left: -100%;
  width: 100%;
  height: 4px;
  animation: animate-bottom 2s linear infinite;
  animation-delay: 1s;
  background: linear-gradient(90deg, #03e9f4, transparent);
}

.animated-button span.border-left {
  bottom: -100%;
  left: 0;
  width: 4px;
  height: 100%;
  animation: animate-left 2s linear infinite;
  animation-delay: 1.5s;
  background: linear-gradient(0deg, transparent, #03e9f4);
}

@keyframes animate-top {
  0% {
    left: -100%;
    background-size: 0% 100%;
  }
  50% {
    left: 100%;
    background-size: 100% 100%;
  }
  100% {
    left: 100%;
    background-size: 0% 100%;
  }
}

@keyframes animate-right {
  0% {
    top: -100%;
    background-size: 100% 0%;
  }
  50% {
    top: 100%;
    background-size: 100% 100%;
  }
  100% {
    top: 100%;
    background-size: 100% 0%;
  }
}

@keyframes animate-bottom {
  0% {
    left: 100%;
    background-size: 0% 100%;
  }
  50% {
    left: -100%;
    background-size: 100% 100%;
  }
  100% {
    left: -100%;
    background-size: 0% 100%;
  }
}

@keyframes animate-left {
  0% {
    bottom: -100%;
    background-size: 100% 0%;
  }
  50% {
    bottom: 100%;
    background-size: 100% 100%;
  }
  100% {
    bottom: 100%;
    background-size: 100% 0%;
  }
}

.loading-dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-content {
  background: white;
  padding: 20px;
  border-radius: 5px;
  text-align: center;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  padding: 20px;
  border-radius: 5px;
  text-align: center;
}

button {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #4facfe;
  border: none;
  border-radius: 5px;
  color: white;
  font-size: 1em;
  cursor: pointer;
}

button:hover {
  background-color: #2e83df;
}
</style>
