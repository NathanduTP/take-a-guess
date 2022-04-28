<template>
  <div class="flex justify-center p-4 flex-col h-screen">
    <div class="py-6">
      <p class="text-center text-5xl py-1 text-white uppercase">Classement</p>
      <p class="text-center text-8xl py-1 text-white uppercase">Final</p>
    </div>

    <div class="flex flex-row pb-4 w-full gap-4">
      <button
        class="rounded-xl border-2 px-4 py-2 border-white w-1/2"
        @click="showDead = false"
      >
        <span class="uppercase text-2xl text-white">Survivants</span>
      </button>
      <button
        class="rounded-xl border-2 px-4 py-2 border-white w-1/2"
        @click="showDead = true"
      >
        <span class="uppercase text-2xl text-white">Morts</span>
      </button>
    </div>
    <div
      class="border-2 border-white rounded-xl flex flex-col gap-4 p-4 h-full overflow-x-scroll"
      v-if="!showDead"
    >
      <div
        class="flex flex-row text-white text-2xl"
        v-for="(user, i) in playersAlive"
        :key="user.id"
      >
        <div class="w-1/5">{{ i + 1 }}</div>
        <div class="w-3/5">{{ user.name }}</div>
        <div class="w-1/5">{{ user.points }} pts</div>
      </div>
    </div>
    <div
      class="border-2 border-white rounded-xl flex flex-col gap-4 p-4 h-full overflow-x-scroll"
      v-else
    >
      <div
        class="flex flex-row text-white text-2xl"
        v-for="(user, i) in deadPlayers"
        :key="user.id"
      >
        <div class="w-1/5">{{ i + 1 }}</div>
        <div class="w-3/5">{{ user.name }}</div>
        <div class="w-1/5">{{ user.points }} pts</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import Hearts from "@/components/Hearts.vue";
import { Player } from "@/constants/types";

@Component({
  components: {
    Hearts,
  },
})
export default class Leaderboard extends Vue {
  playersAlive: Player[] = [];
  deadPlayers: Player[] = [];
  showDead = false;

  mounted() {
    this.$socket.emit("get-players");

    /**
     * Ping the server to get a list of all the players
     */
    this.sockets.subscribe("get-players-response", (data) => {
      // Sort players by their points
      let sortedPlayers: Player[] = data.players.sort(
        (p1: Player, p2: Player) => {
          if (p1.points < p2.points) return 1; // Sort in dsc order
          if (p1.points > p2.points) return -1;
          return 0;
        }
      );

      // Keep players with al least one heart left
      this.playersAlive = sortedPlayers.filter((p: Player) => p.hearts > 0);

      // Keep the dead players
      this.deadPlayers = sortedPlayers.filter((p: Player) => p.hearts === 0);

      console.log("A:", this.playersAlive);
      console.log("D:", this.deadPlayers);
    });
  }
}
</script>
