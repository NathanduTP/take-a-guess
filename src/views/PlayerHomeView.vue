<template>
  <div class="root">
    <div class="logo">
      <img
        src="../assets/images/logo-battle-royale-culture-g.png"
        alt="Battle Royale de la Culture Générale"
        width="110%"
      />
    </div>

    <div class="pseudo">Pseudo :</div>

    <div class="form">
      <input
        @change="onPseudoChange"
        type="text"
        name="pseudo-input"
        class="pseudo-input"
        placeholder="Pseudo"
      />
    </div>

    <div class="butt">
      <button @click="onGoClick" class="button">
        <span>GO !</span>
      </button>
    </div>

    <div class="logo1">
      <div class="logos">
        <img
          src="../assets/images/logo-club-culture-inge.png"
          alt="Logo du club culture ingé"
        />
        <img src="../assets/images/hero-logo.svg" alt="Logo du club info" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from "vue-property-decorator";
import LogoClubInfo from "@/components/LogoClubInfo.vue";

@Component({
  components: {
    LogoClubInfo,
  },
})
export default class PlayerHomeView extends Vue {
  username!: string;

  onPseudoChange(event: any) {
    if (event.target.value) {
      this.username = event.target.value;
    }
  }

  /**
   * Ping the server to join the room
   */
  onGoClick() {
    if (this.username) {
      this.$socket.emit("join-room", {
        username: this.username,
      });
    }
  }

  mounted() {
    /**
     * Send the player to the waiting room once he joined the room
     */
    this.sockets.subscribe("join-room", (data) => {
      if (data.status === "success") {
        this.$router.push({ name: "waiting" });
      }
    });
  }
}
</script>
