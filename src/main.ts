import Vue from "vue";
import App from "./App.vue";
import router from "./router";

import { library } from "@fortawesome/fontawesome-svg-core";
import { faHeart as fasHeart } from "@fortawesome/free-solid-svg-icons";
import { faHeart as farHeart } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import VueApexCharts from "vue-apexcharts";
import VueSocketIO from "vue-socket.io";

import "./index.css";

Vue.config.productionTip = false;
library.add(fasHeart);
library.add(farHeart);

// eslint-disable-next-line vue/multi-word-component-names
Vue.component("apexchart", VueApexCharts);
Vue.component("font-awesome-icon", FontAwesomeIcon);

Vue.use(VueApexCharts);

Vue.use(
  new VueSocketIO({
    debug: true,
    connection: "http://localhost:3001",
  })
);

new Vue({
  router,
  render: (h) => h(App),
  components: {},
  sockets: {
    connect: () => {
      console.log("Connected");
    },
  },
}).$mount("#app");
