<template>
  <div class="min-h-screen bg-slate-900 text-slate-200 flex flex-col">
    <header class="border-b border-slate-700 px-6 py-4 flex items-center justify-between shrink-0">
      <div>
        <h1 class="text-2xl font-bold text-cyan-400">蒙特卡洛模拟与统计假设检验平台</h1>
        <p class="text-sm text-slate-500 mt-1">随机采样模拟 · 6种MC场景 · 假设检验 · 置信区间可视化 · <span class="text-amber-400">协作批注</span></p>
      </div>
      <div class="flex items-center gap-3">
        <span v-if="pickModeActive" class="text-xs bg-cyan-600 text-white px-3 py-1.5 rounded-full animate-pulse">
          📍 批注选点模式 - 点击图表任意位置关联批注
        </span>
        <button v-if="pickModeActive" @click="cancelPickMode" class="text-xs bg-slate-700 hover:bg-slate-600 text-white px-3 py-1.5 rounded-full">
          取消选点
        </button>
      </div>
    </header>
    <div class="flex flex-1 gap-4 p-4 overflow-hidden">
      <div class="w-72 shrink-0 space-y-4 overflow-y-auto pr-1">
        <div class="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <h3 class="text-sm font-bold text-slate-400 mb-3">模拟场景</h3>
          <div class="space-y-1">
            <div v-for="s in SCENARIOS" :key="s.id" @click="store.setScenario(s)"
              :class="['cursor-pointer p-2 rounded border text-sm transition-all', store.currentScenario.id === s.id ? 'border-cyan-500 bg-cyan-900/30 text-cyan-400' : 'border-slate-700 text-slate-300 hover:border-slate-500']">
              <div class="font-bold">{{ s.name }}</div>
              <div class="text-xs text-slate-500 mt-0.5">{{ s.description }}</div>
              <div v-if="getAnnCount(s.id) > 0" class="text-xs mt-1 text-amber-400">💬 {{ getAnnCount(s.id) }} 条批注</div>
            </div>
          </div>
        </div>
        <div class="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <h3 class="text-sm font-bold text-slate-400 mb-3">参数控制</h3>
          <label class="text-xs text-slate-500">迭代次数: {{ store.iterations }}</label>
          <input type="range" min="100" max="5000" step="100" v-model.number="store.iterations" class="w-full mt-1 mb-3 accent-cyan-500" />
          <button @click="store.runSimulation" :disabled="store.isRunning" class="w-full py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 rounded text-sm font-bold">
            {{ store.isRunning ? '运行中...' : '▶ 开始模拟' }}
          </button>
        </div>
        <div v-if="store.result" class="bg-slate-800 rounded-lg p-4 border border-slate-700 text-sm">
          <h3 class="text-sm font-bold text-slate-400 mb-3">模拟结果</h3>
          <div class="space-y-2">
            <div class="flex justify-between"><span class="text-slate-500">估算值</span><span class="text-cyan-400 font-bold font-mono">{{ store.result.estimate.toFixed(6) }}</span></div>
            <div v-if="store.result.trueValue !== undefined" class="flex justify-between"><span class="text-slate-500">真实值</span><span class="text-green-400 font-mono">{{ store.result.trueValue.toFixed(6) }}</span></div>
            <div v-if="store.result.error !== undefined" class="flex justify-between"><span class="text-slate-500">误差</span><span class="text-orange-400 font-mono">{{ store.result.error.toFixed(6) }}</span></div>
            <div class="flex justify-between"><span class="text-slate-500">样本数</span><span class="text-slate-300">{{ store.result.iterations }}</span></div>
          </div>
        </div>
      </div>
      <div class="flex-1 space-y-4 overflow-y-auto pr-1" ref="chartsContainer">
        <div ref="convergenceSection" class="bg-slate-800 rounded-lg p-4 border border-slate-700 transition-all"
          :class="highlightChart === 'convergence' ? 'ring-2 ring-amber-400 border-amber-400' : ''">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <h3 class="text-sm font-bold text-slate-400">收敛过程</h3>
              <span v-if="convAnnotations.length > 0" class="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full">
                📍 {{ convAnnotations.length }}
              </span>
            </div>
            <span class="text-xs text-slate-500">{{ pickModeActive ? '点击图表选择批注位置' : '提示: 先点击批注面板的"关联图表位置"再点击图表' }}</span>
          </div>
          <div ref="convergenceRef" class="w-full rounded chart-container"
            :class="pickModeActive ? 'cursor-crosshair' : ''" style="height:240px;background:#0f172a;"></div>
        </div>
        <div ref="histogramSection" class="bg-slate-800 rounded-lg p-4 border border-slate-700 transition-all"
          :class="highlightChart === 'histogram' ? 'ring-2 ring-amber-400 border-amber-400' : ''">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <h3 class="text-sm font-bold text-slate-400">样本分布直方图</h3>
              <span v-if="histAnnotations.length > 0" class="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full">
                📍 {{ histAnnotations.length }}
              </span>
            </div>
            <span class="text-xs text-slate-500">{{ pickModeActive ? '点击图表选择批注位置' : '' }}</span>
          </div>
          <div ref="histogramRef" class="w-full rounded chart-container"
            :class="pickModeActive ? 'cursor-crosshair' : ''" style="height:220px;background:#0f172a;"></div>
        </div>
        <div class="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <h3 class="text-sm font-bold text-slate-400 mb-3">假设检验 (独立样本 T 检验)</h3>
          <div class="grid grid-cols-2 gap-4 mb-3">
            <div>
              <label class="text-xs text-slate-500">样本组A (逗号分隔)</label>
              <textarea v-model="group1Input" rows="2" class="w-full mt-1 bg-slate-900 border border-slate-600 rounded px-2 py-1 text-xs font-mono focus:outline-none focus:border-cyan-500 resize-none"></textarea>
            </div>
            <div>
              <label class="text-xs text-slate-500">样本组B (逗号分隔)</label>
              <textarea v-model="group2Input" rows="2" class="w-full mt-1 bg-slate-900 border border-slate-600 rounded px-2 py-1 text-xs font-mono focus:outline-none focus:border-cyan-500 resize-none"></textarea>
            </div>
          </div>
          <button @click="runTest" class="px-4 py-1.5 bg-purple-600 hover:bg-purple-500 rounded text-sm">执行T检验</button>
          <div v-if="store.testResult" class="mt-3 grid grid-cols-4 gap-3 text-sm">
            <div class="bg-slate-900 rounded p-2 text-center"><div class="text-xs text-slate-500 mb-1">统计量 t</div><div class="text-cyan-400 font-bold font-mono">{{ store.testResult.statistic }}</div></div>
            <div class="bg-slate-900 rounded p-2 text-center"><div class="text-xs text-slate-500 mb-1">p 值</div><div class="font-bold font-mono" :class="store.testResult.significant ? 'text-red-400' : 'text-green-400'">{{ store.testResult.pValue }}</div></div>
            <div class="bg-slate-900 rounded p-2 text-center"><div class="text-xs text-slate-500 mb-1">自由度 df</div><div class="text-slate-300 font-mono">{{ store.testResult.df }}</div></div>
            <div class="bg-slate-900 rounded p-2 text-center"><div class="text-xs text-slate-500 mb-1">显著性</div><div class="text-xs font-bold" :class="store.testResult.significant ? 'text-red-400' : 'text-green-400'">{{ store.testResult.significant ? '显著(p<0.05)' : '不显著' }}</div></div>
          </div>
        </div>
      </div>
      <div class="w-80 shrink-0">
        <AnnotationPanel
          @pickModeChange="onPickModeChange"
          @scrollToChart="onScrollToChart"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import { useMCStore, SCENARIOS, Annotation, ChartPosition } from './store/mc'
