<template>
  <nav class="navbar">
    <div class="container">
      <div class="navbar-brand">
        <a class="navbar-item" href="../">
          <img src="../assets/servian-logo.png" alt="Logo" class="logo">
        </a>
        <span class="navbar-burger burger" v-bind:class="{ 'is-active': navbarActive }" @click="navbarActive = !navbarActive">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </div>
      <div id="navbarMenu" class="navbar-menu" v-bind:class="{ 'is-active': navbarActive }">
        <div class="navbar-end">
          <div class="tabs is-right">
            <ul>
              <router-link tag="li" to="/">
                <a>Home</a>
              </router-link>
              <li>
                <a href="https://timesheets.com.au" target="_blank">Timesheets</a>
              </li>
              <li>
                <a href="https://chat.google.com" target="_blank">Chat</a>
              </li>
              <li>
                <a href="https://source.servian.com/AWS_Melbourne_Hackathon_2018/Team_2" target="_blank">GitLab</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavBar',
  data () {
    return {
      navbarActive: false
    }
  }
}
</script>
