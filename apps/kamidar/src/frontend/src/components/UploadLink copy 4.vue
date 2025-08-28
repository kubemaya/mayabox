<template>
  <div>
    <h2>Take a Picture</h2>
    <q-form @submit.prevent="submitPhoto">
      <div class="q-mb-md">
        <video ref="video" autoplay playsinline width="320" height="240" v-show="!photoData"></video>
        <canvas ref="canvas" width="320" height="240" style="display:none;"></canvas>
        <img
          v-if="photoData"
          :src="photoData"
          alt="Captured photo"
          width="320"
          height="240"
          class="q-mb-md"
          @click="getPixelColor"
          ref="img"
          style="cursor: crosshair;"
        />
        <div v-if="pixelColor" class="q-mb-md">
          <span>Selected Pixel Color:</span>
          <span :style="{background: pixelColor, color: '#fff', padding: '2px 8px', borderRadius: '4px'}">{{ pixelColor }}</span>
        </div>
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
      <q-input
        v-if="outputText"
        type="textarea"
        label="Analysis Output"
        v-model="outputText"
        readonly
        class="q-mt-md"
        autogrow
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
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

export default {
  name: 'UploadLink',
  setup() {
    const video = ref(null)
    const canvas = ref(null)
    const photoData = ref('')
    const loading = ref(false)
    const message = ref('')
    const messageType = ref('positive')
    const pixelColor = ref('')
    const img = ref(null)
    const outputText = ref('')
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
      pixelColor.value = ''
      nextTick(() => {
        if (img.value) {
          img.value.addEventListener('click', getPixelColor)
        }
      })
    }

    function retakePhoto() {
      photoData.value = ''
      pixelColor.value = ''
      outputText.value = ''
      startCamera()
    }

    function getPixelColor(event) {
      if (!img.value || !canvas.value) return
      const ctx = canvas.value.getContext('2d')
      const image = new window.Image()
      image.src = photoData.value
      image.onload = function() {
        ctx.drawImage(image, 0, 0, canvas.value.width, canvas.value.height)
        const rect = img.value.getBoundingClientRect()
        const x = Math.floor((event.clientX - rect.left) * (canvas.value.width / rect.width))
        const y = Math.floor((event.clientY - rect.top) * (canvas.value.height / rect.height))
        const pixel = ctx.getImageData(x, y, 1, 1).data
        const hex = "#" + ((1 << 24) + (pixel[0] << 16) + (pixel[1] << 8) + pixel[2]).toString(16).slice(1).toUpperCase()
        pixelColor.value = hex
      }
    }

    async function submitPhoto() {
      if (!photoData.value) return
      loading.value = true
      message.value = ''
      outputText.value = ''
      try {
        const blob = await (await fetch(photoData.value)).blob()
        const formData = new FormData()
        formData.append('file', blob, 'photo.png')
        if (pixelColor.value) {
          formData.append('color', pixelColor.value)
        }
        const response = await fetch('/upload', {
          method: 'POST',
          body: formData
        })
        if (!response.ok) throw new Error('Upload failed')
        const data = await response.json()
        console.log(data)
        message.value = data.message || 'Photo uploaded successfully & processed'
        messageType.value = 'positive'
        // Format output from data.data
        if (data.data && typeof data.data === 'object') {
          outputText.value = Object.entries(data.data)
            .map(([key, value]) => `${key}: ${value}`)
            .join('\n')
        }
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
      pixelColor,
      img,
      outputText,
      capturePhoto,
      retakePhoto,
      getPixelColor,
      submitPhoto
    }
  }
}
</script>