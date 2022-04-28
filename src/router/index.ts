import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";

import PlayeyHomeView from "@/views/PlayerHomeView.vue";
import PlayerWaitingRoomView from "@/views/PlayerWaitingRoomView.vue";
import PlayerBeReadyView from "@/views/PlayerBeReadyView.vue";
import PlayerQuizzView from "@/views/PlayerQuizzView.vue";
import PlayerStatsView from "@/views/PlayerStatsView.vue";

import AdminWaitingRoomView from "@/views/AdminWaitingRoomView.vue";
import AdminSettingQuestionView from "@/views/AdminSettingQuestionView.vue";
import AdminStatsView from "@/views/AdminStatsView.vue";
import AdminHomeView from "@/views/AdminHomeView.vue";

import LeaderboardView from "@/views/LeaderboardView.vue";

Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
  {
    path: "/",
    name: "home",
    component: PlayeyHomeView,
  },
  {
    path: "/waiting",
    name: "waiting",
    component: PlayerWaitingRoomView,
  },
  {
    path: "/be-ready",
    name: "beReady",
    component: PlayerBeReadyView,
  },
  {
    path: "/quizz",
    name: "quizz",
    component: PlayerQuizzView,
  },
  {
    path: "/stats",
    name: "stats",
    component: PlayerStatsView,
  },
  {
    path: "/leaderboard",
    name: "leaderboard",
    component: LeaderboardView,
  },
  {
    path: "/admin-home",
    name: "admin-home",
    component: AdminHomeView,
  },
  {
    path: "/admin-waiting",
    name: "admin-waiting",
    component: AdminWaitingRoomView,
  },
  {
    path: "/admin-question-settings",
    name: "admin-question-settings",
    component: AdminSettingQuestionView,
  },
  {
    path: "/admin-stats",
    name: "admin-stats",
    component: AdminStatsView,
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

export default router;
