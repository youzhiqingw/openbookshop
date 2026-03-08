<template>
  <div class="dashboard-view">
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="5" v-for="item in overviewCards" :key="item.title">
        <el-card shadow="hover" class="stat-card" :style="{ borderTop: `4px solid ${item.color}` }">
          <div class="stat-content">
            <div class="stat-icon" :style="{ color: item.color, background: `${item.color}18` }">
              <el-icon :size="28"><component :is="item.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-label">{{ item.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <span>近30天订单与收入趋势</span>
          </template>
          <div ref="lineChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <span>订单状态分布</span>
          </template>
          <div ref="pieChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <span>销量 TOP 10 图书</span>
          </template>
          <div ref="barChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { adminApi } from '@/api'
import { ElMessage } from 'element-plus'
import { User, Shop, Reading, Warning, Wallet } from '@element-plus/icons-vue'
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
    { title: '注册用户', value: ov.total_users, icon: 'User', color: '#1890FF' },
    { title: '在营商家', value: ov.total_merchants, icon: 'Shop', color: '#2C5F2D' },
    { title: '在售图书', value: ov.total_books, icon: 'Reading', color: '#4A7C4B' },
    { title: '库存预警', value: ov.low_stock_count, icon: 'Warning', color: '#FAAD14' },
    { title: '平台总收入', value: `¥${Number(ov.total_revenue).toFixed(2)}`, icon: 'Wallet', color: '#C75B39' },
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
  const { daily_data, status_distribution, top_books } = stats.value

  // 折线图：订单量 & 收入趋势
  const lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['订单数', '收入(元)'] },
    xAxis: { type: 'category', data: daily_data.map(d => d.date.slice(5)) },
    yAxis: [
      { type: 'value', name: '订单数' },
      { type: 'value', name: '收入(元)' },
    ],
    series: [
      {
        name: '订单数', type: 'line', smooth: true,
        data: daily_data.map(d => d.orders),
        itemStyle: { color: '#1890FF' },
        areaStyle: { color: 'rgba(24,144,255,0.08)' },
      },
      {
        name: '收入(元)', type: 'line', smooth: true, yAxisIndex: 1,
        data: daily_data.map(d => Number(d.revenue).toFixed(2)),
        itemStyle: { color: '#2C5F2D' },
        areaStyle: { color: 'rgba(44,95,45,0.08)' },
      },
    ],
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

  // 条形图：TOP10图书销量
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
      itemStyle: { color: '#2C5F2D', borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top' },
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
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 4px 0;
  }
  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    opacity: 0.85;
  }
  .stat-value {
    font-size: 24px;
    font-weight: 700;
    color: #1A1A1A;
    line-height: 1;
  }
  .stat-label {
    font-size: 13px;
    color: #666;
    margin-top: 6px;
  }
}
.chart-row {
  margin-bottom: 20px;
}
</style>
