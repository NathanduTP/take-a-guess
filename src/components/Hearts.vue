<template>
  <div
    class="flex w-full justify-between text-white bg-white border rounded-xl bg-opacity-30 p-2 mb-8"
  >
    <p class="text-2xl uppercase font-bold">Vies</p>
    <div class="flex flex-row items-center gap-x-2">
      <!-- Lifes consummed -->
      <font-awesome-icon
        icon="fa-regular fa-heart"
        :key="brokenHeartId(j)"
        v-for="j in total - left"
        size="xl"
      />

      <!-- Lifes left -->
      <font-awesome-icon
        icon="fa-solid fa-heart"
        :key="HeartLeftId(i)"
        v-for="i in left"
        size="xl"
      />
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";

@Component
export default class Hearts extends Vue {
  @Prop({ required: true, default: 0 }) readonly left!: number;
  @Prop({ required: true, default: 0 }) readonly total!: number;

  brokenHeartId(i: number) {
    return `broken-${i}`;
  }

  HeartLeftId(i: number) {
    return `heart-${i}`;
  }
}
</script>
