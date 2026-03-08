<template>
  <div class="analytics-view">
    <el-row :gutter="16" class="overview-cards">
      <el-col :span="4" v-for="item in overviewCards" :key="item.title">
        <el-card shadow="hover" class="stat-card" :style="{ borderTop: `4px solid ${item.color}` }">
          <div class="stat-content">
            <div class="stat-value">{{ item.value }}</div>
            <div class="stat-label">{{ item.title }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header><span>近30天收入趋势</span></template>
          <div ref="lineChartRef" style="height: 280px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span>订单状态分布</span></template>
          <div ref="pieChartRef" style="height: 280px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header><span>热销图书排行 TOP 10</span></template>
          <div ref="barChartRef" style="height: 280px;"></div>
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
    { title: '在售图书', value: `${ov.on_sale_books} / ${ov.total_books}`, color: '#1890FF' },
    { title: '累计订单', value: ov.total_orders, color: '#2C5F2D' },
    { title: '已完成订单', value: ov.completed_orders, color: '#4A7C4B' },
    { title: '累计收入', value: `¥${Number(ov.total_revenue).toFixed(2)}`, color: '#C75B39' },
    { title: '库存预警', value: ov.low_stock_count, color: '#FAAD14' },
    { title: '完成率', value: ov.total_orders ? `${((ov.completed_orders / ov.total_orders) * 100).toFixed(1)}%` : '0%', color: '#52C41A' },
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
      itemStyle: { color: '#2C5F2D' },
      areaStyle: { color: 'rgba(44,95,45,0.1)' },
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
      itemStyle: { color: '#4A7C4B', borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top' },
    }],
  })
}

onMounted(fetchAnalytics)
</script>

<style lang="scss" scoped>
.analytics-view {}
.overview-cards {
  margin-bottom: 24px;
}
.stat-card {
  border-radius: 8px;
  transition: box-shadow 0.3s, transform 0.3s;

  &:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    transform: translateY(-2px);
  }

  .stat-content {
    text-align: center;
    padding: 8px 0;
  }
  .stat-value {
    font-size: 22px;
    font-weight: 700;
    color: #1A1A1A;
    line-height: 1;
  }
  .stat-label {
    font-size: 13px;
    color: #666;
    margin-top: 8px;
  }
}
.chart-row {
  margin-bottom: 20px;
}
</style>
