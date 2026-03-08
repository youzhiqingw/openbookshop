<template>
  <div class="merchant-stock-warning-view">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>库存预警</span>
          <el-button type="primary" :icon="Refresh" @click="fetchData">刷新</el-button>
        </div>
      </template>

      <el-alert
        v-if="list.length > 0"
        :title="`当前共有 ${total} 件商品库存不足，请及时补货！`"
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
            <img v-if="row.cover" :src="row.cover" style="width:45px;height:57px;object-fit:cover;border-radius:2px;" />
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="书名" min-width="160" />
        <el-table-column prop="author" label="作者" width="110" />
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
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="$router.push('/merchant/books')">去补货</el-button>
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
import { merchantApi } from '@/api'
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
    const res = await merchantApi.getLowStock({ page: page.value, page_size: pageSize.value })
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
