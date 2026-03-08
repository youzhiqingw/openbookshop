# 在线书店界面设计规范

## 设计原则

清晰优先、阅读友好、操作直观、书卷气息与现代感结合。

---

## 色彩系统

### 主色调

| 角色 | 色值 | 用途 |
|------|------|------|
| 主色 | `#2C5F2D` | 品牌色、主要按钮、导航激活 |
| 主色浅 | `#4A7C4B` | 悬停状态 |
| 主色淡 | `#E8F5E9` | 背景高亮、标签背景 |

### 辅助色

| 角色 | 色值 | 用途 |
|------|------|------|
| 强调色 | `#C75B39` | 价格、促销标签、重要提醒 |
| 强调色浅 | `#E07A5F` | 悬停状态 |
| 强调色淡 | `#FBE9E7` | 促销背景 |

### 中性色

| 角色 | 色值 | 用途 |
|------|------|------|
| 标题文字 | `#1A1A1A` | 主标题、重要文本 |
| 正文文字 | `#333333` | 正文内容 |
| 次要文字 | `#666666` | 辅助说明、作者信息 |
| 占位文字 | `#999999` | 输入框 placeholder |
| 边框浅色 | `#E5E5E5` | 分割线、输入框边框 |
| 背景灰 | `#F5F5F5` | 页面背景、表格表头 |
| 纯白 | `#FFFFFF` | 卡片背景、侧边栏 |

### 功能色

| 角色 | 色值 | 用途 |
|------|------|------|
| 成功 | `#52C41A` | 成功提示、库存充足 |
| 警告 | `#FAAD14` | 警告提示、库存预警 |
| 错误 | `#F5222D` | 错误提示、缺货状态 |
| 信息 | `#1890FF` | 普通信息提示 |

---

## 布局系统

### 网格系统

- 容器最大宽度：`1200px`
- 栅格：12 列
- 间距：`24px`（标准）/ `16px`（紧凑）/ `32px`（宽松）

### 响应式断点

| 设备 | 断点 |
|------|------|
| 桌面大屏 | ≥ 1440px |
| 桌面 | 1200px – 1439px |
| 平板横屏 | 992px – 1199px |
| 平板竖屏 | 768px – 991px |
| 手机 | < 768px |

### 间距规范

| 尺寸 | 值 |
|------|----|
| xs | 4px |
| sm | 8px |
| md | 16px |
| lg | 24px |
| xl | 32px |
| 2xl | 48px |
| 3xl | 64px |

---

## 核心组件

### 按钮

```css
/* 主要按钮 */
.btn-primary {
  background: #2C5F2D;
  color: #FFFFFF;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}
.btn-primary:hover { background: #4A7C4B; }

/* 次要按钮 */
.btn-secondary {
  background: #FFFFFF;
  color: #2C5F2D;
  border: 1px solid #2C5F2D;
  padding: 12px 24px;
  border-radius: 4px;
}
.btn-secondary:hover { background: #E8F5E9; }

/* 强调按钮 */
.btn-accent {
  background: #C75B39;
  color: #FFFFFF;
  padding: 12px 24px;
  border-radius: 4px;
}
.btn-accent:hover { background: #E07A5F; }
```

### 图书卡片

```css
.book-card {
  background: #FFFFFF;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: box-shadow 0.3s, transform 0.3s;
  cursor: pointer;
}
.book-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  transform: translateY(-4px);
}
.book-card-cover {
  width: 100%;
  aspect-ratio: 3/4;
  object-fit: cover;
  background: #F5F5F5;
}
.book-card-info { padding: 16px; }
.book-card-title {
  font-size: 14px;
  font-weight: 600;
  color: #1A1A1A;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 8px;
}
.book-card-author {
  font-size: 13px;
  color: #666666;
  margin-bottom: 12px;
}
.book-card-price {
  font-size: 16px;
  font-weight: 700;
  color: #C75B39;
}
```

### 输入框

```css
.input {
  height: 40px;
  padding: 0 12px;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  font-size: 14px;
  color: #333333;
  background: #FFFFFF;
  transition: border-color 0.3s;
  width: 100%;
}
.input:hover { border-color: #4A7C4B; }
.input:focus {
  border-color: #2C5F2D;
  outline: none;
  box-shadow: 0 0 0 3px rgba(44,95,45,0.1);
}
.input::placeholder { color: #999999; }
```

### 搜索框

```css
.search-box {
  display: flex;
  align-items: center;
  background: #F5F5F5;
  border-radius: 20px;
  padding: 0 16px;
  height: 40px;
  transition: background 0.3s;
}
.search-box:focus-within {
  background: #FFFFFF;
  box-shadow: 0 0 0 2px #2C5F2D;
}
.search-box input {
  border: none;
  background: transparent;
  flex: 1;
  margin-left: 8px;
  outline: none;
}
```

