import { defineStore } from 'pinia'
import { ref } from 'vue'

const TOUR_KEY = 'tf_tour_v1_concluido'

export const useUiStore = defineStore('ui', () => {
  const notificacoesNaoLidas = ref(0)
  const ocrDisponivel = ref(false)
  const socModeActive = ref(false)

  function tourConcluido() {
    return localStorage.getItem(TOUR_KEY) === '1'
  }

  function marcarTourConcluido() {
    localStorage.setItem(TOUR_KEY, '1')
  }

  function reiniciarTour() {
    localStorage.removeItem(TOUR_KEY)
  }

  return {
    notificacoesNaoLidas,
    ocrDisponivel,
    socModeActive,
    tourConcluido,
    marcarTourConcluido,
    reiniciarTour,
  }
})
