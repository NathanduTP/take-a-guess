<template>
  <svg viewBox="0 0 36 36" class="w-40 h-40">
    <path
      d="M18 2.0845
      a 15.9155 15.9155 0 0 1 0 31.831
      a 15.9155 15.9155 0 0 1 0 -31.831"
      fill="none"
      stroke="currentColor"
      stroke-width="4"
      :stroke-dasharray="strokeDashArray()"
    />
  </svg>
</template>
<script lang="ts">
import { Component, Prop, Vue } from "vue-property-decorator";

@Component
export default class CircleProgress extends Vue {
  @Prop({ required: true }) readonly percent!: number;

  strokeDashArray() {
    return `${this.percent}, 100`;
  }
}
</script>
