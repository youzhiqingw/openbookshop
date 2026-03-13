<template>
  <div class="dashboard-view">
    <!-- Overview Cards -->
    <el-row :gutter="16" class="overview-cards">
      <el-col :xs="12" :sm="12" :md="8" :lg="5" v-for="item in overviewCards" :key="item.title">
        <div class="stat-card" :style="{ '--card-color': item.color, '--card-bg': item.bg }">
          <div class="stat-icon-wrap">
            <el-icon :size="28"><component :is="item.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ item.value }}</div>
            <div class="stat-label">{{ item.title }}</div>
          </div>
          <div class="stat-decoration"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts Row 1 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="16">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">近30天订单与收入趋势</span>
              <el-tag size="small" type="info">实时数据</el-tag>
            </div>
          </template>
          <div ref="lineChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">订单状态分布</span>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row 2 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="24">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">销量 TOP 10 图书</span>
            </div>
          </template>
          <div ref="barChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { adminApi } from '@/api'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const stats = ref(null)
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
  if (!stats.value) return []
  const ov = stats.value.overview
  return [
    { title: '注册用户', value: ov.total_users, icon: 'User', color: '#1890ff', bg: '#e6f4ff' },
    { title: '在营商家', value: ov.total_merchants, icon: 'Shop', color: '#52c41a', bg: '#f6ffed' },
    { title: '在售图书', value: ov.total_books, icon: 'Reading', color: '#fa8c16', bg: '#fff7e6' },
    { title: '库存预警', value: ov.low_stock_count, icon: 'Warning', color: '#ff4d4f', bg: '#fff2f0' },
    { title: '平台总收入', value: `¥${Number(ov.total_revenue).toFixed(0)}`, icon: 'Wallet', color: '#722ed1', bg: '#f9f0ff' },
  ]
})

async function fetchStatistics() {
  try {
    const res = await adminApi.getStatistics()
    stats.value = res.data
    initCharts()
  } catch {
    ElMessage.error('获取统计数据失败')
  }
}

function initCharts() {
  if (!stats.value) return
  const daily_data = stats.value.daily_data || []
  const status_distribution = stats.value.status_distribution || []
  const top_books = stats.value.top_books || []

  // 折线图
  const lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.9)', borderColor: '#eee', textStyle: { color: '#333' } },
    legend: { data: ['订单数', '收入(元)'], bottom: 0 },
    grid: { top: 10, right: 20, bottom: 40, left: 50 },
    xAxis: { type: 'category', data: daily_data.map(d => d.date.slice(5)), axisLine: { lineStyle: { color: '#ddd' } } },
    yAxis: [
      { type: 'value', name: '订单数', splitLine: { lineStyle: { color: '#f0f0f0' } } },
      { type: 'value', name: '收入(元)', splitLine: { show: false } },
    ],
    series: [
      {
        name: '订单数', type: 'line', smooth: true,
        data: daily_data.map(d => d.orders),
        itemStyle: { color: '#1890ff' },
        areaStyle: { color: 'rgba(24,144,255,0.08)' },
      },
      {
        name: '收入(元)', type: 'line', smooth: true, yAxisIndex: 1,
        data: daily_data.map(d => Number(d.revenue).toFixed(2)),
        itemStyle: { color: '#52c41a' },
        areaStyle: { color: 'rgba(82,196,26,0.08)' },
      },
    ],
  })

  // 饼图
  const pieChart = echarts.init(pieChartRef.value)
  const pieColors = ['#1890ff', '#52c41a', '#fa8c16', '#722ed1', '#ff4d4f', '#13c2c2', '#eb2f96', '#faad14']
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['50%', '48%'],
      data: status_distribution.map((s, i) => ({
        name: STATUS_LABEL[s.status] || s.status,
        value: s.count,
        itemStyle: { color: pieColors[i % pieColors.length] },
      })),
      label: { formatter: '{b}\n{c}', fontSize: 11 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.3)' } },
    }],
  })

  // 条形图
  const barChart = echarts.init(barChartRef.value)
  barChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 10, right: 20, bottom: 60, left: 50 },
    xAxis: {
      type: 'category',
      data: top_books.map(b => b.title.length > 8 ? b.title.slice(0, 8) + '…' : b.title),
      axisLabel: { rotate: 30, fontSize: 12 },
      axisLine: { lineStyle: { color: '#ddd' } },
    },
    yAxis: { type: 'value', name: '销量', splitLine: { lineStyle: { color: '#f0f0f0' } } },
    series: [{
      type: 'bar',
      data: top_books.map((b, i) => ({
        value: b.sales,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: i === 0 ? '#fa8c16' : '#1890ff' },
            { offset: 1, color: i === 0 ? '#faad14' : '#69c0ff' },
          ]),
        },
      })),
      barMaxWidth: 48,
      label: { show: true, position: 'top', fontSize: 11 },
    }],
  })
}

onMounted(() => {
  fetchStatistics()
})
</script>

<style lang="scss" scoped>
.dashboard-view {
  padding: 0;
}

// ── Overview Cards ────────────────────────────────────
.overview-cards {
  margin-bottom: 16px;
}

.stat-card {
  position: relative;
  background: #ffffff;
  border-radius: 12px;
  padding: 20px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: default;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  }

  .stat-icon-wrap {
    width: 52px;
    height: 52px;
    border-radius: 12px;
    background: var(--card-bg);
    color: var(--card-color);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .stat-info {
    flex: 1;
    min-width: 0;
  }

  .stat-value {
    font-size: 22px;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .stat-label {
    font-size: 12px;
    color: #888;
    margin-top: 4px;
  }

  .stat-decoration {
    position: absolute;
    right: -10px;
    bottom: -10px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: var(--card-bg);
    opacity: 0.6;
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

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;

  .chart-title {
    font-size: 14px;
    font-weight: 600;
    color: #1a1a1a;
  }
}

.chart-container {
  height: 280px;
}
</style>
