<template>
  <div class="container has-text-centered">
    <div class="columns is-vcentered">
      <mascot class="column is-5"></mascot>
      <div class="column is-6 is-offset-1">
        <h1 class="title is-2">
          Configure TimePro
        </h1>
        <h2 class="subtitle is-4">
          Enter your TimePro Timesheets username and password.
        </h2>
        <br>
        <section class="timepro-form">
          <form @submit="checkForm">
            <b-field>
              <b-input placeholder="SERV" type="text" icon="domain" disabled v-model="company">
              </b-input>
            </b-field>
            <b-field>
              <b-input placeholder="Username" type="username" icon="account" v-model="username">
              </b-input>
            </b-field>
            <b-field>
              <b-input placeholder="Password" type="password" icon="lock" v-model="password">
              </b-input>
            </b-field>
            <div class="control">
              <button type="submit" class="button" v-bind:class="[{ 'is-loading': formLoading }, buttonClass]" :disabled="buttonDisabled">{{ buttonLabel }}</button>
            </div>
          </form>
        </section>
      </div>
    </div>
  </div>
</template>

<script>
import Mascot from '@/components/Mascot'

export default {
  name: 'RegisterConfig',
  created: function () {
    this.state = this.$route.query.state
    if (this.state === undefined) {
      this.$router.push('/')
    }
  },
  data () {
    return {
      username: '',
      password: '',
      company: 'SERV',
      formLoading: false,
      buttonLabel: 'Submit',
      buttonDisabled: false,
      buttonClass: 'is-primary',
      state: null
    }
  },
  methods: {
    checkForm: function (e) {
      e.preventDefault()
      this.formLoading = this.buttonDisabled = true
      let body = {
        'username': this.username,
        'password': this.password,
        'company': this.company,
        'state': this.state
      }
      this.$http.post('http://127.0.0.1:8000/timepro/config', body)
        .then((response) => {
          console.log(response.body)
          this.formLoading = false
          this.buttonLabel = 'Success!'
          this.buttonClass = 'is-success'
        })
        .catch((response) => {
          console.log('error')
          this.formLoading = this.buttonDisabled = false
        })
    }
  },
  components: {
    Mascot
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.timepro-form {
  padding: 0 5rem;
}
</style>
