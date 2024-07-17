<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>

import axios from 'axios';
import config from '../config';
axios.defaults.baseURL = config.baseurl;
export default {
  components: {
  }
};
</script>

<style>
/* 这里可以放置全局样式 */
</style>