import AnnotationPanel from './components/AnnotationPanel.vue'

const store = useMCStore()
const convergenceRef = ref<HTMLDivElement | null>(null)
const histogramRef = ref<HTMLDivElement | null>(null)
const chartsContainer = ref<HTMLDivElement | null>(null)
const convergenceSection = ref<HTMLDivElement | null>(null)
const histogramSection = ref<HTMLDivElement | null>(null)
const group1Input = ref('5.1,4.8,5.3,4.9,5.2,5.0,4.7,5.1,5.4,4.8')
const group2Input = ref('4.6,4.2,4.9,4.3,4.5,4.7,4.4,4.8,4.1,4.6')
let convChart: echarts.ECharts | null = null
let histChart: echarts.ECharts | null = null

const pickModeActive = ref(false)
const highlightChart = ref<string | null>(null)

const convAnnotations = computed(() => store.annotationsByChart.convergence)
const histAnnotations = computed(() => store.annotationsByChart.histogram)

function getAnnCount(scenarioId: string) {
  try {
    const raw = localStorage.getItem('mc_annotations_v1')
    if (raw) {
      const all = JSON.parse(raw)
      return all.filter((a: Annotation) => a.scenarioId === scenarioId && !a.resolved).length
    }
  } catch {}
  return 0
}

