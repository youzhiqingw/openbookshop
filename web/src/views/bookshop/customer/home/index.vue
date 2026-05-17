<template>
	<div class="customer-home">
		<el-empty description="书城首页即将上线，敬请期待">
			<el-button type="primary" @click="$router.push('/bookshop/home')">刷新</el-button>
		</el-empty>
	</div>
</template>

<script lang="ts" setup name="customerHome">
</script>

<style scoped>
.customer-home {
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: 60vh;
}
</style>
