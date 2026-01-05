<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  height: 100%;
}

body {
  margin: 0 !important;
  padding: 0 !important;
  min-height: 100% !important;
  width: 100% !important;
  background-color: #0f172a !important; /* Slate 900 */
  color: #f8fafc;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  display: block !important; 
  place-items: unset !important;
  overflow-x: hidden;
}

#app {
  width: 100%;
  min-height: 100vh;
  margin: 0 auto;
  padding: 0;
  display: block;
}

/* Scrollbar oscura */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #475569; }
</style>