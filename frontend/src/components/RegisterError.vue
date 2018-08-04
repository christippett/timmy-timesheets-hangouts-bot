<template>
  <div class="error">
    <h1>Error!</h1>
    <h2>{{ errorDescription }}</h2>
    <ul>
      <li>
        <a href="/">Home</a>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'RegisterError',
  data () {
    return {
      errorDescription: 'Could not authenticate user.'
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
