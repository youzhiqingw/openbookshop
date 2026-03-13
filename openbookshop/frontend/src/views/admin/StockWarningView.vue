<template>
  <div class="stock-warning-view">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <span>全平台库存预警</span>
          <el-button type="primary" :icon="Refresh" @click="fetchData">刷新</el-button>
        </div>
      </template>

      <el-alert
        v-if="list.length > 0"
        :title="`当前共有 ${total} 件商品库存不足，需及时补货！`"
        type="warning"
        show-icon
        :closable="false"
        style="margin-bottom: 16px;"
      />
      <el-alert
        v-else-if="!loading"
        title="当前所有商品库存充足，无预警。"
        type="success"
        show-icon
        :closable="false"
        style="margin-bottom: 16px;"
      />

      <el-table v-loading="loading" :data="list" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="封面" width="70">
          <template #default="{ row }">
            <img v-if="row.cover_url || row.cover" :src="row.cover_url || row.cover" style="width:45px;height:57px;object-fit:cover;border-radius:2px;" @error="(e) => (e.target.style.display = 'none')" />
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="书名" min-width="150" />
        <el-table-column prop="author" label="作者" width="100" />
        <el-table-column prop="merchant_name" label="商家" width="130" />
        <el-table-column prop="stock" label="当前库存" width="100">
          <template #default="{ row }">
            <el-tag type="danger">{{ row.stock }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="warning_stock" label="预警阈值" width="100" />
        <el-table-column prop="price" label="价格" width="90">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="sales" label="累计销量" width="90" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_on_sale ? 'success' : 'info'" size="small">
              {{ row.is_on_sale ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="fetchData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

const list = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

async function fetchData() {
  loading.value = true
  try {
    const res = await adminApi.getLowStock({ page: page.value, page_size: pageSize.value })
    const data = res.data
    list.value = data.results
    total.value = data.total
  } catch {
    ElMessage.error('获取库存预警数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
.main-card {
  border-radius: 12px !important;
  :deep(.el-card__header) { padding: 14px 20px; }
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
