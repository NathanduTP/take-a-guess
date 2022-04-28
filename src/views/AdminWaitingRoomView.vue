<template>
  <div class="flex justify-center p-4 flex-col h-screen">
    <p class="text-center text-4xl py-1 text-white uppercase">
      Salle d'attente
    </p>
    <div
      class="relative border-2 border-white rounded-xl flex flex-col gap-4 h-full overflow-x-scroll"
    >
      <span
        class="md:text-4xl text-3xl text-center text-white"
        v-for="user in users"
        :key="user.id"
        >{{ user.name }}</span
      >
    </div>
    <button
      class="absolute bottom-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 p-4 bg-[#E40495] border-[#5E17EB] border-2 rounded-3xl fancy-shadow"
      :class="users.length ? 'block' : 'hidden'"
      @click="prepareQuestion"
    >
      <span class="uppercase text-3xl text-white">Go !</span>
    </button>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";
import { Player } from "@/constants/types";

@Component
export default class AdminWaitingRoomView extends Vue {
  private users: Player[] = [];

  mounted() {
    this.sockets.subscribe("user-joined", (data) => {
      this.users = data.players;
    });

    this.sockets.subscribe("lock-room-response", () => {
      this.$router.push({ name: "admin-question-settings" });
    });
  }

  prepareQuestion() {
    if (this.users.length) {
      this.$socket.emit("lock-room");
    }
  }
}
</script>
