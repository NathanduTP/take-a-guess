<template>
  <div class="flex justify-center p-4 flex-col h-screen">
    <p class="text-center text-5xl py-8 text-white uppercase">Stats</p>
    <div class="border-white rounded-xl flex flex-col gap-4 h-full">
      <div>
        <p class="text-center text-xl text-white">
          Joueur en lice: {{ playersStillAlive() }}
        </p>
        <apexchart type="bar" :options="options" :series="alive"></apexchart>
      </div>
      <div>
        <p class="text-center text-xl text-white">
          Joueur spectateur: {{ deadPlayers() }}
        </p>
        <apexchart type="bar" :options="options" :series="dead"></apexchart>
      </div>
    </div>
  </div>
</template>
<script lang="ts">
import { Component, Vue } from "vue-property-decorator";

@Component({
  components: {},
})
export default class PlayerStatsView extends Vue {
  chartTitle1 = "Answers among the remaining players";
  chartTitle2 = "Answers among the eliminated players";

  options = {
    bar: {
      horizontal: true,
    },
    chart: {
      id: "vuechart-example",
      toolbar: {
        show: false,
      },
    },
    grid: {
      show: false,
    },
    legend: {
      show: false,
    },
    plotOptions: {
      bar: {
        borderRadius: 4,
        horizontal: true,
      },
    },
    xaxis: {
      categories: ["A", "B", "C", "D", "X"],
      lines: {
        show: false,
      },
      labels: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        style: ["#000"],
      },
      lines: {
        show: false,
      },
    },
  };
  alive = [
    {
      name: this.chartTitle1,
      data: [],
    },
  ];
  dead = [
    {
      name: this.chartTitle2,
      data: [],
    },
  ];

  onDataUpdate(data: Record<string, any>) {
    this.alive = [
      {
        name: this.chartTitle1,
        data: data.alive,
      },
    ];

    this.dead = [
      {
        name: this.chartTitle2,
        data: data.dead,
      },
    ];
  }

  mounted() {
    // Refresh values when mounted
    this.$socket.emit("get-update-answers");

    this.sockets.subscribe("get-update-answers-response", this.onDataUpdate);
    this.sockets.subscribe("update-answers", this.onDataUpdate);
  }

  /**
   * Count the number of player still alive
   */
  playersStillAlive() {
    return this.alive[0].data.reduce((a, b) => a + b, 0);
  }

  /**
   * Count the number of dead player
   */
  deadPlayers() {
    return this.dead[0].data.reduce((a, b) => a + b, 0);
  }
}
</script>
