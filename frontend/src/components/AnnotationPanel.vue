<template>
  <div class="bg-slate-800 rounded-lg border border-slate-700 flex flex-col" style="height: 100%;">
    <div class="flex items-center justify-between px-4 py-3 border-b border-slate-700">
      <div class="flex items-center gap-2">
        <span class="text-amber-400">💬</span>
        <h3 class="text-sm font-bold text-slate-300">协作批注</h3>
        <span class="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full">
          {{ store.activeAnnotations.length }}
        </span>
      </div>
      <div class="flex items-center gap-1">
        <span v-if="!store.apiAvailable" class="text-xs text-orange-400 mr-2" title="后端API未连接，使用本地存储">📁 本地模式</span>
        <button @click="showResolved = !showResolved" class="text-xs text-slate-400 hover:text-slate-200 px-2 py-1 rounded hover:bg-slate-700">
          {{ showResolved ? '隐藏已解决' : `已解决(${store.resolvedAnnotations.length})` }}
        </button>
      </div>
    </div>

    <div v-if="store.pendingAnnotationPosition" class="mx-4 mt-3 p-2 bg-amber-500/10 border border-amber-500/40 rounded text-xs text-amber-300 flex items-center justify-between">
      <span>📍 已关联 {{ chartTypeName(store.pendingAnnotationPosition.chartType) }}
        <span v-if="store.pendingAnnotationPosition.dataIndex !== undefined">#{{ store.pendingAnnotationPosition.dataIndex }}</span>
        <span v-if="store.pendingAnnotationPosition.xValue !== undefined"> (x={{ store.pendingAnnotationPosition.xValue.toFixed(2) }})</span>
      </span>
      <button @click="store.setPendingPosition(null)" class="text-slate-400 hover:text-white">✕</button>
    </div>

    <div class="px-4 py-3 border-b border-slate-700">
      <div class="space-y-2">
        <div class="flex gap-2">
          <input v-model="newAuthor" type="text" placeholder="你的名字" maxlength="20"
            class="flex-1 bg-slate-900 border border-slate-600 rounded px-2 py-1.5 text-xs focus:outline-none focus:border-cyan-500" />
        </div>
        <textarea v-model="newContent" placeholder="写下你的批注意见、讨论或反馈..." rows="3"
          class="w-full bg-slate-900 border border-slate-600 rounded px-2 py-1.5 text-xs focus:outline-none focus:border-cyan-500 resize-none"></textarea>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1">
            <button v-if="!store.pendingAnnotationPosition" @click="pickMode = !pickMode"
              :class="['text-xs px-2 py-1 rounded border transition-all', pickMode ? 'bg-cyan-600 border-cyan-500 text-white' : 'bg-slate-700 border-slate-600 text-slate-300 hover:border-slate-500']">
              {{ pickMode ? '📌 选择中...点击图表' : '📍 关联图表位置' }}
            </button>
            <span v-if="pickMode && !store.pendingAnnotationPosition" class="text-xs text-cyan-400 animate-pulse">请点击下方图表</span>
          </div>
          <button @click="submitAnnotation" :disabled="!newContent.trim() || !newAuthor.trim()"
            class="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed rounded text-xs font-bold text-white">
            添加批注
          </button>
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto p-4 space-y-3">
      <div v-if="store.activeAnnotations.length === 0 && (!showResolved || store.resolvedAnnotations.length === 0)"
        class="text-center py-8 text-slate-500 text-xs">
        <div class="text-3xl mb-2 opacity-30">📝</div>
        <div>暂无批注，来添加第一条吧！</div>
        <div class="mt-1 text-slate-600">你可以对整个实验结果评论，或点击"关联图表位置"对具体数据点批注</div>
      </div>

      <template v-for="a in sortedActiveAnnotations" :key="a.id">
        <div @click="selectAndScroll(a)"
          :class="['rounded-lg border p-3 cursor-pointer transition-all group',
            store.selectedAnnotationId === a.id ? 'border-cyan-500 bg-cyan-900/20 ring-1 ring-cyan-500/50' : 'border-slate-700 bg-slate-900/50 hover:border-slate-500']">
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-2">
              <div class="w-6 h-6 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center text-xs font-bold text-white">
                {{ a.author.charAt(0).toUpperCase() }}
              </div>
              <span class="text-xs font-bold text-slate-200">{{ a.author }}</span>
              <span v-if="a.position" @click.stop="selectAndScroll(a)"
                class="text-xs bg-purple-500/20 text-purple-300 px-1.5 py-0.5 rounded hover:bg-purple-500/30">
                📍 {{ chartTypeName(a.position.chartType) }}
                <span v-if="a.position.dataIndex !== undefined">#{{ a.position.dataIndex }}</span>
              </span>
            </div>
            <span class="text-xs text-slate-500">{{ formatTime(a.createdAt) }}</span>
          </div>
          <div v-if="editingId === a.id">
            <textarea v-model="editContent" rows="2"
              class="w-full bg-slate-800 border border-slate-600 rounded px-2 py-1 text-xs focus:outline-none focus:border-cyan-500 resize-none mb-2"></textarea>
            <div class="flex gap-1 justify-end">
              <button @click.stop="cancelEdit" class="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 rounded">取消</button>
              <button @click.stop="saveEdit(a)" :disabled="!editContent.trim()"
                class="text-xs px-2 py-1 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 rounded">保存</button>
            </div>
          </div>
          <div v-else class="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">{{ a.content }}</div>
          <div v-if="a.updatedAt !== a.createdAt" class="mt-1 text-xs text-slate-500 italic">(已编辑)</div>
          <div class="mt-2 pt-2 border-t border-slate-700/50 flex items-center justify-between opacity-0 group-hover:opacity-100 transition-opacity">
            <div class="flex gap-1">
              <button @click.stop="startEdit(a)" class="text-xs text-slate-400 hover:text-cyan-400 px-1.5 py-0.5">✏️ 编辑</button>
              <button @click.stop="toggleResolve(a, true)" class="text-xs text-slate-400 hover:text-green-400 px-1.5 py-0.5">✅ 解决</button>
            </div>
            <button @click.stop="confirmDelete(a)" class="text-xs text-slate-400 hover:text-red-400 px-1.5 py-0.5">🗑 删除</button>
          </div>
        </div>
      </template>

      <template v-if="showResolved && store.resolvedAnnotations.length > 0">
        <div class="text-xs text-slate-500 pt-3 mt-3 border-t border-slate-700">已解决 ({{ store.resolvedAnnotations.length }})</div>
        <template v-for="a in store.resolvedAnnotations" :key="a.id">
          <div class="rounded-lg border border-slate-700/50 bg-slate-900/30 p-3 opacity-70">
            <div class="flex items-start justify-between mb-2">
              <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded-full bg-slate-600 flex items-center justify-center text-xs font-bold text-slate-300">
                  {{ a.author.charAt(0).toUpperCase() }}
                </div>
                <span class="text-xs font-bold text-slate-400 line-through">{{ a.author }}</span>
                <span class="text-xs bg-green-500/20 text-green-400 px-1.5 py-0.5 rounded">✓ 已解决</span>
              </div>
              <span class="text-xs text-slate-600">{{ formatTime(a.createdAt) }}</span>
            </div>
            <div class="text-xs text-slate-500 line-through">{{ a.content }}</div>
            <div class="mt-2 flex gap-1">
              <button @click="toggleResolve(a, false)" class="text-xs text-slate-500 hover:text-amber-400 px-1.5 py-0.5">↩️ 重新打开</button>
              <button @click="confirmDelete(a)" class="text-xs text-slate-500 hover:text-red-400 px-1.5 py-0.5">🗑 删除</button>
            </div>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useMCStore, Annotation, ChartPosition } from '../store/mc'

