<template>
  <div class="flex justify-center p-4 flex-col h-screen">
    <hearts :left="hearts" :total="hearts" />
    <p class="text-center text-4xl py-1 text-white uppercase">
      Salle d'attente
    </p>
    <div
      class="border-2 border-white rounded-xl flex flex-col gap-4 h-full overflow-x-scroll"
    >
      <span
        class="text-2xl text-center text-white"
        v-for="user in users"
        :key="user.id"
        >{{ user.name }}</span
      >
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
export default class WaitingRoomView extends Vue {
  private users: Player[] = [];
  private hearts = 0;
  private question = 0;

  mounted() {
    // Whenever a player joined the room
    this.sockets.subscribe("user-joined", (data) => {
      this.users = data.players;
    });

    // Ping the server to get room info
    this.$socket.emit("get-game-info");

    // Response the above ping
    this.sockets.subscribe("get-game-info", (data) => {
      this.users = data.players;
      this.hearts = parseInt(data.settings.lives);
      this.question = parseInt(data.question);
    });

    // Whenever the admin is preparing the (next) question
    this.sockets.subscribe("be-ready", () => {
      this.$router.push({
        name: "beReady",
      });
    });
  }
}
</script>
