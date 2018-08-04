<template>
  <div class="container has-text-centered">
    <div class="columns is-vcentered">
      <mascot class="column is-5"></mascot>
      <div class="column is-6 is-offset-1">
        <h1 class="title is-2">
          Authentication Error
        </h1>
        <h2 class="subtitle is-4">
          We had trouble logging you in.
        </h2>
      </div>
    </div>
  </div>
</template>

<script>
import Mascot from '@/components/Mascot'

export default {
  name: 'RegisterError',
  components: {
    Mascot
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
