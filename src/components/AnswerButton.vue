<template>
  <div
    class="flex justify-center items-center bg-white roundy fancy-shadow"
    :class="
      selected ? 'border-yellow-500 border-8' : 'border-[#5E17EB] border-2'
    "
  >
    <span
      class="text-gray-600 text-6xl"
      :class="selected && 'text-yellow-500'"
      >{{ answer }}</span
    >
  </div>
</template>
<script lang="ts">
import { Vue, Prop, Component } from "vue-property-decorator";

@Component
export default class AnswerButton extends Vue {
  @Prop({ required: true }) readonly answer!: string;
  @Prop({ required: false }) readonly selected!: boolean;
}
</script>
<style>
.roundy {
  border-radius: 50px;
}
</style>
