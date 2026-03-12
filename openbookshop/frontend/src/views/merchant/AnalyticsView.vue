<template>
  <div class="analytics-view">
    <!-- Overview Cards -->
    <el-row :gutter="16" class="overview-cards">
      <el-col :xs="12" :sm="8" :md="4" v-for="item in overviewCards" :key="item.title">
        <div class="stat-card" :style="{ '--card-color': item.color, '--card-bg': item.bg }">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.title }}</div>
          <div class="stat-bar" :style="{ background: item.color }"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :span="16">
        <el-card shadow="never" class="chart-card">
          <template #header><span class="chart-title">近30天收入趋势</span></template>
          <div ref="lineChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="chart-card">
          <template #header><span class="chart-title">订单状态分布</span></template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :span="24">
        <el-card shadow="never" class="chart-card">
          <template #header><span class="chart-title">热销图书排行 TOP 10</span></template>
          <div ref="barChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { merchantApi } from '@/api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const analytics = ref(null)
const lineChartRef = ref(null)
const pieChartRef = ref(null)
const barChartRef = ref(null)

const STATUS_LABEL = {
  pending_payment: '待支付',
  paid: '已支付',
  processing: '备货中',
  shipped: '已发货',
  delivered: '已送达',
  completed: '已完成',
  cancelled: '已取消',
  refunding: '退款中',
  refunded: '已退款',
}

const overviewCards = computed(() => {
  if (!analytics.value) return []
  const ov = analytics.value.overview
  return [
    { title: '在售图书', value: `${ov.on_sale_books}/${ov.total_books}`, color: '#1890ff', bg: '#e6f4ff' },
    { title: '累计订单', value: ov.total_orders, color: '#52c41a', bg: '#f6ffed' },
    { title: '已完成订单', value: ov.completed_orders, color: '#13c2c2', bg: '#e6fffb' },
    { title: '累计收入', value: `¥${Number(ov.total_revenue).toFixed(0)}`, color: '#722ed1', bg: '#f9f0ff' },
    { title: '库存预警', value: ov.low_stock_count, color: '#ff4d4f', bg: '#fff2f0' },
    { title: '完成率', value: ov.total_orders ? `${((ov.completed_orders / ov.total_orders) * 100).toFixed(1)}%` : '0%', color: '#fa8c16', bg: '#fff7e6' },
  ]
})

async function fetchAnalytics() {
  try {
    const res = await merchantApi.getAnalytics()
    analytics.value = res.data
    initCharts()
  } catch {
    ElMessage.error('获取统计数据失败')
  }
}

function initCharts() {
  if (!analytics.value) return
  const { daily_data, top_books, status_distribution } = analytics.value

  // 折线图
  const lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: daily_data.map(d => d.date.slice(5)) },
    yAxis: { type: 'value', name: '收入(元)' },
    series: [{
      name: '收入', type: 'line', smooth: true,
      data: daily_data.map(d => Number(d.revenue).toFixed(2)),
      itemStyle: { color: '#67c23a' },
      areaStyle: { color: 'rgba(103, 194, 58, 0.1)' },
    }],
  })

  // 饼图：订单状态
  const pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: status_distribution.map(s => ({
        name: STATUS_LABEL[s.status] || s.status,
        value: s.count,
      })),
      label: { formatter: '{b}: {c}' },
    }],
  })

  // 条形图：TOP10图书
  const barChart = echarts.init(barChartRef.value)
  barChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: top_books.map(b => b.title.length > 8 ? b.title.slice(0, 8) + '…' : b.title),
      axisLabel: { rotate: 30 },
    },
    yAxis: { type: 'value', name: '销量' },
    series: [{
      type: 'bar', data: top_books.map(b => b.sales),
      itemStyle: { color: '#409eff' },
      label: { show: true, position: 'top' },
    }],
  })
}

onMounted(fetchAnalytics)
</script>

<style lang="scss" scoped>
.analytics-view {}

// ── Overview Cards ────────────────────────────────────
.overview-cards {
  margin-bottom: 16px;
}

.stat-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 18px 16px 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: default;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  }

  .stat-value {
    font-size: 20px;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1.2;
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 12px;
    color: #888;
  }

  .stat-bar {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
  }
}

// ── Charts ────────────────────────────────────────────
.chart-row {
  margin-bottom: 16px;
}

.chart-card {
  border-radius: 12px !important;

  :deep(.el-card__header) {
    padding: 14px 20px;
    border-bottom: 1px solid #f5f5f5;
  }

  :deep(.el-card__body) {
    padding: 16px 20px;
  }
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.chart-container {
  height: 260px;
}
</style>