### 标签

```css
.tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
.tag-primary { background: #E8F5E9; color: #2C5F2D; }
.tag-accent  { background: #FBE9E7; color: #C75B39; }
.tag-gray    { background: #F5F5F5; color: #666666; }
```

### 导航

```css
/* 顶部导航 */
.navbar {
  height: 64px;
  background: #FFFFFF;
  border-bottom: 1px solid #E5E5E5;
  position: sticky;
  top: 0;
  z-index: 100;
}
.navbar-logo {
  font-size: 24px;
  font-weight: 700;
  color: #2C5F2D;
}
.navbar-menu { display: flex; gap: 32px; }
.navbar-menu-item {
  font-size: 14px;
  color: #333333;
  text-decoration: none;
  padding: 4px 0;
}
.navbar-menu-item:hover,
.navbar-menu-item.active { color: #2C5F2D; }
.navbar-menu-item.active {
  font-weight: 500;
  border-bottom: 2px solid #2C5F2D;
}

/* 侧边导航 */
.sidebar {
  width: 240px;
  background: #FFFFFF;
  border-right: 1px solid #E5E5E5;
  height: calc(100vh - 64px);
  position: fixed;
  left: 0;
  top: 64px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  color: #666666;
  gap: 12px;
  transition: all 0.3s;
}
.sidebar-item:hover {
  background: #F5F5F5;
  color: #333333;
}
.sidebar-item.active {
  background: #E8F5E9;
  color: #2C5F2D;
  border-right: 3px solid #2C5F2D;
}
```

### 表格

```css
.table {
  width: 100%;
  border-collapse: collapse;
  background: #FFFFFF;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.table th {
  background: #F5F5F5;
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #1A1A1A;
  font-size: 14px;
  border-bottom: 1px solid #E5E5E5;
}
.table td {
  padding: 16px;
  border-bottom: 1px solid #E5E5E5;
  color: #333333;
  font-size: 14px;
}
.table tr:hover td { background: #FAFAFA; }
```

---

## 三端风格指南

### 用户端

- **顶部导航**：白色背景，品牌绿 Logo，导航激活项带绿色下划线
- **图书卡片**：白色圆角卡片，悬停上浮 + 深阴影，价格用强调红
- **购物车 / 结算**：主操作按钮使用主色绿，次要操作使用次要按钮样式
- **页面背景**：浅灰 `#F5F5F5`，内容区白色卡片

### 管理端

- **侧边栏**：白色背景，激活项浅绿背景 + 左侧绿色竖线
- **顶部**：白色，面包屑导航
- **数据卡片**：白色圆角卡片，统计数字强调显示
- **表格**：圆角阴影，表头灰底，行悬停浅灰

### 商家端

- **侧边栏**：白色背景（与管理端同风格，但 Logo 区标注"商家中心"）
- **图表区**：使用功能色配合主色调形成数据可视化色板
- **操作流程**：强调清晰的操作状态（待处理 → 处理中 → 完成）

### 登录 / 注册

- **背景**：浅绿渐变，体现品牌调性
- **卡片**：白色圆角，阴影适中
- **表单链接**：使用主色绿，悬停下划线

---

## 字体规范

```css
font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
```

| 层级 | 字号 | 字重 | 用途 |
|------|------|------|------|
| 大标题 | 28px | 700 | 页面主标题 |
| 标题 | 22–24px | 600 | 区块标题 |
| 小标题 | 16–18px | 600 | 卡片标题 |
| 正文 | 14px | 400 | 主要内容 |
| 辅助文字 | 12–13px | 400 | 标注、元数据 |

行高：正文 `1.6`，标题 `1.3`，卡片标题 `1.4`

---

## 圆角与阴影

| 类型 | 值 |
|------|----|
| 小圆角（按钮、标签、输入框）| `4px` |
| 中圆角（卡片）| `8px` |
| 大圆角（搜索框、头像）| `20px` / `50%` |

| 层级 | 阴影 |
|------|------|
| 卡片默认 | `0 2px 8px rgba(0,0,0,0.08)` |
| 卡片悬停 | `0 8px 24px rgba(0,0,0,0.12)` |
| 弹窗 | `0 20px 60px rgba(0,0,0,0.2)` |
| 表格 | `0 2px 8px rgba(0,0,0,0.06)` |

---

## 过渡动画

所有交互元素使用统一过渡：

```css
transition: all 0.3s ease;
```

卡片悬停上浮：`transform: translateY(-4px)`
