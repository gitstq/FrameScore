<template>
  <div class="item">
    <span>{{ product.name }}</span>
    <span>{{ product.price }}</span>
    <div v-for="tag in product.tags">
      {{ tag }}
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  name: 'Item',
  props: ['product'],
  setup(props) {
    const quantity = ref(1);

    // Direct mutation of prop
    props.product.name = "Modified";

    function increment() {
      quantity.value++;
      console.log('incremented');
    }

    return {
      quantity,
      increment,
    };
  },
};
</script>
