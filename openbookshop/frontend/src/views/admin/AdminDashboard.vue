<template>
  <div class="admin-dashboard">
    <!-- Welcome Section -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">欢迎回来，{{ currentUser?.username }}</h1>
        <p class="welcome-subtitle">{{ greeting }}</p>
      </div>
      <div class="welcome-stats">
        <div class="stat-bubble">
          <span class="stat-number">{{ todayNewUsers }}</span>
          <span class="stat-label">今日新用户</span>
        </div>
        <div class="stat-bubble">
          <span class="stat-number">{{ todayOrders }}</span>
          <span class="stat-label">今日订单</span>
        </div>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-section">
      <div class="kpi-card" v-for="card in kpiCards" :key="card.id" :style="{ '--card-color': card.color }">
        <div class="kpi-header">
          <h3 class="kpi-title">{{ card.title }}</h3>
          <el-tag :type="card.trend > 0 ? 'success' : 'danger'" effect="dark" size="small">
            {{ card.trend > 0 ? '📈' : '📉' }} {{ Math.abs(card.trend) }}%
          </el-tag>
        </div>
        <div class="kpi-value">{{ formatNumber(card.value) }}</div>
        <div class="kpi-unit">{{ card.unit }}</div>
        <div class="kpi-footer">
          <span class="kpi-compare">较上周 {{ card.compare > 0 ? '+' : '' }}{{ card.compare }}%</span>
        </div>
        <div class="kpi-decoration"></div>
      </div>
    </div>

    <!-- Charts Section -->
    <el-row :gutter="24" class="charts-section">
      <!-- Revenue Chart -->
      <el-col :xs="24" :sm="24" :md="14" :lg="14">
        <div class="chart-card premium">
          <div class="chart-header">
            <h3 class="chart-title">收入趋势</h3>
            <div class="chart-controls">
              <el-radio-group v-model="revenueChartType" size="small" @change="updateRevenueChart">
                <el-radio-button label="week">周</el-radio-button>
                <el-radio-button label="month">月</el-radio-button>
                <el-radio-button label="year">年</el-radio-button>
              </el-radio-group>
            </div>
          </div>
          <div ref="revenueChartRef" class="chart-container" style="height: 300px;"></div>
        </div>
      </el-col>

      <!-- Order Distribution -->
      <el-col :xs="24" :sm="24" :md="10" :lg="10">
        <div class="chart-card premium">
          <div class="chart-header">
            <h3 class="chart-title">订单状态分布</h3>
          </div>
          <div ref="orderChartRef" class="chart-container" style="height: 300px;"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Tables Section -->
    <el-row :gutter="24" class="tables-section">
      <!-- Recent Orders -->
      <el-col :xs="24" :sm="24" :md="14" :lg="14">
        <div class="table-card">
          <div class="table-header">
            <h3 class="table-title">最近订单</h3>
            <RouterLink to="/admin/orders" class="link-more">查看全部 →</RouterLink>
          </div>
          <el-table :data="recentOrders" stripe style="width: 100%;" :default-sort="{ prop: 'date', order: 'descending' }">
            <el-table-column prop="id" label="订单号" width="120" />
            <el-table-column prop="customer" label="客户" />
            <el-table-column prop="amount" label="金额" width="80">
              <template #default="{ row }">
                ¥{{ row.amount.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="date" label="时间" width="150" />
          </el-table>
        </div>
      </el-col>

      <!-- Top Products -->
      <el-col :xs="24" :sm="24" :md="10" :lg="10">
        <div class="table-card">
          <div class="table-header">
            <h3 class="table-title">热销商品 TOP 5</h3>
            <RouterLink to="/admin/books" class="link-more">管理 →</RouterLink>
          </div>
          <div class="product-list">
            <div class="product-item" v-for="(product, index) in topProducts" :key="index">
              <div class="product-rank">{{ index + 1 }}</div>
              <div class="product-info">
                <p class="product-name">{{ product.name }}</p>
                <p class="product-sales">销量 {{ product.sales }}</p>
              </div>
              <div class="product-revenue">¥{{ product.revenue.toFixed(2) }}</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Activity Timeline -->
    <div class="activity-section">
      <h3 class="section-title">最近活动</h3>
      <div class="timeline">
        <div class="timeline-item" v-for="(activity, index) in recentActivities" :key="index">
          <div class="timeline-dot" :class="`type-${activity.type}`"></div>
          <div class="timeline-content">
            <p class="timeline-title">{{ activity.title }}</p>
            <p class="timeline-time">{{ activity.time }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Management } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好！'
  if (hour < 18) return '下午好！'
  return '晚上好！'
})