function buildConvOption() {
  const markPointData = convAnnotations.value.map((a, idx) => {
    const isSelected = store.selectedAnnotationId === a.id
    const dataIndex = a.position?.dataIndex ?? 0
    const data = store.convergenceData[dataIndex]
    return {
      name: a.content.slice(0, 15),
      coord: data ? [data[0], data[1]] : [dataIndex, 0],
      value: idx + 1,
      symbol: 'pin',
      symbolSize: isSelected ? 48 : 36,
      itemStyle: {
        color: isSelected ? '#f59e0b' : (a.resolved ? '#22c55e' : '#ef4444'),
        borderColor: isSelected ? '#fbbf24' : 'transparent',
        borderWidth: isSelected ? 3 : 0
      },
      label: {
        show: true,
        color: '#fff',
        fontSize: 11,
        fontWeight: 'bold',
        formatter: `${idx + 1}`
      },
      annotationId: a.id
    }
  })

  const baseOption: echarts.EChartsOption = {
    backgroundColor: '#0f172a',
    grid: { top: 30, bottom: 35, left: 65, right: 25 },
    xAxis: { type: 'value', axisLabel: { color: '#94a3b8', fontSize: 10 } },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8', fontSize: 10 } },
    series: [{
      type: 'line',
      data: store.convergenceData,
      smooth: true,
      lineStyle: { color: '#06b6d4', width: 2 },
      areaStyle: { color: 'rgba(6,182,212,0.1)' },
      symbol: 'none',
      markPoint: markPointData.length > 0 ? {
        symbol: 'pin',
        data: markPointData as any,
        silent: false
      } : undefined
    }],
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e293b',
      borderColor: '#475569',
      formatter: (params: any) => {
        const data = params[0]
        let html = `<div style="font-size:11px;"><div style="color:#94a3b8;">迭代 #${data.value[0]}</div><div style="color:#06b6d4;font-weight:bold;">值: ${data.value[1]}</div>`
        const nearAnns = convAnnotations.value.filter(a => Math.abs((a.position?.dataIndex ?? -1) - data.value[0]) <= 2)
        if (nearAnns.length > 0) {
          html += `<div style="margin-top:4px;padding-top:4px;border-top:1px solid #475569;color:#fbbf24;">相关批注:</div>`
          nearAnns.forEach(a => {
            html += `<div style="color:#fde68a;font-size:10px;">• ${a.author}: ${a.content.slice(0, 30)}${a.content.length > 30 ? '...' : ''}</div>`
          })
        }
        html += '</div>'
        return html
      }
    }
  }
  return baseOption
}

function buildHistOption() {
  const markPointData = histAnnotations.value.map((a, idx) => {
    const isSelected = store.selectedAnnotationId === a.id
    const dataIndex = Math.min(a.position?.dataIndex ?? 0, store.histogramData.data.length - 1)
    return {
      name: a.content.slice(0, 15),
      xAxis: store.histogramData.xAxis[dataIndex] ?? 0,
      y: store.histogramData.data[dataIndex] ?? 0,
      value: idx + 1,
      symbol: 'pin',
      symbolSize: isSelected ? 48 : 36,
      itemStyle: {
        color: isSelected ? '#f59e0b' : (a.resolved ? '#22c55e' : '#ef4444'),
        borderColor: isSelected ? '#fbbf24' : 'transparent',
        borderWidth: isSelected ? 3 : 0
      },
      label: {
        show: true,
        color: '#fff',
        fontSize: 11,
        fontWeight: 'bold',
        formatter: `${idx + 1}`
      },
      annotationId: a.id
    }
  })

  const baseOption: echarts.EChartsOption = {
    backgroundColor: '#0f172a',
    grid: { top: 30, bottom: 40, left: 55, right: 15 },
    xAxis: { type: 'category', data: store.histogramData.xAxis as any, axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 30 } },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8', fontSize: 10 } },
    series: [{
      type: 'bar',
      data: store.histogramData.data,
      itemStyle: {
        color: (params: any) => {
          const relatedAnn = histAnnotations.value.find(a => a.position?.dataIndex === params.dataIndex)
          if (relatedAnn) {
            if (store.selectedAnnotationId === relatedAnn.id) return '#f59e0b'
            return relatedAnn.resolved ? '#16a34a' : '#dc2626'
          }
          return '#8b5cf6'
        }
      },
      markPoint: markPointData.length > 0 ? {
        symbol: 'pin',
        data: markPointData as any,
        silent: false
      } : undefined
    }],
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e293b',
      borderColor: '#475569',
      formatter: (params: any) => {
        const data = params[0]
        let html = `<div style="font-size:11px;"><div style="color:#94a3b8;">区间中心: ${data.name}</div><div style="color:#8b5cf6;font-weight:bold;">频数: ${data.value}</div>`
        const relatedAnn = histAnnotations.value.find(a => a.position?.dataIndex === data.dataIndex)
        if (relatedAnn) {
          html += `<div style="margin-top:4px;padding-top:4px;border-top:1px solid #475569;color:#fbbf24;">批注 ${relatedAnn.author}:</div>`
          html += `<div style="color:#fde68a;font-size:10px;">${relatedAnn.content}</div>`
        }
        html += '</div>'
        return html
      }
    }
  }
  return baseOption
}

