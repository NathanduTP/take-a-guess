<template>
  <div class="flex justify-center p-4 flex-col h-screen">
    <hearts
      :left="heartsLeft"
      :total="hearts"
      v-if="hearts !== -1 && heartsLeft !== -1"
    />
    <p class="text-center text-5xl py-8 text-white uppercase">
      Question {{ question }}
    </p>
    <div class="my-8 h-full">
      <div class="p-4 grid gap-4 grid-cols-2 h-3/4">
        <answer-button
          answer="A"
          :selected="selectedAnswer === 'A'"
          @click.native="!hasAnswered && giveAnswer('A')"
        />
        <answer-button
          answer="B"
          :selected="selectedAnswer === 'B'"
          @click.native="!hasAnswered && giveAnswer('B')"
        />
        <answer-button
          answer="C"
          :selected="selectedAnswer === 'C'"
          @click.native="!hasAnswered && giveAnswer('C')"
        />
        <answer-button
          answer="D"
          :selected="selectedAnswer === 'D'"
          @click.native="!hasAnswered && giveAnswer('D')"
        />
      </div>

      <div class="flex justify-center items-center h-1/4">
        <circle-progress
          :class="hasAnswered ? 'hidden' : 'block'"
          class="text-[#5E17EB]"
          :percent="100 * (1 - (maxTime - timeLeft) / maxTime)"
        />
        <p
          class="text-4xl text-white uppercase"
          :class="hasAnswered ? 'block' : 'hidden'"
          v-if="isCorrect === true"
        >
          correct
        </p>
        <p
          class="text-4xl text-white uppercase text-center"
          :class="hasAnswered ? 'block' : 'hidden'"
          v-if="isCorrect === false"
        >
          raté ! <br />réponse: {{ rightAnswer }}
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import Hearts from "@/components/Hearts.vue";
import AnswerButton from "@/components/AnswerButton.vue";
import CircleProgress from "@/components/CircleProgress.vue";

@Component({
  components: {
    AnswerButton,
    CircleProgress,
    Hearts,
  },
})
export default class QuizzView extends Vue {
  hearts = -1; // Total hearts available
  heartsLeft = -1; // Player's hearts left

  question = ""; // The number of question
  hasAnswered = false; // Whether or not the player answered the question
  selectedAnswer = ""; // The player's selected answer
  isCorrect: boolean | null = null; // Whether or not the answer is correct
  rightAnswer = ""; // The right answer to the question

  maxTime = 0; // Time to answer the question
  timeLeft = Number.MAX_VALUE;
  startTime!: number;

  intervalId!: number;

  /**
   * When the component is mounted
   */
  mounted() {
    /**
     * 
    this.hearts = parseInt(this.$route.params.hearts);
    this.heartsLeft = parseInt(this.$route.params.heartsLeft);
    this.maxTime = parseInt(this.$route.params.timer);
    this.question = this.$route.params.question;
     */

    this.startTime = new Date().getTime();

    this.intervalId = setInterval(() => {
      this.timeLeft =
        this.maxTime - (new Date().getTime() - this.startTime) / 1000;
      if (this.timeLeft <= 0) {
        clearInterval(this.intervalId);
        this.giveAnswer("X");
      }
    }, 1000);

    this.$socket.emit("get-player-info");

    this.sockets.subscribe("get-player-info", (data) => {
      this.hearts = parseInt(data.hearts);
      this.heartsLeft = data.left;
      this.maxTime = data.timer;
      this.question = data.question;
    });

    this.sockets.subscribe("user-answer", (data) => {
      console.log("Data answer: ", data);
      this.heartsLeft = data.left;
      this.isCorrect = data.correct;
      this.rightAnswer = data.answer;
    });

    this.sockets.subscribe("next-question", () => {
      this.$router.push("be-ready");
    });

    this.sockets.subscribe("show-leaderboard", () => {
      this.$router.push("leaderboard");
    });
  }

  /**
   * Submit the player's answer
   */
  giveAnswer(answer: string) {
    this.selectedAnswer = answer;
    this.$socket.emit("user-answer", {
      answer: answer,
    });
    // TODO: Block answer and show results
    this.hasAnswered = true;

    // Kill the timer
    clearInterval(this.intervalId);
  }
}
</script>
