<template>
  <div class="app-container">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <div class="main-card">
      <div class="header">
        <div class="title-group">
          <div class="icon-box">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
          </div>
          <h1>Control de Voz</h1>
        </div>
        <button @click="irAAsistente" class="nav-btn" title="Ir al Asistente">
          <span>Ir al Asistente</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>
        </button>
      </div>

      <div class="control-section">
        <div class="mic-status-wrapper">
            <div class="status-dot" :class="{ 'active': isMicOn }"></div>
            <p class="status-text">{{ micStatus }}</p>
        </div>
        <button 
            @click="toggleMic" 
            class="big-mic-btn"
            :class="{ 'recording': isMicOn }"
        >
            <svg v-if="!isMicOn" xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="animate-pulse"><rect x="9" y="9" width="6" height="6" rx="1"/></svg>
        </button>
        <p class="hint-text">{{ isMicOn ? 'Te estoy escuchando...' : 'Toca el micrófono para hablar' }}</p>
      </div>

      <div class="conversation-area">
        <div v-if="mensaje" class="message-card user-card fade-in">
          <div class="card-header">
            <span class="label">Tú dijiste:</span>
          </div>
          <p class="card-text">{{ mensaje }}</p>
        </div>

        <div v-if="cargando" class="loading-indicator fade-in">
          <div class="spinner"></div>
          <span>Procesando solicitud...</span>
        </div>

        <div v-if="respuesta" class="message-card ai-card fade-in">
          <div class="card-header">
            <span class="label">Respuesta:</span>
          </div>
          <p class="card-text">{{ respuesta }}</p>
        </div>
      </div>

      <div class="footer-actions">
        <button 
            v-if="mensaje" 
            @click="enviarMensaje" 
            class="action-btn send-btn"
            :disabled="cargando"
        >
          <span>Enviar Mensaje</span>
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      mensaje: "",
      respuesta: "",
      reconocimiento: null,
      micStatus: "Micrófono apagado",
      isMicOn: false,
      cargando: false, 
    };
  },
  methods: {
    irAAsistente() {
      if (this.$router) {
        this.$router.push('/asistente-psicologico');
      } else {
        window.location.href = '/asistente-psicologico';
      }
    },

    iniciarVoz() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

      if (!SpeechRecognition) {
        alert("Tu navegador no soporta reconocimiento de voz.");
        return;
      }

      if (this.reconocimiento) {
        this.reconocimiento.stop();
        this.reconocimiento = null;
      }

      this.reconocimiento = new SpeechRecognition();
      this.reconocimiento.continuous = true;
      this.reconocimiento.lang = "es-ES";
      this.reconocimiento.interimResults = false;

      this.reconocimiento.onresult = (event) => {
        const texto = event.results[event.results.length - 1][0].transcript;
        this.mensaje = texto;
      };

      this.reconocimiento.onerror = (event) => {
        console.error("Error de reconocimiento: ", event.error);
        this.isMicOn = false;
        this.micStatus = "Error de micrófono";
      };

      this.reconocimiento.onend = () => {
        if (this.isMicOn) {
          try {
             this.reconocimiento.start(); 
          } catch (e) {
             console.log("Reconocimiento ya iniciado o error al reiniciar");
          }
        }
      };

      this.reconocimiento.start();
      this.micStatus = "Escuchando...";
    },

    detenerVoz() {
      if (this.reconocimiento) {
        this.reconocimiento.stop();
        this.micStatus = "Micrófono apagado";
      }
    },

    toggleMic() {
      this.isMicOn = !this.isMicOn;
      if (this.isMicOn) {
        this.micStatus = "Micrófono encendido";
        this.iniciarVoz();
      } else {
        this.detenerVoz();
      }
    },

    async enviarMensaje() {
      this.cargando = true;
      this.respuesta = ""; 
      
      try {
        let url = "http://127.0.0.1:8000/api/front/";
        let method = 'POST';
        let body = JSON.stringify({ mensaje: this.mensaje });

        if (this.mensaje.toLowerCase().includes("chiste")) {
          url = "http://localhost:8000/api/chiste/";
          method = 'GET';
          body = null;
        }

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: body
        });

        if (!response.ok) {
             throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (this.mensaje.toLowerCase().includes("chiste")) {
            this.respuesta = data?.chiste || "No encontré un chiste en este momento.";
        } else {
            this.respuesta = data?.message || "No hubo respuesta del servidor.";
        }
        
        this.hablar(this.respuesta);

      } catch (error) {
        console.error(error);
        this.respuesta = "Error al procesar tu solicitud.";
        this.hablar("Ocurrió un error.");
      } finally {
        this.cargando = false;
      }
    },

    hablar(texto) {
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const maxLength = 200;
        const speechArray = texto.match(new RegExp(`.{1,${maxLength}}`, "g")) || [texto];

        speechArray.forEach((fragment, index) => {
          const speech = new SpeechSynthesisUtterance(fragment);
          speech.lang = "es-ES";
          speech.pitch = 1;
          speech.rate = 0.9;
          speech.volume = 1;
          window.speechSynthesis.speak(speech);
        });
      }
    },
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.app-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #0f172a;
  color: #f8fafc;
  font-family: 'Inter', sans-serif;
  position: relative;
  overflow: hidden;
  padding: 20px;
}

