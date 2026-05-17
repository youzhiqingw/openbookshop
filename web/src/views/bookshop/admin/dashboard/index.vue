<template>
	<div class="dashboard-container">
		<!-- 顶部统计卡片 -->
		<el-row :gutter="16" class="stat-cards">
			<el-col :xs="12" :sm="12" :md="6" :lg="6">
				<el-card shadow="hover" class="stat-card">
					<div class="stat-card-body">
						<div class="stat-icon" style="background: #e8f4fd">
							<el-icon :size="28" color="#409EFF"><Document /></el-icon>
						</div>
						<div class="stat-info">
							<div class="stat-value">{{ overview.total_orders ?? 0 }}</div>
							<div class="stat-label">总订单数</div>
						</div>
					</div>
				</el-card>
			</el-col>
			<el-col :xs="12" :sm="12" :md="6" :lg="6">
				<el-card shadow="hover" class="stat-card">
					<div class="stat-card-body">
						<div class="stat-icon" style="background: #fdf2e8">
							<el-icon :size="28" color="#E6A23C"><Money /></el-icon>
						</div>
						<div class="stat-info">
							<div class="stat-value">¥{{ formatAmount(overview.total_sales_amount) }}</div>
							<div class="stat-label">总销售额</div>
						</div>
					</div>
				</el-card>
			</el-col>
			<el-col :xs="12" :sm="12" :md="6" :lg="6">
				<el-card shadow="hover" class="stat-card">
					<div class="stat-card-body">
						<div class="stat-icon" style="background: #e8f8f0">
							<el-icon :size="28" color="#67C23A"><Shop /></el-icon>
						</div>
						<div class="stat-info">
							<div class="stat-value">{{ overview.approved_merchants ?? 0 }}</div>
							<div class="stat-label">活跃商家</div>
						</div>
					</div>
				</el-card>
			</el-col>
			<el-col :xs="12" :sm="12" :md="6" :lg="6">
				<el-card shadow="hover" class="stat-card">
					<div class="stat-card-body">
						<div class="stat-icon" style="background: #f0e8fd">
							<el-icon :size="28" color="#9B59B6"><User /></el-icon>
						</div>
						<div class="stat-info">
							<div class="stat-value">{{ overview.total_users ?? 0 }}</div>
							<div class="stat-label">消费者总数</div>
						</div>
					</div>
				</el-card>
			</el-col>
		</el-row>

		<!-- 趋势折线图 -->
		<el-card shadow="hover" class="chart-card">
			<template #header>
				<div class="chart-header">
					<span class="chart-title">运营趋势</span>
					<el-radio-group v-model="trendDays" size="small" @change="fetchTrend">
						<el-radio-button :value="7">近7天</el-radio-button>
						<el-radio-button :value="30">近30天</el-radio-button>
						<el-radio-button :value="90">近90天</el-radio-button>
					</el-radio-group>
				</div>
			</template>
			<div ref="trendChartRef" class="chart-content"></div>
		</el-card>

		<!-- 下方两列 -->
		<el-row :gutter="16" class="bottom-charts">
			<el-col :xs="24" :sm="24" :md="12" :lg="12">
				<el-card shadow="hover" class="chart-card">
					<template #header>
						<span class="chart-title">分类分布</span>
					</template>
					<div ref="categoryChartRef" class="chart-content"></div>
				</el-card>
			</el-col>
			<el-col :xs="24" :sm="24" :md="12" :lg="12">
				<el-card shadow="hover" class="chart-card">
					<template #header>
						<div class="chart-header">
							<span class="chart-title">商家排行</span>
							<el-radio-group v-model="rankingOrderBy" size="small" @change="fetchMerchantRanking">
								<el-radio-button value="sales_amount">销售额</el-radio-button>
								<el-radio-button value="order_count">订单数</el-radio-button>
							</el-radio-group>
						</div>
					</template>
					<div ref="rankingChartRef" class="chart-content"></div>
				</el-card>
			</el-col>
		</el-row>
	</div>
</template>

