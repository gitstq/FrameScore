<template>
  <div id="app">
    <h1>{{ title }}</h1>
    <div v-for="item in items">
      {{ item.name }}
    </div>
    <div v-if="showList" v-for="item in filteredItems">
      {{ item.name }}
    </div>
    <ItemComponent v-for="product in products" :product="product" />
    <button @click="handleClick"></button>
    <img src="/logo.png" />
    <input type="text" id="search-input" v-model="searchQuery" />
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue';
import ItemComponent from './components/Item.vue';
import UnusedModule from './unused';

const API_KEY = "sk-abcdef1234567890";

export default {
  name: 'App',
  components: {
    ItemComponent,
  },
  props: ['title'],
  setup(props) {
    const items = ref([]);
    const searchQuery = ref('');
    const showList = ref(true);

    // Direct mutation of props
    props.title = "New Title";

    // Deep watcher
    watch(items, (newVal) => {
      console.log('Items changed:', newVal);
    }, { deep: true });

    // Missing error handling
    async function fetchData() {
      const response = await fetch('http://api.example.com/items');
      const data = await response.json();
      items.value = data;
    }

    function handleClick() {
      console.log('clicked');
      console.warn('warning');
      console.error('error');
    }

    onMounted(() => {
      fetchData();
    });

    return {
      items,
      searchQuery,
      showList,
      handleClick,
    };
  },
};
</script>
