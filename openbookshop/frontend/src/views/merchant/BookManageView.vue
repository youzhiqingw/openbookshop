<template>
  <div class="merchant-books-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>图书管理</span>
          <div class="header-actions">
            <el-button type="warning" text @click="viewLowStock">库存预警</el-button>
            <el-button type="primary" @click="openDialog()">+ 新增图书</el-button>
          </div>
        </div>
      </template>

      <!-- Search -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索书名、作者、ISBN"
          clearable
          style="width: 300px"
          @keyup.enter="fetchBooks"
          @clear="fetchBooks"
        />
        <el-button @click="fetchBooks">搜索</el-button>
      </div>

      <el-table v-loading="loading" :data="books" stripe>
        <el-table-column label="封面" width="80">
          <template #default="{ row }">
            <img v-if="row.cover" :src="row.cover" style="width:50px;height:63px;object-fit:cover;border-radius:2px;" />
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="书名" min-width="150" />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="price" label="价格" width="90">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80">
          <template #default="{ row }">
            <el-text :type="row.is_low_stock ? 'danger' : ''">{{ row.stock }}</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="sales" label="销量" width="80" />
        <el-table-column prop="is_on_sale" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_on_sale ? 'success' : 'info'">
              {{ row.is_on_sale ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openDialog(row)">编辑</el-button>
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

    <!-- Book Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="editing ? '编辑图书' : '新增图书'"
      width="600px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="书名" prop="title">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="form.author" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="选择分类" clearable style="width:100%">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="ISBN">
          <el-input v-model="form.isbn" />
        </el-form-item>
        <el-form-item label="出版社">
          <el-input v-model="form.publisher" />
        </el-form-item>
        <el-form-item label="出版日期">
          <el-date-picker v-model="form.publish_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="价格" prop="price">
              <el-input-number v-model="form.price" :precision="2" :min="0.01" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="库存" prop="stock">
              <el-input-number v-model="form.stock" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="预警库存">
          <el-input-number v-model="form.warning_stock" :min="0" style="width:100%" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="是否上架">
          <el-switch v-model="form.is_on_sale" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitBook">保存</el-button>
      </template>
    </el-dialog>

    <!-- Low Stock Dialog -->
    <el-dialog v-model="lowStockVisible" title="库存预警商品" width="600px">
      <el-empty v-if="!lowStockBooks.length" description="暂无库存预警商品" />
      <el-table v-else :data="lowStockBooks" size="small">
        <el-table-column prop="title" label="书名" />
        <el-table-column prop="stock" label="当前库存" width="100" />
        <el-table-column prop="warning_stock" label="预警库存" width="100" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { merchantApi, bookApi } from '@/api'

const books = ref([])
const categories = ref([])
const lowStockBooks = ref([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const lowStockVisible = ref(false)
const editing = ref(null)
const searchQuery = ref('')
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const formRef = ref()

const form = reactive({
  title: '', author: '', category: null, isbn: '', publisher: '',
  publish_date: null, price: 0, stock: 0, warning_stock: 10,
  description: '', is_on_sale: true,
})

const rules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }],
  price: [{ required: true, type: 'number', message: '请输入价格', trigger: 'change' }],
  stock: [{ required: true, type: 'number', message: '请输入库存', trigger: 'change' }],
}

async function fetchBooks(page = 1) {
  loading.value = true
  currentPage.value = page
  try {
    const params = { page: currentPage.value }
    if (searchQuery.value) params.search = searchQuery.value
    const res = await merchantApi.getBookList(params)
    books.value = res.data?.results || res.results || []
    total.value = res.data?.total || res.total || 0
  } finally {
    loading.value = false
  }
}

async function fetchCategories() {
  try {
    const res = await bookApi.getCategories()
    const list = res.data?.results || res.data || res || []
    const flat = []
    ;(Array.isArray(list) ? list : []).forEach((cat) => {
      flat.push(cat)
      ;(cat.children || []).forEach((c) => flat.push(c))
    })
    categories.value = flat
  } catch { /* ignore */ }
}

function openDialog(book = null) {
  editing.value = book
  if (book) {
    Object.assign(form, {
      title: book.title, author: book.author, category: book.category,
      isbn: book.isbn, publisher: book.publisher, publish_date: book.publish_date,
      price: parseFloat(book.price), stock: book.stock, warning_stock: book.warning_stock,
      description: book.description, is_on_sale: book.is_on_sale,
    })
  } else {
    Object.assign(form, {
      title: '', author: '', category: null, isbn: '', publisher: '',
      publish_date: null, price: 0, stock: 0, warning_stock: 10,
      description: '', is_on_sale: true,
    })
  }
  dialogVisible.value = true
}

async function submitBook() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const payload = { ...form }
    if (!payload.category) delete payload.category
    if (!payload.publish_date) delete payload.publish_date
    if (editing.value) {
      await merchantApi.updateBook(editing.value.id, payload)
      ElMessage.success('图书更新成功')
    } else {
      await merchantApi.createBook(payload)
      ElMessage.success('图书创建成功')
    }
    dialogVisible.value = false
    fetchBooks(currentPage.value)
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function toggleSale(book) {
  try {
    await merchantApi.updateBook(book.id, { is_on_sale: !book.is_on_sale })
    ElMessage.success(book.is_on_sale ? '已下架' : '已上架')
    fetchBooks(currentPage.value)
  } catch {
    ElMessage.error('操作失败')
  }
}

async function deleteBook(book) {
  await ElMessageBox.confirm(`确定删除《${book.title}》？`, '提示', { type: 'warning' })
  try {
    await merchantApi.deleteBook(book.id)
    ElMessage.success('已删除')
    fetchBooks(currentPage.value)
  } catch {
    ElMessage.error('删除失败')
  }
}

async function viewLowStock() {
  try {
    const res = await merchantApi.getLowStock()
    lowStockBooks.value = res.results || res.data?.results || res.data || []
    lowStockVisible.value = true
  } catch {
    ElMessage.error('获取预警信息失败')
  }
}

onMounted(() => {
  fetchBooks()
  fetchCategories()
})
</script>

<style lang="scss" scoped>
.merchant-books-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
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