<script lang="ts" setup name="bookshopDashboard">
import { ref, reactive, onMounted, onActivated, onBeforeUnmount, nextTick, watch } from 'vue';
import * as echarts from 'echarts';
import { GetOverview, GetTrend, GetCategoryDistribution, GetMerchantRanking } from '/@/api/bookshop/statistics';
import { Document, Money, Shop, User } from '@element-plus/icons-vue';
import { useThemeConfig } from '/@/stores/themeConfig';
import { storeToRefs } from 'pinia';

const { themeConfig } = storeToRefs(useThemeConfig());

// 数据
const overview = reactive<Record<string, any>>({});
const trendDays = ref(30);
const rankingOrderBy = ref('sales_amount');

// ECharts refs
const trendChartRef = ref<HTMLElement>();
const categoryChartRef = ref<HTMLElement>();
const rankingChartRef = ref<HTMLElement>();
const charts: echarts.ECharts[] = [];

// 金额格式化
const formatAmount = (val: any) => {
	if (val === undefined || val === null) return '0.00';
	return parseFloat(String(val)).toFixed(2);
};

// 获取总览
const fetchOverview = async () => {
	try {
		const res = await GetOverview();
		Object.assign(overview, res.data || {});
	} catch (e) {
		console.error('获取总览数据失败', e);
	}
};

// 获取趋势
const fetchTrend = async () => {
	try {
		const res = await GetTrend({ days: trendDays.value });
		initTrendChart(res.data || {});
	} catch (e) {
		console.error('获取趋势数据失败', e);
	}
};

// 获取分类分布
const fetchCategoryDistribution = async () => {
	try {
		const res = await GetCategoryDistribution();
		initCategoryChart(res.data || []);
	} catch (e) {
		console.error('获取分类分布失败', e);
	}
};

// 获取商家排行
const fetchMerchantRanking = async () => {
	try {
		const res = await GetMerchantRanking({ limit: 10, order_by: rankingOrderBy.value });
		initRankingChart(res.data || []);
	} catch (e) {
		console.error('获取商家排行失败', e);
	}
};

// 趋势折线图
const initTrendChart = (data: any) => {
	if (!trendChartRef.value) return;
	const chart = echarts.init(trendChartRef.value);
	charts.push(chart);
	const option: echarts.EChartsOption = {
		tooltip: { trigger: 'axis' },
		legend: { data: ['订单数', '销售额', '新用户'] },
		grid: { top: 50, right: 60, bottom: 30, left: 60 },
		xAxis: { type: 'category', data: data.dates || [], boundaryGap: false },
		yAxis: [
			{ type: 'value', name: '数量', position: 'left' },
			{ type: 'value', name: '金额(元)', position: 'right', axisLabel: { formatter: (v: number) => '¥' + v } },
		],
		series: [
			{
				name: '订单数',
				type: 'line',
				smooth: true,
				yAxisIndex: 0,
				data: data.order_count || [],
				itemStyle: { color: '#409EFF' },
				areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
					{ offset: 0, color: 'rgba(64,158,255,0.3)' },
					{ offset: 1, color: 'rgba(64,158,255,0.02)' },
				]) },
			},
			{
				name: '销售额',
				type: 'line',
				smooth: true,
				yAxisIndex: 1,
				data: (data.sales_amount || []).map((v: any) => parseFloat(String(v))),
				itemStyle: { color: '#E6A23C' },
				areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
					{ offset: 0, color: 'rgba(230,162,60,0.3)' },
					{ offset: 1, color: 'rgba(230,162,60,0.02)' },
				]) },
			},
			{
				name: '新用户',
				type: 'line',
				smooth: true,
				yAxisIndex: 0,
				data: data.new_users || [],
				itemStyle: { color: '#67C23A' },
				areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
					{ offset: 0, color: 'rgba(103,194,58,0.3)' },
					{ offset: 1, color: 'rgba(103,194,58,0.02)' },
				]) },
			},
		],
	};
	chart.setOption(option);
};

