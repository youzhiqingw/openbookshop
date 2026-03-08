<template>
  <div class="auth-layout">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo-icon">📚</div>
        <h1>在线书店</h1>
        <p class="auth-subtitle">发现好书，享受阅读</p>
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
  background: linear-gradient(135deg, #1A3D1B 0%, #2C5F2D 40%, #4A7C4B 70%, #E8F5E9 100%);
  padding: 20px;
}

.auth-card {
  background: #fff;
  border-radius: 16px;
  padding: 48px 44px 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2), 0 4px 16px rgba(0, 0, 0, 0.1);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;

  .logo-icon {
    font-size: 48px;
    margin-bottom: 8px;
    display: block;
  }

  h1 {
    font-size: 28px;
    font-weight: 700;
    color: #2C5F2D;
    margin-bottom: 6px;
    letter-spacing: 1px;
  }

  .auth-subtitle {
    color: #999;
    font-size: 14px;
  }
}
</style>