const store = useMCStore()
const newAuthor = ref('研究员A')
const newContent = ref('')
const pickMode = ref(false)
const showResolved = ref(false)
const editingId = ref<string | null>(null)
const editContent = ref('')

const emit = defineEmits<{
  (e: 'selectAnnotation', ann: Annotation | null): void
  (e: 'pickModeChange', active: boolean): void
  (e: 'scrollToChart', chartType: string, position?: ChartPosition): void
}>()

const sortedActiveAnnotations = computed(() => {
  return [...store.activeAnnotations].sort((a, b) => {
    if (store.selectedAnnotationId === a.id) return -1
    if (store.selectedAnnotationId === b.id) return 1
    return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  })
})

watch(pickMode, (v) => emit('pickModeChange', v))

function chartTypeName(t: string) {
  const map: Record<string, string> = { convergence: '收敛曲线', histogram: '直方图' }
  return map[t] || t
}

function formatTime(iso: string) {
  try {
    const d = new Date(iso)
    const now = new Date()
    const diff = (now.getTime() - d.getTime()) / 1000
    if (diff < 60) return '刚刚'
    if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
    if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
    return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch { return iso }
}

async function submitAnnotation() {
  if (!newContent.value.trim() || !newAuthor.value.trim()) return
  await store.createAnnotation({
    content: newContent.value.trim(),
    author: newAuthor.value.trim(),
    scenarioId: store.currentScenario.id,
    position: store.pendingAnnotationPosition || undefined
  })
  newContent.value = ''
  store.setPendingPosition(null)
  pickMode.value = false
}

function selectAndScroll(a: Annotation) {
  store.selectAnnotation(a.id === store.selectedAnnotationId ? null : a.id)
  if (a.position && store.selectedAnnotationId === a.id) {
    emit('scrollToChart', a.position.chartType, a.position)
  }
}

function startEdit(a: Annotation) {
  editingId.value = a.id
  editContent.value = a.content
}

function cancelEdit() {
  editingId.value = null
  editContent.value = ''
}

async function saveEdit(a: Annotation) {
  if (!editContent.value.trim()) return
  await store.updateAnnotation(a.id, { content: editContent.value.trim() })
  editingId.value = null
  editContent.value = ''
}

async function toggleResolve(a: Annotation, resolved: boolean) {
  await store.updateAnnotation(a.id, { resolved })
}

function confirmDelete(a: Annotation) {
  if (confirm(`确定删除 ${a.author} 的批注吗？`)) {
    store.deleteAnnotation(a.id)
    if (store.selectedAnnotationId === a.id) store.selectAnnotation(null)
  }
}
</script>