.background-shapes { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; }
.shape { position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.4; animation: float 8s infinite ease-in-out; }
.shape-1 { width: 400px; height: 400px; background: #3b82f6; top: -50px; left: -50px; }
.shape-2 { width: 500px; height: 500px; background: #8b5cf6; bottom: -100px; right: -100px; animation-delay: 2s; }
.shape-3 { width: 300px; height: 300px; background: #ec4899; top: 40%; left: 40%; animation-delay: 4s; }
@keyframes float { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(20px, 20px); } }

.main-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 850px;
  background: rgba(30, 41, 59, 0.75);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 40px;
  padding: 48px;
  box-shadow: 0 40px 80px -12px rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-group {
  display: flex;
  align-items: center;
  gap: 20px;
}

.icon-box {
  width: 64px; 
  height: 64px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
}

.header h1 {
  font-size: 2.2rem;
  font-weight: 800;
  margin: 0;
  color: white;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #f1f5f9;
  padding: 14px 24px;
  border-radius: 28px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.control-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.mic-status-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
  background: rgba(15, 23, 42, 0.5);
  padding: 10px 20px;
  border-radius: 30px;
}

.status-dot { width: 12px; height: 12px; border-radius: 50%; background: #64748b; transition: background 0.3s; }
.status-dot.active { background: #ef4444; box-shadow: 0 0 12px #ef4444; }
.status-text { font-size: 1.1rem; color: #cbd5e1; margin: 0; font-weight: 500; }

.big-mic-btn {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 4px solid rgba(255, 255, 255, 0.15);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}

.big-mic-btn:hover {
  transform: scale(1.08);
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.1);
}

.big-mic-btn.recording {
  background: linear-gradient(135deg, #ef4444, #f87171);
  border-color: transparent;
  box-shadow: 0 0 50px rgba(239, 68, 68, 0.6);
  animation: pulse-ring 2s infinite;
}

.hint-text {
  margin-top: 24px;
  font-size: 1.2rem;
  color: #94a3b8;
}

.conversation-area {
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: 140px;
}

.message-card {
  padding: 24px 32px;
  border-radius: 24px;
  position: relative;
}

.user-card {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.25);
  border-left: 6px solid #3b82f6;
}

.ai-card {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-left: 6px solid #10b981;
}

.card-header .label {
  font-size: 0.9rem;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.05em;
  opacity: 0.9;
  margin-bottom: 10px;
  display: block;
}

.card-text {
  margin: 0;
  font-size: 1.25rem;
  line-height: 1.6;
  color: #f1f5f9;
}

.loading-indicator { display: flex; align-items: center; justify-content: center; gap: 14px; padding: 24px; color: #cbd5e1; font-size: 1.1rem; }
.spinner { width: 28px; height: 28px; border: 4px solid rgba(255, 255, 255, 0.1); border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; }

.footer-actions { margin-top: 10px; }

.action-btn {
  width: 100%;
  padding: 20px;
  border-radius: 20px;
  border: none;
  font-weight: 700;
  font-size: 1.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.send-btn {
  background: linear-gradient(to right, #3b82f6, #2563eb);
  color: white;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
}

.send-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 25px rgba(37, 99, 235, 0.5);
}

.send-btn:disabled { background: #334155; color: #64748b; transform: none; box-shadow: none; cursor: not-allowed; }

@keyframes pulse-ring {
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
  70% { box-shadow: 0 0 0 25px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}
@keyframes spin { to { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.4s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>