// 分类饼图
const initCategoryChart = (data: any[]) => {
	if (!categoryChartRef.value) return;
	const chart = echarts.init(categoryChartRef.value);
	charts.push(chart);
	const names = data.map((d: any) => d.category_name || '未分类');
	const bookData = data.map((d: any) => ({ name: d.category_name || '未分类', value: d.book_count || 0 }));
	const salesData = data.map((d: any) => ({ name: d.category_name || '未分类', value: d.sales_count || 0 }));
	const option: echarts.EChartsOption = {
		tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
		legend: { data: names, bottom: 0, type: 'scroll' },
		series: [
			{
				name: '图书数量',
				type: 'pie',
				radius: ['20%', '45%'],
				center: ['25%', '45%'],
				data: bookData,
				label: { show: false },
			},
			{
				name: '销量分布',
				type: 'pie',
				radius: ['20%', '45%'],
				center: ['75%', '45%'],
				data: salesData,
				label: { show: false },
			},
		],
		title: [
			{ text: '图书数量', left: '15%', top: '5%', textStyle: { fontSize: 14 } },
			{ text: '销量分布', left: '65%', top: '5%', textStyle: { fontSize: 14 } },
		],
	};
	chart.setOption(option);
};

// 商家排行柱状图
const initRankingChart = (data: any[]) => {
	if (!rankingChartRef.value) return;
	const chart = echarts.init(rankingChartRef.value);
	charts.push(chart);
	const names = data.map((d: any) => d.merchant_name || '');
	const isAmount = rankingOrderBy.value === 'sales_amount';
	const values = data.map((d: any) => isAmount ? parseFloat(String(d.sales_amount || 0)) : (d.order_count || 0));
	const option: echarts.EChartsOption = {
		tooltip: { trigger: 'axis', formatter: (params: any) => {
			const p = params[0];
			return `${p.name}<br/>${isAmount ? '¥' : ''}${p.value}${isAmount ? '' : ' 单'}`;
		}},
		grid: { top: 20, right: 30, bottom: 40, left: 100 },
		xAxis: { type: 'value', axisLabel: { formatter: isAmount ? (v: number) => '¥' + v : '{value}' } },
		yAxis: { type: 'category', data: names.reverse(), inverse: false },
		series: [{
			type: 'bar',
			data: values.reverse(),
			itemStyle: {
				color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
					{ offset: 0, color: '#409EFF' },
					{ offset: 1, color: '#67C23A' },
				]),
				borderRadius: [0, 4, 4, 0],
			},
			barWidth: 20,
		}],
	};
	chart.setOption(option);
};

// Resize
const handleResize = () => {
	charts.forEach((c) => c.resize());
};

// 主题变化时重绘
watch(() => themeConfig.value.isIsDark, () => {
	nextTick(() => {
		charts.forEach((c) => c.dispose());
		charts.length = 0;
		fetchTrend();
		fetchCategoryDistribution();
		fetchMerchantRanking();
	});
});

onMounted(async () => {
	window.addEventListener('resize', handleResize);
	await fetchOverview();
	await fetchTrend();
	await fetchCategoryDistribution();
	await fetchMerchantRanking();
});

onActivated(() => {
	handleResize();
});

onBeforeUnmount(() => {
	window.removeEventListener('resize', handleResize);
	charts.forEach((c) => c.dispose());
	charts.length = 0;
});
</script>

<style scoped lang="scss">
.dashboard-container {
	padding: 16px;
}

.stat-cards {
	margin-bottom: 16px;
}

.stat-card {
	.stat-card-body {
		display: flex;
		align-items: center;
		gap: 16px;
	}
	.stat-icon {
		width: 56px;
		height: 56px;
		border-radius: 12px;
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
		color: var(--el-text-color-primary);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.stat-label {
		font-size: 13px;
		color: var(--el-text-color-secondary);
		margin-top: 4px;
	}
}

.chart-card {
	margin-bottom: 16px;
}

.chart-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.chart-title {
	font-size: 16px;
	font-weight: 600;
}

.chart-content {
	height: 360px;
	width: 100%;
}

.bottom-charts {
	.chart-content {
		height: 320px;
	}
}
</style>
