<template>
  <div class="merchant-books-page">
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">图书管理</span>
          <div class="header-actions">
            <el-button type="warning" plain :icon="Warning" size="small" @click="viewLowStock">库存预警</el-button>
            <el-button type="primary" :icon="Plus" @click="openDialog()">新增图书</el-button>
          </div>
        </div>
      </template>

      <!-- Search bar -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索书名、作者、ISBN"
          clearable
          style="width: 320px"
          :prefix-icon="Search"
          @keyup.enter="() => { currentPage = 1; fetchBooks() }"
          @clear="() => { currentPage = 1; fetchBooks() }"
        />
        <el-button type="primary" plain @click="() => { currentPage = 1; fetchBooks() }">搜索</el-button>
      </div>

      <el-table v-loading="loading" :data="books" stripe row-key="id">
        <el-table-column label="封面" width="72" align="center">
          <template #default="{ row }">
            <div class="cover-cell">
              <img v-if="row.cover_url || row.cover" :src="row.cover_url || row.cover" class="book-cover" @error="(e) => (e.target.style.display = 'none')" />
              <div v-else class="cover-placeholder">📖</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="书名 / 作者" min-width="180">
          <template #default="{ row }">
            <div class="book-title-cell">
              <div class="book-title">{{ row.title }}</div>
              <div class="book-author">{{ row.author }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="90" align="right">
          <template #default="{ row }">
            <span class="price">¥{{ row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="90" align="center">
          <template #default="{ row }">
            <span :class="row.is_low_stock ? 'stock-low' : 'stock-ok'">{{ row.stock }}</span>
            <el-icon v-if="row.is_low_stock" color="#ff4d4f" style="margin-left:4px"><Warning /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="sales" label="累计销量" width="90" align="center" />
        <el-table-column prop="is_on_sale" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_on_sale ? 'success' : 'info'" effect="light" round size="small">
              {{ row.is_on_sale ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="openDialog(row)">编辑</el-button>
            <el-button size="small" :type="row.is_on_sale ? 'warning' : 'success'" plain @click="toggleSale(row)">
              {{ row.is_on_sale ? '下架' : '上架' }}
            </el-button>
            <el-button size="small" type="danger" plain @click="deleteBook(row)">删除</el-button>
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
      width="620px"
      align-center
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="16">
            <el-form-item label="书名" prop="title">
              <el-input v-model="form.title" placeholder="请输入书名" />
            </el-form-item>
            <el-form-item label="作者" prop="author">
              <el-input v-model="form.author" placeholder="请输入作者" />
            </el-form-item>
            <el-form-item label="分类">
              <el-select v-model="form.category" placeholder="选择分类" clearable style="width:100%">
                <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="ISBN">
              <el-input v-model="form.isbn" placeholder="978-..." />
            </el-form-item>
            <el-form-item label="出版社">
              <el-input v-model="form.publisher" />
            </el-form-item>
            <el-form-item label="出版日期">
              <el-date-picker v-model="form.publish_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="封面图" label-width="60px">
              <div class="cover-preview-wrap">
                <img v-if="form.cover" :src="form.cover" class="cover-preview" @error="(e) => (e.target.style.display = 'none')" />
                <div v-else class="cover-placeholder-lg">📖</div>
              </div>
            </el-form-item>
            <el-form-item label="封面URL" label-width="60px">
              <el-input v-model="form.cover" type="textarea" :rows="3" placeholder="封面图片URL" size="small" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider />

        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="价格" prop="price">
              <el-input-number v-model="form.price" :precision="2" :min="0.01" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="库存" prop="stock">
              <el-input-number v-model="form.stock" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="预警库存">
              <el-input-number v-model="form.warning_stock" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="书籍简介（可选）" />
        </el-form-item>
        <el-form-item label="上架销售">
          <el-switch
            v-model="form.is_on_sale"
            active-text="上架中"
            inactive-text="已下架"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitBook">
          {{ editing ? '保存修改' : '创建图书' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Low Stock Dialog -->
    <el-dialog v-model="lowStockVisible" title="⚠️ 库存预警商品" width="560px" align-center>
      <el-empty v-if="!lowStockBooks.length" description="暂无库存预警商品，库存充足 ✅" />
      <el-table v-else :data="lowStockBooks" size="small" stripe>
        <el-table-column prop="title" label="书名" min-width="150" show-overflow-tooltip />
        <el-table-column prop="stock" label="当前库存" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="danger" size="small">{{ row.stock }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="warning_stock" label="预警阈值" width="100" align="center" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Warning, Search } from '@element-plus/icons-vue'
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
  description: '', is_on_sale: true, cover: '',
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
      description: book.description, is_on_sale: book.is_on_sale, cover: book.cover || '',
    })
  } else {
    Object.assign(form, {
      title: '', author: '', category: null, isbn: '', publisher: '',
      publish_date: null, price: 0, stock: 0, warning_stock: 10,
      description: '', is_on_sale: true, cover: '',
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
.merchant-books-page { }

.main-card {
  border-radius: 12px !important;
  :deep(.el-card__header) { padding: 14px 20px; }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  .card-title { font-size: 15px; font-weight: 600; color: #1a1a1a; }
  .header-actions { display: flex; gap: 8px; }
}

.search-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

// ── Table Cells ──────────────────────────────────────
.cover-cell {
  display: flex;
  align-items: center;
  justify-content: center;

  .book-cover {
    width: 42px;
    height: 54px;
    object-fit: cover;
    border-radius: 3px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.15);
  }

  .cover-placeholder {
    width: 42px;
    height: 54px;
    background: #f5f5f5;
    border-radius: 3px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
  }
}

.book-title-cell {
  .book-title { font-size: 13px; font-weight: 600; color: #1a1a1a; }
  .book-author { font-size: 12px; color: #999; margin-top: 2px; }
}

.price { font-weight: 600; color: #c75b39; }
.stock-low { color: #ff4d4f; font-weight: 600; }
.stock-ok { color: #52c41a; font-weight: 600; }

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

// ── Cover Preview ─────────────────────────────────────
.cover-preview-wrap {
  width: 100%;
  aspect-ratio: 3/4;
  background: #f5f5f5;
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;

  .cover-preview {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .cover-placeholder-lg {
    font-size: 36px;
  }
}
</style>
