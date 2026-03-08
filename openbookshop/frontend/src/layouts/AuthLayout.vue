<template>
  <div class="auth-layout">
    <div class="auth-card">
      <div class="auth-header">
        <h1>📚 在线书店</h1>
      </div>
      <RouterView />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2C5F2D 0%, #4A7C4B 50%, #E8F5E9 100%);
}

.auth-card {
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;

  h1 {
    font-size: 28px;
    font-weight: 700;
    color: #2C5F2D;
  }
}
</style>
