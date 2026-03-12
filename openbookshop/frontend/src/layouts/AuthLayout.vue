<template>
  <div class="auth-layout">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo-wrap">
          <span class="logo-icon">📚</span>
          <h1 class="logo-text">知书坊</h1>
        </div>
        <p class="logo-sub">开启阅读之旅</p>
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
  background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #bfdbfe 100%);
}

.auth-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  width: 440px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;

  .logo-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin-bottom: 8px;
  }

  .logo-icon {
    font-size: 36px;
  }

  .logo-text {
    font-size: 28px;
    font-weight: 700;
    color: #1e40af;
    margin: 0;
  }

  .logo-sub {
    color: #6b7280;
    font-size: 14px;
    margin: 0;
  }
}
</style>