const todayNewUsers = ref(24)
const todayOrders = ref(156)
const revenueChartType = ref('week')

const kpiCards = ref([
  { id: 1, title: '总用户数', value: 12450, unit: '人', trend: 12.5, compare: 8, color: '#3b82f6' },
  { id: 2, title: '总商品数', value: 850, unit: '件', trend: 5.2, compare: 3, color: '#06b6d4' },
  { id: 3, title: '今日收入', value: 45320, unit: '元', trend: 18.7, compare: 15, color: '#10b981' },
  { id: 4, title: '活跃商家', value: 342, unit: '家', trend: 3.1, compare: 2, color: '#f59e0b' },
])

const recentOrders = ref([
  { id: 'ORD001', customer: ' 张三', amount: 199.99, status: '已完成', date: '2026-03-13 10:30' },
  { id: 'ORD002', customer: '李四', amount: 299.50, status: '待发货', date: '2026-03-13 09:15' },
  { id: 'ORD003', customer: '王五', amount: 89.99, status: '已取消', date: '2026-03-13 08:45' },
  { id: 'ORD004', customer: '赵六', amount: 150.00, status: '待支付', date: '2026-03-13 07:20' },
  { id: 'ORD005', customer: '孙七', amount: 450.75, status: '已完成', date: '2026-03-12 20:10' },
])

const topProducts = ref([
  { name: 'Python 深度学习', sales: 324, revenue: 2592 },
  { name: 'JavaScript 高级程序设计', sales: 287, revenue: 3440 },
  { name: 'Vue3 实战指南', sales: 256, revenue: 1792 },
  { name: '数据科学基础', sales: 198, revenue: 1782 },
  { name: '云计算架构设计', sales: 156, revenue: 1560 },
])

const recentActivities = ref([
  { type: 'user', title: '新用户注册：李明', time: '5分钟前' },
  { type: 'order', title: '订单完成：ORD001', time: '12分钟前' },
  { type: 'merchant', title: '商家申请审核通过', time: '25分钟前' },
  { type: 'warning', title: '库存预警：《数据库入门》', time: '1小时前' },
  { type: 'system', title: '系统备份完成', time: '2小时前' },
])

const revenueChartRef = ref()
const orderChartRef = ref()

const formatNumber = (num) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toLocaleString()
}

const getStatusType = (status) => {
  const statusMap = {
    '已完成': 'success',
    '待发货': 'warning',
    '待支付': 'info',
    '已取消': 'danger',
  }
  return statusMap[status] || 'info'
}

const updateRevenueChart = () => {
  // 更新图表的逻辑
  console.log('Chart updated for:', revenueChartType.value)
}

onMounted(() => {
  // 初始化图表的逻辑
})
</script>

<style lang="scss" scoped>
// ============================================
// Admin Dashboard - Premium Design
// ============================================

.admin-dashboard {
  width: 100%;
  animation: fadeIn 0.4s ease-out;

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
}

// ============================================
// Welcome Section
// ============================================

.welcome-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%);
  border-radius: 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  margin-bottom: 32px;
  backdrop-filter: blur(10px);

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }

  .welcome-content {
    .welcome-title {
      font-size: 28px;
      font-weight: 700;
      color: #ffffff;
      margin: 0 0 8px 0;
      letter-spacing: -0.5px;
    }

    .welcome-subtitle {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.8);
      margin: 0;
    }
  }

  .welcome-stats {
    display: flex;
    gap: 20px;

    @media (max-width: 768px) {
      width: 100%;
      justify-content: center;
    }

    .stat-bubble {
      background: rgba(255, 255, 255, 0.12);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 12px;
      padding: 16px 24px;
      text-align: center;
      backdrop-filter: blur(10px);

      .stat-number {
        display: block;
        font-size: 24px;
        font-weight: 700;
        color: #60a5fa;
        margin-bottom: 6px;
      }

      .stat-label {
        display: block;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.7);
      }
    }
  }
}

// ============================================
// KPI Cards
// ============================================

