<template>
  <div class="admin-books-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>图书管理（全平台）</span>
          <el-button type="warning" text @click="viewLowStock">全平台库存预警</el-button>
        </div>
      </template>

      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索书名、作者、ISBN、商家"
          clearable
          style="width:320px"
          @keyup.enter="fetchBooks"
          @clear="fetchBooks"
        />
        <el-button @click="fetchBooks">搜索</el-button>
      </div>

      <el-table v-loading="loading" :data="books" stripe>
        <el-table-column label="封面" width="70">
          <template #default="{ row }">
            <img v-if="row.cover" :src="row.cover" style="width:45px;height:57px;object-fit:cover;border-radius:2px;" />
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="书名" min-width="150" />
        <el-table-column prop="author" label="作者" width="100" />
        <el-table-column prop="merchant_name" label="商家" width="120" />
        <el-table-column prop="price" label="价格" width="90">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80">
          <template #default="{ row }">
            <el-text :type="row.is_low_stock ? 'danger' : ''">{{ row.stock }}</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="sales" label="销量" width="80" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_on_sale ? 'success' : 'info'">
              {{ row.is_on_sale ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <el-button text :type="row.is_on_sale ? 'warning' : 'success'" @click="toggleSale(row)">
              {{ row.is_on_sale ? '下架' : '上架' }}
            </el-button>
            <el-button text type="danger" @click="deleteBook(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next, total"
          @current-change="fetchBooks"
        />
      </div>
    </el-card>

    <!-- Category Management -->
    <el-card style="margin-top:20px">
      <template #header>
        <div class="card-header">
          <span>分类管理</span>
          <el-button type="primary" size="small" @click="openCatDialog()">+ 新增分类</el-button>
        </div>
      </template>
      <el-table :data="categories" stripe size="small">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="分类名称" />
        <el-table-column label="父分类" width="120">
          <template #default="{ row }">
            {{ row.parent ? categories.find(c => c.id === row.parent)?.name : '顶级' }}
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button text type="primary" @click="openCatDialog(row)">编辑</el-button>
            <el-button text type="danger" @click="deleteCategory(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Category Dialog -->
    <el-dialog v-model="catDialogVisible" :title="editingCat ? '编辑分类' : '新增分类'" width="400px">
      <el-form ref="catFormRef" :model="catForm" label-width="80px">
        <el-form-item label="分类名称" :rules="[{ required: true, message: '请输入名称' }]" prop="name">
          <el-input v-model="catForm.name" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-select v-model="catForm.parent" placeholder="顶级分类" clearable style="width:100%">
            <el-option
              v-for="cat in topCategories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="catForm.sort_order" :min="0" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="catDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="catSubmitting" @click="submitCategory">保存</el-button>
      </template>
    </el-dialog>

    <!-- Low Stock Dialog -->
    <el-dialog v-model="lowStockVisible" title="全平台库存预警" width="650px">
      <el-empty v-if="!lowStockBooks.length" description="暂无库存预警商品" />
      <el-table v-else :data="lowStockBooks" size="small">
        <el-table-column prop="title" label="书名" />
        <el-table-column prop="merchant_name" label="商家" width="120" />
        <el-table-column prop="stock" label="当前库存" width="100" />
        <el-table-column prop="warning_stock" label="预警库存" width="100" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api'

const books = ref([])
const categories = ref([])
const lowStockBooks = ref([])
const loading = ref(false)
const catSubmitting = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchQuery = ref('')
const dialogVisible = ref(false)
const catDialogVisible = ref(false)
const lowStockVisible = ref(false)
const editingCat = ref(null)
const catFormRef = ref()

const catForm = reactive({ name: '', parent: null, sort_order: 0 })

const topCategories = computed(() => categories.value.filter((c) => !c.parent))

async function fetchBooks(page = 1) {
  loading.value = true
  currentPage.value = page
  try {
    const params = { page: currentPage.value }
    if (searchQuery.value) params.search = searchQuery.value
    const res = await adminApi.getBookList(params)
    books.value = res.data?.results || res.results || []
    total.value = res.data?.total || res.total || 0
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const res = await adminApi.getCategories()
    const list = res.data?.results || res.data || res || []
    const flat = []
    ;(Array.isArray(list) ? list : []).forEach((cat) => {
      flat.push(cat)
      ;(cat.children || []).forEach((c) => flat.push({ ...c }))
    })
    categories.value = flat
  } catch { /* ignore */ }
}

async function toggleSale(book) {
  try {
    await adminApi.updateBook(book.id, { is_on_sale: !book.is_on_sale })
    ElMessage.success(book.is_on_sale ? '已下架' : '已上架')
    fetchBooks(currentPage.value)
  } catch {
    ElMessage.error('操作失败')
  }
}

async function deleteBook(book) {
  await ElMessageBox.confirm(`确定删除《${book.title}》？`, '提示', { type: 'warning' })
  try {
    await adminApi.deleteBook(book.id)
    ElMessage.success('已删除')
    fetchBooks(currentPage.value)
  } catch {
    ElMessage.error('删除失败')
  }
}

async function viewLowStock() {
  try {
    const res = await adminApi.getLowStock()
    lowStockBooks.value = res.results || res.data?.results || res.data || []
    lowStockVisible.value = true
  } catch {
    ElMessage.error('获取失败')
  }
}

function openCatDialog(cat = null) {
  editingCat.value = cat
  if (cat) {
    Object.assign(catForm, { name: cat.name, parent: cat.parent, sort_order: cat.sort_order })
  } else {
    Object.assign(catForm, { name: '', parent: null, sort_order: 0 })
  }
  catDialogVisible.value = true
}

async function submitCategory() {
  await catFormRef.value.validate()
  catSubmitting.value = true
  try {
    if (editingCat.value) {
      await adminApi.updateCategory(editingCat.value.id, catForm)
      ElMessage.success('分类已更新')
    } else {
      await adminApi.createCategory(catForm)
      ElMessage.success('分类已创建')
    }
    catDialogVisible.value = false
    fetchCategories()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '操作失败')
  } finally {
    catSubmitting.value = false
  }
}

async function deleteCategory(cat) {
  await ElMessageBox.confirm(`确定删除分类「${cat.name}」？`, '提示', { type: 'warning' })
  try {
    await adminApi.deleteCategory(cat.id)
    ElMessage.success('分类已删除')
    fetchCategories()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchBooks()
  fetchCategories()
})
</script>

<style lang="scss" scoped>
.admin-books-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

:deep(.el-card) {
  border-radius: 12px !important;
}

:deep(.el-card__header) {
  padding: 14px 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
