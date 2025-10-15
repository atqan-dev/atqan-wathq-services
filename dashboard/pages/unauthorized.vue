<template>
  <div class="unauthorized-container">
    <div class="error-illustration">
      <div class="numbers">
        <div class="number-4">4</div>
        <div class="door-container">
          <div class="door">
            <div class="doorknob"></div>
            <div class="sign">{{ t('unauthorized.private') }}</div>
          </div>
        </div>
        <div class="number-3">3</div>
      </div>
      <div class="people">
        <div class="person person-sitting"></div>
        <div class="person person-standing"></div>
      </div>
    </div>
    
    <h1 class="error-title">{{ t('unauthorized.title') }}</h1>
    <p class="error-message">{{ t('unauthorized.message') }}</p>
    <p class="error-submessage">{{ t('unauthorized.submessage') }}</p>
    
    <div class="actions">
      <NuxtLink to="/" class="btn btn-primary">
        {{ t('unauthorized.goBack') }}
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

const { t } = useI18n()
</script>

<style scoped>
.unauthorized-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

.error-illustration {
  position: relative;
  width: 100%;
  height: 250px;
  margin-bottom: 2rem;
}

.numbers {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.number-4, .number-3 {
  font-size: 10rem;
  font-weight: 300;
  color: #f0f4f9;
  line-height: 1;
  position: relative;
  z-index: 1;
}

.door-container {
  position: relative;
  width: 120px;
  height: 180px;
  margin: 0 10px;
}

.door {
  width: 100%;
  height: 100%;
  background-color: #fff;
  border: 2px solid #6b7280;
  border-radius: 50% 50% 0 0;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.doorknob {
  position: absolute;
  width: 15px;
  height: 15px;
  background-color: #6b7280;
  border-radius: 50%;
  right: 15px;
  top: 50%;
}

.sign {
  background-color: #6b7280;
  color: white;
  padding: 2px 8px;
  font-size: 0.7rem;
  border-radius: 4px;
}

.people {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
}

.person {
  position: relative;
  z-index: 2;
}

.error-title {
  font-size: 2.5rem;
  color: #4a2c82;
  margin-bottom: 1rem;
  font-weight: 600;
}

.error-message {
  font-size: 1.2rem;
  color: #4b5563;
  margin-bottom: 0.5rem;
}

.error-submessage {
  color: #6b7280;
  margin-bottom: 2rem;
}

.actions {
  margin-top: 1rem;
}

.btn {
  display: inline-block;
  padding: 0.75rem 2rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #f37973;
  color: white;
  box-shadow: 0 4px 10px rgba(0, 188, 212, 0.3);
}

.btn-primary:hover {
  background-color: #c61b1b;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 188, 212, 0.4);
}
</style>
