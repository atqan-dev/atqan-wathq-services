<template>
  <Doughnut :data="chartData" :options="chartOptions" />
</template>

<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend
)

interface Props {
  labels: string[]
  datasets: Array<{
    data: number[]
    backgroundColor?: string[]
    borderWidth?: number
  }>
  title?: string
  height?: number
}

const props = withDefaults(defineProps<Props>(), {
  height: 300
})

const chartData = computed<ChartData<'doughnut'>>(() => ({
  labels: props.labels,
  datasets: props.datasets.map((dataset) => ({
    ...dataset,
    borderWidth: dataset.borderWidth ?? 0
  }))
}))

const chartOptions = computed<ChartOptions<'doughnut'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 15
      }
    },
    title: {
      display: !!props.title,
      text: props.title,
      padding: {
        top: 10,
        bottom: 20
      },
      font: {
        size: 16,
        weight: 'bold'
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 12,
      cornerRadius: 8,
      displayColors: true
    }
  }
}))
</script>
