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
          alert('用户不存在，请先注册');
        }
      } catch (error) {
        console.error('登录失败:', error);
      }
    },
    async register() {
      // 注册逻辑
      console.log('注册用户名:', this.username);
      console.log('注册密码:', this.password);

      // 发送 POST 请求到后端注册接口
      try {
        const response = await axios.post('http://localhost:5000/create_user', {
          username: this.username,
          password: this.password, // 假设后端也需要密码
        });

        if (response.data.status === 'success') {
          alert('注册成功');
          const userId = response.data.user_id;

          // 将用户名和 user_id 保存在 IndexedDB 中
          await this.saveUserToIndexedDB(this.username, userId);

          // 跳转到登录页面或其他页面
          // this.$router.push('/index');
        } else {
          alert('注册失败: ' + response.data.msg);
        }
      } catch (error) {
        console.error('注册请求失败:', error);
        alert('注册请求失败');
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
      
      // 清空现有数据
      await store.clear();
      
      // 存储新数据
      await store.put({ username, userId });
      await tx.done;
      console.log('用户数据已保存到 IndexedDB');
    },
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
</style>
