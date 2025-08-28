<template>
  <div>
    <h2>Take a Picture</h2>
    <q-form @submit.prevent="submitPhoto">
      <div class="q-mb-md">
        <video ref="video" autoplay playsinline width="320" height="240" v-show="!photoData"></video>
        <canvas ref="canvas" width="320" height="240" style="display:none;"></canvas>
        <img v-if="photoData" :src="photoData" alt="Captured photo" width="320" height="240" class="q-mb-md" />
      </div>
      <q-btn
        label="Take Photo"
        color="primary"
        :disable="loading"
        @click="capturePhoto"
        v-if="!photoData"
        class="q-mb-md"
      />
      <q-btn
        label="Retake"
        color="secondary"
        :disable="loading"
        @click="retakePhoto"
        v-if="photoData"
        class="q-mb-md"
      />
      <q-btn
        label="Upload"
        type="submit"
        color="primary"
        :loading="loading"
        :disable="!photoData"
      />
    </q-form>
    <div v-if="message" class="q-mt-md">
      <q-banner :class="messageType === 'positive' ? 'bg-positive text-white' : 'bg-negative text-white'">
        {{ message }}
      </q-banner>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'UploadLink',
  setup() {
    const video = ref(null)
    const canvas = ref(null)
    const photoData = ref('')
    const loading = ref(false)
    const message = ref('')
    const messageType = ref('positive')
    let stream = null

    async function startCamera() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true })
        if (video.value) {
          video.value.srcObject = stream
        }
      } catch (err) {
        message.value = 'Cannot access camera: ' + err.message
        messageType.value = 'negative'
      }
    }

    function stopCamera() {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
        stream = null
      }
    }

    function capturePhoto() {
      if (!video.value || !canvas.value) return
      const ctx = canvas.value.getContext('2d')
      ctx.drawImage(video.value, 0, 0, canvas.value.width, canvas.value.height)
      photoData.value = canvas.value.toDataURL('image/png')
      stopCamera()
    }

    function retakePhoto() {
      photoData.value = ''
      startCamera()
    }

    async function submitPhoto() {
      if (!photoData.value) return
      loading.value = true
      message.value = ''
      try {
        const blob = await (await fetch(photoData.value)).blob()
        const formData = new FormData()
        formData.append('file', blob, 'photo.png')
        const response = await fetch('/upload', {
          method: 'POST',
          body: formData
        })
        if (!response.ok) throw new Error('Upload failed')
        const data = await response.json()
        message.value = data.message || 'Photo uploaded successfully'
        messageType.value = 'positive'
      } catch (err) {
        message.value = err.message
        messageType.value = 'negative'
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      startCamera()
    })

    onBeforeUnmount(() => {
      stopCamera()
    })

    return {
      video,
      canvas,
      photoData,
      loading,
      message,
      messageType,
      capturePhoto,
      retakePhoto,
      submitPhoto
    }
  }
}
</script>