import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const hasDocument = ref(false)
  const documentId = ref<string | null>(null)
  const graphData = ref<any>(null)
  const activeNode = ref<string | null>(null)
  const physicsEnabled = ref(true)
  const learnedCount = ref(0)
  const totalScore = ref(0)
  const streak = ref(0)
  const currentQuiz = ref<any>(null)
  const nodeTitle = ref('')
  const nodeSummary = ref('')
  const nodeQuizzes = ref<any[]>([])

  const nodeCategory = computed(() => 'Topic')

  function setDocument(data: any) {
    hasDocument.value = true
    documentId.value = data.id
  }

  function setGraph(data: any) {
    graphData.value = data
  }

  function setActiveNode(id: string) {
    activeNode.value = id
  }

  function closePanel() {
    activeNode.value = null
    currentQuiz.value = null
  }

  function resetZoom() {
    // implemented by graph component reference
  }

  function togglePhysics() {
    physicsEnabled.value = !physicsEnabled.value
  }

  function openQuiz() {
    currentQuiz.value = { title: nodeTitle.value, questions: [] }
  }

  return {
    hasDocument, documentId, graphData,
    activeNode, physicsEnabled, learnedCount, totalScore, streak, currentQuiz,
    nodeTitle, nodeSummary, nodeCategory, nodeQuizzes,
    setDocument, setGraph, setActiveNode, closePanel,
    resetZoom, togglePhysics, openQuiz
  }
})
