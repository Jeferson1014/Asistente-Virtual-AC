<template>
  <div class="landing-container">
    <div class="aurora-bg">
      <div class="aurora-blob blob-1"></div>
      <div class="aurora-blob blob-2"></div>
      <div class="aurora-blob blob-3"></div>
      <div class="noise-overlay"></div>
    </div>

    <div class="content-wrapper">
      <nav class="navbar animate-fade-down">
        <div class="logo">
          <div class="icon-box">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
          </div>
          <span>Asistente Virtual</span>
        </div>
      </nav>
      <header class="hero-section">
        <div class="hero-content animate-fade-up">
          <div class="badge">
            <span class="pulse-dot"></span> Nueva Versión 2.0 con IA Emocional
          </div>
          
          <h1 class="title">
            Tu compañero de bienestar <br />
            <span class="text-gradient">disponible 24/7</span>
          </h1>
          
          <p class="description">
            Un espacio seguro para hablar, desahogarte y encontrar calma. 
            Nuestra IA detecta tus emociones y adapta el entorno para ti.
            Totalmente privado y empático.
          </p>

          <div class="cta-group">
            <button @click="irAlChat" class="btn-primary">
              <span>Hablar con el Asistente Psicologico</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
            </button>
            
            <button @click="irAlAsistente" class="btn-secondary">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>
                <span>Asistente Virtual</span>
            </button>
          </div>
        </div>
        <div class="hero-visual animate-fade-in">
           <div class="glass-card-preview">
              <div class="mock-chat">
                 <div class="mock-bubble user">Me siento un poco ansioso hoy...</div>
                 <div class="mock-bubble ai">Entiendo. Respira profundo. Estoy aquí contigo. ¿Quieres que cambie el ambiente a un color más relajante?</div>
              </div>
              <div class="glow-effect"></div>
           </div>
        </div>
      </header>
      <footer class="footer animate-fade-in">
        <p>ASISTENTE VIRTUAL PARA EL CURSO DE ARQUITECTURA DE COMPUTADORAS</p>
      </footer>

    </div>
  </div>
</template>

<script>
export default {
  name: 'LandingPage',
  methods: {
    irAlChat() {
      if (this.$router) {
        this.$router.push('/asistente-psicologico'); 
      } else {
        window.location.href = '/asistente-psicologico'; 
      }
    },
    irAlAsistente() {
      if (this.$router) {
        this.$router.push('/mic-control');
      } else {
        window.location.href = '/mic-control';
      }
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');
.landing-container {
  min-height: 100vh; width: 100vw; overflow-x: hidden;
  background-color: #0f172a; color: #fff;
  font-family: 'Plus Jakarta Sans', sans-serif;
  position: relative;
}

.aurora-bg {
  position: absolute; inset: 0; pointer-events: none; z-index: 0; overflow: hidden;
}
.aurora-blob {
  position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.5;
  animation: float 10s infinite alternate cubic-bezier(0.4, 0, 0.2, 1);
}
.blob-1 { width: 50vw; height: 50vw; background: #3b82f6; top: -10%; left: -10%; }
.blob-2 { width: 40vw; height: 40vw; background: #8b5cf6; bottom: -10%; right: -10%; animation-delay: -2s; }
.blob-3 { width: 30vw; height: 30vw; background: #ec4899; top: 40%; left: 30%; animation-delay: -4s; opacity: 0.3; }
.noise-overlay {
  position: absolute; inset: 0; opacity: 0.05;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}
.content-wrapper {
  position: relative; z-index: 10;
  max-width: 1200px; margin: 0 auto; padding: 0 20px;
  display: flex; flex-direction: column; min-height: 100vh;
}
.navbar {
  display: flex; justify-content: space-between; align-items: center; padding: 30px 0;
}
.logo { display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 1.2rem; }
.icon-box {
  width: 40px; height: 40px; background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white;
}
.nav-links .link {
  margin-left: 30px; text-decoration: none; color: #94a3b8; font-weight: 500; transition: 0.2s;
}
.nav-links .link:hover { color: #fff; }

.hero-section {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; gap: 40px; padding: 40px 0;
}

.badge {
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  padding: 6px 16px; border-radius: 20px; font-size: 0.9rem; color: #a8c7fa;
  margin-bottom: 20px;
}
.pulse-dot { width: 8px; height: 8px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 10px #22c55e; }

.title {
  font-size: 4rem; font-weight: 800; line-height: 1.1; letter-spacing: -0.02em; margin: 0;
}
.text-gradient {
  background: linear-gradient(to right, #60a5fa, #c084fc); -webkit-background-clip: text; color: transparent;
}

.description {
  font-size: 1.25rem; color: #94a3b8; max-width: 600px; line-height: 1.6;
}

.cta-group {
  display: flex; gap: 20px; margin-top: 10px; flex-wrap: wrap; justify-content: center;
}

.btn-primary {
  background: #2563eb; color: white; padding: 16px 32px; border-radius: 12px;
  font-size: 1.1rem; font-weight: 700; border: none; cursor: pointer;
  display: flex; align-items: center; gap: 10px; transition: 0.3s;
  box-shadow: 0 10px 30px -10px rgba(37, 99, 235, 0.5);
}
.btn-primary:hover { transform: translateY(-3px); background: #1d4ed8; box-shadow: 0 20px 40px -10px rgba(37, 99, 235, 0.6); }

.btn-secondary {
  background: rgba(255,255,255,0.05); color: white; padding: 16px 32px; border-radius: 12px;
  font-size: 1.1rem; font-weight: 600; border: 1px solid rgba(255,255,255,0.1); cursor: pointer;
  display: flex; align-items: center; gap: 10px; transition: 0.3s;
}
.btn-secondary:hover { background: rgba(255,255,255,0.1); }

.hero-visual { margin-top: 40px; width: 100%; max-width: 700px; }
.glass-card-preview {
  background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 24px; padding: 30px;
  position: relative; overflow: hidden;
}
.mock-chat { display: flex; flex-direction: column; gap: 15px; align-items: flex-start; }
.mock-bubble { padding: 12px 20px; border-radius: 16px; font-size: 1rem; color: #e2e8f0; }
.mock-bubble.user { background: #2563eb; align-self: flex-end; border-bottom-right-radius: 4px; }
.mock-bubble.ai { background: #1e293b; border: 1px solid rgba(255,255,255,0.1); border-bottom-left-radius: 4px; }

/* FOOTER */
.footer { padding: 30px 0; text-align: center; color: #64748b; font-size: 0.9rem; border-top: 1px solid rgba(255,255,255,0.05); }

.animate-fade-down { animation: fadeInDown 0.8s ease-out forwards; opacity: 0; }
.animate-fade-up { animation: fadeInUp 0.8s ease-out 0.2s forwards; opacity: 0; }
.animate-fade-in { animation: fadeIn 1s ease-out 0.5s forwards; opacity: 0; }

@keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes float { 0% { transform: translate(0,0); } 100% { transform: translate(20px, 20px); } }

@media(max-width: 768px) {
  .title { font-size: 2.5rem; }
  .cta-group { flex-direction: column; width: 100%; }
  .btn-primary, .btn-secondary { width: 100%; justify-content: center; }
}
</style>