.kpi-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;

  .kpi-card {
    position: relative;
    padding: 24px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    backdrop-filter: blur(10px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;

    &:hover {
      transform: translateY(-4px);
      border-color: rgba(255, 255, 255, 0.2);
      box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
    }

    .kpi-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      .kpi-title {
        font-size: 14px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.8);
        margin: 0;
      }
    }

    .kpi-value {
      font-size: 32px;
      font-weight: 700;
      color: var(--card-color);
      margin-bottom: 4px;
      line-height: 1;
    }

    .kpi-unit {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.6);
      margin-bottom: 12px;
    }

    .kpi-footer {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.7);

      .kpi-compare {
        display: inline-block;
      }
    }

    .kpi-decoration {
      position: absolute;
      width: 120px;
      height: 120px;
      background: radial-gradient(circle, var(--card-color, #3b82f6), transparent);
      opacity: 0.1;
      border-radius: 50%;
      top: -40px;
      right: -40px;
      pointer-events: none;
    }
  }
}

// ============================================
// Charts Section
// ============================================

.charts-section {
  margin-bottom: 32px;

  .chart-card {
    padding: 24px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    backdrop-filter: blur(10px);

    &.premium {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.04) 100%);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      .chart-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
      }

      .chart-controls {
        :deep(.el-radio-group) {
          .el-radio-button__inner {
            background: rgba(255, 255, 255, 0.08);
            color: rgba(255, 255, 255, 0.7);
            border-color: rgba(255, 255, 255, 0.12);

            &:hover {
              color: white;
            }
          }

          .el-radio-button__original-radio:checked + .el-radio-button__inner {
            background: #3b82f6;
            border-color: #3b82f6;
            color: white;
          }
        }
      }
    }

    .chart-container {
      width: 100%;
    }
  }
}

// ============================================
// Tables Section
// ============================================

.tables-section {
  margin-bottom: 32px;

  .table-card {
    padding: 24px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    backdrop-filter: blur(10px);

    .table-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      .table-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
      }

      .link-more {
        color: #3b82f6;
        text-decoration: none;
        font-size: 13px;
        font-weight: 600;
        transition: color 0.3s;

        &:hover {
          color: #60a5fa;
        }
      }
    }

    :deep(.el-table) {
      --el-table-bg-color: transparent;
      --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.08);
      --el-border-color: rgba(255, 255, 255, 0.12);

      th {
        background: transparent !important;
        color: rgba(255, 255, 255, 0.9) !important;
        border-bottom-color: rgba(255, 255, 255, 0.12) !important;
        font-weight: 600;
      }

      td {
        color: rgba(255, 255, 255, 0.8) !important;
        border-bottom-color: rgba(255, 255, 255, 0.08) !important;
      }

      tr {
        background: transparent !important;

        &:hover > td {
          background: rgba(255, 255, 255, 0.08) !important;
        }
      }
    }

    .product-list {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .product-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 8px;
        transition: all 0.3s;

        &:hover {
          background: rgba(255, 255, 255, 0.08);
        }

        .product-rank {
          width: 32px;
          height: 32px;
          background: linear-gradient(135deg, #3b82f6, #06b6d4);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: 700;
          font-size: 14px;
          flex-shrink: 0;
        }

        .product-info {
          flex: 1;

          .product-name {
            margin: 0 0 4px 0;
            color: #ffffff;
            font-size: 14px;
            font-weight: 500;
          }

          .product-sales {
            margin: 0;
            color: rgba(255, 255, 255, 0.6);
            font-size: 12px;
          }
        }

        .product-revenue {
          color: #10b981;
          font-weight: 600;
          font-size: 14px;
          flex-shrink: 0;
        }
      }
    }
  }
}

// ============================================
// Activity Timeline
// ============================================

.activity-section {
  padding: 24px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  backdrop-filter: blur(10px);

  .section-title {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 20px 0;
  }

  .timeline {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .timeline-item {
      display: flex;
      gap: 16px;
      padding: 12px 0;

      .timeline-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        flex-shrink: 0;
        margin-top: 4px;

        &.type-user { background: #3b82f6; }
        &.type-order { background: #10b981; }
        &.type-merchant { background: #f59e0b; }
        &.type-warning { background: #ef4444; }
        &.type-system { background: #06b6d4; }
      }

      .timeline-content {
        flex: 1;

        .timeline-title {
          margin: 0 0 4px 0;
          color: #ffffff;
          font-size: 14px;
          font-weight: 500;
        }

        .timeline-time {
          margin: 0;
          color: rgba(255, 255, 255, 0.6);
          font-size: 12px;
        }
      }
    }
  }
}

// ============================================
// Responsive
// ============================================

@media (max-width: 1024px) {
  .kpi-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .kpi-section {
    grid-template-columns: 1fr;
  }

  .welcome-section {
    padding: 16px;
  }
}
</style>