function initCharts() {
  if (convergenceRef.value) {
    convChart = echarts.init(convergenceRef.value, 'dark')
    convChart.on('click', (params: any) => onChartClick('convergence', params))
  }
  if (histogramRef.value) {
    histChart = echarts.init(histogramRef.value, 'dark')
    histChart.on('click', (params: any) => onChartClick('histogram', params))
  }
  window.addEventListener('resize', handleResize)
}

function handleResize() {
  convChart?.resize()
  histChart?.resize()
}

function onChartClick(chartType: string, params: any) {
  if (!pickModeActive.value) {
    if (params.componentType === 'markPoint' && params.data?.annotationId) {
      store.selectAnnotation(params.data.annotationId === store.selectedAnnotationId ? null : params.data.annotationId)
      nextTick(() => updateCharts())
    }
    return
  }

  const pos: ChartPosition = { chartType }
  if (chartType === 'convergence') {
    if (params.componentType === 'series') {
      pos.dataIndex = params.dataIndex
      if (params.value && Array.isArray(params.value)) {
        pos.xValue = params.value[0]
        pos.yValue = params.value[1]
      }
    } else if (params.componentType === 'xAxis' || params.componentType === 'grid') {
      const dataLen = store.convergenceData.length
      if (dataLen > 0) {
        const approx = Math.round((params.offsetX ?? 0) / (convergenceRef.value?.clientWidth ?? 1) * dataLen)
        pos.dataIndex = Math.max(0, Math.min(dataLen - 1, approx))
      }
    }
    if (pos.dataIndex === undefined) pos.dataIndex = 0
    const d = store.convergenceData[pos.dataIndex]
    if (d) { pos.xValue = d[0]; pos.yValue = d[1] }
  } else {
    if (params.componentType === 'series') {
      pos.dataIndex = params.dataIndex
      const xv = store.histogramData.xAxis[params.dataIndex]
      const yv = store.histogramData.data[params.dataIndex]
      if (xv !== undefined) pos.xValue = xv
      if (yv !== undefined) pos.yValue = yv
    } else {
      const dataLen = store.histogramData.xAxis.length
      if (dataLen > 0) {
        const approx = Math.round((params.offsetX ?? 0) / (histogramRef.value?.clientWidth ?? 1) * dataLen)
        pos.dataIndex = Math.max(0, Math.min(dataLen - 1, approx))
        const xv = store.histogramData.xAxis[pos.dataIndex]
        if (xv !== undefined) pos.xValue = xv
      }
    }
    if (pos.dataIndex === undefined) pos.dataIndex = 0
  }

  store.setPendingPosition(pos)
  pickModeActive.value = false
  showPickFlash(chartType)
}

function showPickFlash(chartType: string) {
  highlightChart.value = chartType
  setTimeout(() => { highlightChart.value = null }, 1500)
}

function updateCharts() {
  if (convChart && store.convergenceData.length > 0) {
    convChart.setOption(buildConvOption(), true)
  }
  if (histChart && store.histogramData.xAxis.length > 0) {
    histChart.setOption(buildHistOption(), true)
  }
}

function onPickModeChange(active: boolean) {
  pickModeActive.value = active
}

function cancelPickMode() {
  pickModeActive.value = false
  store.setPendingPosition(null)
}

function onScrollToChart(chartType: string, position?: ChartPosition) {
  highlightChart.value = chartType
  nextTick(() => {
    const el = chartType === 'convergence' ? convergenceSection.value : histogramSection.value
    el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    updateCharts()
  })
  setTimeout(() => { highlightChart.value = null }, 2500)
}

function runTest() {
  const g1 = group1Input.value.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n))
  const g2 = group2Input.value.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n))
  if (g1.length > 1 && g2.length > 1) store.runTest(g1, g2)
}

watch(() => store.result, () => nextTick(() => updateCharts()), { deep: true })
watch(() => store.annotations, () => nextTick(() => updateCharts()), { deep: true })
watch(() => store.selectedAnnotationId, () => nextTick(() => updateCharts()), { deep: true })

onMounted(() => {
  initCharts()
  store.runSimulation()
  store.loadAnnotations()
})
</script>

<style>
.chart-container {
  position: relative;
}
</style>
