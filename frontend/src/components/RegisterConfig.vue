<template>
  <div class="container has-text-centered">
    <div class="columns is-vcentered">
      <mascot class="column is-5"></mascot>
      <div class="column is-6 is-offset-1">
        <transition name="fade">
          <div v-if="configComplete">
            <h1 class="title is-2">
              You're all set up 🎉
            </h1>
            <h2 class="subtitle is-4">
              Your TimePro credentials have been securely stored and ready for Timmy to help you with your timesheets. Hooray!
            </h2>
          </div>
          <div v-else>
            <h1 class="title is-2">
              Configure TimePro
            </h1>
            <h2 class="subtitle is-4">
              Enter your TimePro Timesheets username and password.
            </h2>
            <br>
            <b-notification type="is-danger" v-if="errorMessage" class="form-errors">
              {{ errorMessage }}
            </b-notification>
            <section class="timepro-form">
              <form @submit="checkForm">
                <b-field>
                  <b-input placeholder="SERV" type="text" icon="domain" disabled v-model="customer">
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
        </transition>
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
      customer: 'SERV',
      formLoading: false,
      buttonLabel: 'Submit',
      buttonDisabled: false,
      buttonClass: 'is-primary',
      state: null,
      errorMessage: '',
      configComplete: false
    }
  },
  methods: {
    checkForm: function (e) {
      e.preventDefault()
      this.formLoading = this.buttonDisabled = true
      let body = {
        'username': this.username,
        'password': this.password,
        'customer': this.customer,
        'state': this.state
      }
      this.$http.post('https://api.timesheets.servian.fun/v1/timepro/config', body)
        .then((response) => {
          console.log(response.body)
          this.formLoading = false
          this.configComplete = True
        })
        .catch((response) => {
          console.log(response.body)
          this.errorMessage = response.body.error
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
.form-errors {
  margin: 2rem 1rem;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
