<template>
  <q-layout view="hHh lpR fFf" class="shadow-2">
    <q-header elevated :class="$q.dark.isActive ? 'bg-secondary' : 'bg-black'">
      <q-toolbar>
        <q-btn flat @click="drawer = !drawer" round dense icon="menu" />
        <q-toolbar-title>KAMIDAR</q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="drawer"
      show-if-above
      :mini="miniState"
      @mouseenter="miniState = false"
      @mouseleave="miniState = true"
      :width="200"
      :breakpoint="500"
      bordered
      :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-3'"
    >
      <q-scroll-area class="fit" :horizontal-thumb-style="{ opacity: 0 }">
        <q-list padding>

          <q-item clickable v-ripple @click="selectedComponent = 'Upload'">
            <q-item-section avatar>
              <q-icon name="add_to_home_screen" />
            </q-item-section>
            <q-item-section>
              Upload
            </q-item-section>
          </q-item>     
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <q-page-container>
      <q-page padding>
        <div v-if="selectedComponent === 'Upload'">
          <UploadLink />
        </div>
        <div v-else>
          <div>Welcome! Please select an item from the menu.</div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
import { ref } from 'vue'
import UploadLink from 'components/UploadLink.vue'


export default {
  components: {
    UploadLink
  },
  setup () {
    const drawer = ref(false)
    const miniState = ref(true)
    const selectedComponent = ref('Apps') // Default selection

    return {
      drawer,
      miniState,
      selectedComponent
    }
  }
}
</script>