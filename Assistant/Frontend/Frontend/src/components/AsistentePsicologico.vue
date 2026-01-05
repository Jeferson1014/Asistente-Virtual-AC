<template>
  <div class="app-layout" :style="{ '--active-color': activeColor }">
    
    <div class="aurora-bg">
      <div class="aurora-blob blob-1"></div>
      <div class="aurora-blob blob-2"></div>
      <div class="aurora-blob blob-3"></div>
      <div class="noise-overlay"></div>
    </div>
    <canvas ref="canvas" class="visualizer-canvas"></canvas>

    <aside class="sidebar" :class="{ 'sidebar-closed': !isSidebarOpen }">
      <div class="sidebar-top">
        <button @click="nuevoChat" class="new-chat-btn">
          <span class="icon">+</span>
          <span>Nuevo chat</span>
        </button>
      </div>

      <div class="sidebar-content">
        <div class="history-section">
          <h3 class="history-label">Tus Conversaciones</h3>
          
          <div v-if="conversaciones.length === 0" class="empty-history">
            No hay historial reciente
          </div>

          <div 
            v-for="chat in conversaciones" 
            :key="chat.id" 
            class="history-item"
            :class="{ 'active': chatActualId === chat.id }"
            @click="cargarChat(chat.id)"
          >
            <svg class="chat-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            <span class="chat-title">{{ chat.titulo }}</span>
            
            <div class="chat-actions">
              <button @click.stop="eliminarChat(chat.id)" class="action-icon" title="Eliminar">🗑️</button>
            </div>
          </div>
        </div>
      </div>

      <div class="sidebar-footer">
        <button @click="irAInicio" class="nav-item">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
          <span>Salir al Inicio</span>
        </button>
      </div>
    </aside>

    <main class="main-content">
      
      <header class="top-bar">
        <button class="menu-toggle" @click="isSidebarOpen = !isSidebarOpen">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
        </button>
        <div class="model-selector">
          <span class="model-name">Asistente Empático <span class="status-pill" :class="statusClass">{{ micStatus }}</span></span>
        </div>
      </header>

      <div class="chat-scroll-container" ref="chatArea">
        <div class="chat-inner">
          
          <div v-if="mensajes.length === 0" class="empty-state">
            <div class="logo-circle">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
            </div>
            <h2>¿Cómo te sientes hoy?</h2>
            <p>Estoy aquí para escucharte. Tu voz cambiará el ambiente.</p>
            
            <div class="suggestions-grid">
              <button @click="pedirChisteAutomatico" class="suggestion-card">
                <span class="emoji">🎭</span>
                <span>Cuéntame un chiste</span>
              </button>
              <button @click="procesarMensaje('Me siento estresado')" class="suggestion-card">
                <span class="emoji">🧘</span>
                <span>Me siento estresado</span>
              </button>
              <button @click="procesarMensaje('Necesito un consejo')" class="suggestion-card">
                <span class="emoji">💡</span>
                <span>Dame un consejo</span>
              </button>
            </div>
          </div>

          <div v-else class="messages-feed">
            <div 
              v-for="(msg, index) in mensajes" 
              :key="index" 
              class="message-row"
              :class="msg.remitente === 'usuario' ? 'row-user' : 'row-ai'"
            >
              <div class="avatar" v-if="msg.remitente !== 'usuario'">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 14a1 1 0 1 1 1-1 1 1 0 0 1-1 1zm1-4.29a1 1 0 0 1 0 1.41V15a1 1 0 0 1-2 0v-2a1 1 0 0 1 1-1 1 1 0 0 1 1-1 1 1 0 0 0 0-2 1 1 0 0 0-1 1"/></svg>
              </div>

              <div class="message-content">
                <div class="bubble" :class="msg.remitente === 'usuario' ? 'bubble-user' : 'bubble-ai'">
                    {{ msg.texto }}
                </div>
              </div>
            </div>

            <div v-if="cargando" class="message-row row-ai">
              <div class="avatar"><span class="pulse-dot"></span></div>
              <div class="message-content">
                 <div class="bubble bubble-ai loading">
                    <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
                 </div>
              </div>
            </div>
          </div>
        
        </div>
      </div>

      <div class="input-region">
        <div class="floating-actions" v-if="esModoHumor">
           <button @click="pedirChisteAutomatico" class="chip-btn">
             ✨ Otro chiste
           </button>
        </div>

        <div class="input-box-wrapper">
          <div class="input-box">
             <button class="input-icon mic" @click="toggleMic" :class="{ 'active': isMicOn }">
                <svg v-if="!isMicOn" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
                <div v-else class="mic-wave-container">
                    <div class="bar"></div>
                    <div class="bar"></div>
                    <div class="bar"></div>
                </div>
             </button>
             
             <input 
                v-model="mensajeInput" 
                @keyup.enter="enviarMensajeManual" 
                type="text" 
                placeholder="Escribe un mensaje..." 
             />

             <button class="input-icon send" @click="enviarMensajeManual" :disabled="!mensajeInput.trim()">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
             </button>
          </div>
          <div class="disclaimer">El asistente es una IA de apoyo, no sustituye a un profesional médico</div>
        </div>
      </div>

    </main>
  </div>
</template>

<script>
export default {
  data() {
    return {
      conversaciones: [],
      mensajes: [],
      chatActualId: null,
      mensajeInput: '',
      micStatus: 'Listo',
      isMicOn: false,
      isSpeaking: false,
      cargando: false,
      isSidebarOpen: true,
      esModoHumor: false,
      
      activeColor: '#3b82f6', 
      
      audioContext: null,
      analyser: null,
      dataArray: null,
      animationId: null,
      canvasCtx: null,
      canvas: null,
      reconocimiento: null,
    };
  },
  computed: {
    statusClass() {
      if (this.isMicOn) return 'status-recording';
      if (this.cargando) return 'status-loading';
      return 'status-ready';
    }
  },
  mounted() {
    this.cargarConversaciones();
    this.initCanvas();
    if(window.innerWidth < 1024) this.isSidebarOpen = false;
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resizeCanvas);
    this.stopVisualizer();
    if (this.reconocimiento) this.reconocimiento.abort();
  },
  methods: {
    irAInicio() {
      window.location.href = '/';
    },

    // --- API ---
    async cargarConversaciones() {
        try {
            const res = await fetch('http://localhost:8000/api/conversaciones/');
            if (res.ok) this.conversaciones = await res.json();
        } catch (e) { console.error(e); }
    },
    async cargarChat(id) {
        this.cargando = true;
        this.chatActualId = id;
        this.mensajes = [];
        this.esModoHumor = false;
        try {
            const res = await fetch(`http://localhost:8000/api/conversaciones/${id}/`);
            if (res.ok) {
                const data = await res.json();
                this.mensajes = data.mensajes;
                this.scrollToBottom();
                if (this.mensajes.length > 0) {
                     const ultimos = this.mensajes.slice(-3);
                     const kw = ['chiste', 'broma', 'reír', 'ánimo', 'gracioso', 'divertido', 'risa'];
                     this.esModoHumor = ultimos.some(m => kw.some(k => m.texto.toLowerCase().includes(k)));
                }
                if (window.innerWidth < 800) this.isSidebarOpen = false;
            }
        } catch (e) { console.error(e); }
        this.cargando = false;
    },
    async eliminarChat(id) {
        if(!confirm("¿Eliminar este chat?")) return;
        try {
            const res = await fetch(`http://localhost:8000/api/conversaciones/${id}/`, { method: 'DELETE' });
            if (res.ok) {
                if (this.chatActualId === id) this.nuevoChat();
                this.cargarConversaciones();
            }
        } catch(e) { console.error(e); }
    },
    nuevoChat() {
        this.chatActualId = null;
        this.mensajes = [];
        this.mensajeInput = '';
        this.activeColor = '#3b82f6'; // Reset color
        this.esModoHumor = false;
        if (window.innerWidth < 800) this.isSidebarOpen = false;
    },

    // --- MENSAJES ---
    async procesarMensaje(texto) {
        if (!texto.trim()) return;
        
        const t = texto.toLowerCase();
        if (t.includes('chiste') || t.includes('broma') || t.includes('reír') || t.includes('ánimo')) {
            this.esModoHumor = true;
        }

        this.mensajes.push({ remitente: 'usuario', texto: texto });
        this.scrollToBottom();
        this.detectarColorEnVoz(texto);
        
        this.cargando = true;
        this.micStatus = 'Pensando...';

        try {
            const payload = { mensaje: texto };
            if (this.chatActualId) payload.chat_id = this.chatActualId;

            const res = await fetch('http://localhost:8000/api/assistant/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                const data = await res.json();
                if (data.chat_id && !this.chatActualId) {
                    this.chatActualId = data.chat_id;
                    this.cargarConversaciones(); 
                }
                this.mensajes.push({ remitente: 'ia', texto: data.response });
                this.hablar(data.response);
                this.scrollToBottom();
                this.micStatus = 'Listo';
            }
        } catch (e) {
            this.mensajes.push({ remitente: 'ia', texto: "Error de conexión." });
        } finally {
            this.cargando = false;
        }
    },
    enviarMensajeManual() {
        this.procesarMensaje(this.mensajeInput);
        this.mensajeInput = '';
    },
    pedirChisteAutomatico() {
        this.esModoHumor = true;
        const chistes = ["Cuéntame un chiste corto.", "Algo gracioso.", "Sorpréndeme.", "Chiste de papá."];
        this.procesarMensaje(chistes[Math.floor(Math.random() * chistes.length)]);
    },
    scrollToBottom() {
        this.$nextTick(() => {
            if (this.$refs.chatArea) {
                const container = this.$refs.chatArea;
                container.scrollTop = container.scrollHeight;
            }
        });
    },

    // --- DETECCIÓN DE COLOR VIBRANTE
    detectarColorEnVoz(texto) {
      const t = texto.toLowerCase()
      if (t.includes('rojo') || t.includes('rabia') || t.includes('enojado') || t.includes('furia')) {
        this.activeColor = '#ef4444'; // Rojo brillante
      } else if (t.includes('azul') || t.includes('triste') || t.includes('soledad') || t.includes('pena')) {
        this.activeColor = '#3b82f6'; // Azul eléctrico
      } else if (t.includes('verde') || t.includes('calma') || t.includes('esperanza') || t.includes('paz')) {
        this.activeColor = '#22c55e'; // Verde neón
      } else if (t.includes('feliz') || t.includes('bien') || t.includes('naranja') || t.includes('alegre')) {
        this.activeColor = '#f97316'; // Naranja vivo
      } else if (t.includes('morado') || t.includes('miedo') || t.includes('ansiedad')) {
        this.activeColor = '#a855f7'; // Violeta brillante
      } else if (t.includes('normal') || t.includes('inicio') || t.includes('neutro')) {
        this.activeColor = '#3b82f6'; // Reset a azul default
      }
    },

    initCanvas() {
        this.canvas = this.$refs.canvas;
        if(this.canvas) {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
            this.canvasCtx = this.canvas.getContext('2d');
            this.drawIdle();
        }
    },
    resizeCanvas() {
        if(this.canvas) {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        }
    },
    async initVisualizer() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioContext();
            const src = this.audioContext.createMediaStreamSource(stream);
            this.analyser = this.audioContext.createAnalyser();
            src.connect(this.analyser);
            this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
            this.drawVisualizer();
        } catch(e) { console.log(e); }
    },
    drawVisualizer() {
        if(!this.isMicOn) return;
        requestAnimationFrame(this.drawVisualizer);
        this.analyser.getByteFrequencyData(this.dataArray);
        const w = this.canvas.width; const h = this.canvas.height;
        this.canvasCtx.clearRect(0,0,w,h);
        
        const r = 100 + (this.dataArray[10] || 0);
        this.canvasCtx.beginPath();
        this.canvasCtx.arc(w/2, h/2, r, 0, Math.PI*2);
        this.canvasCtx.strokeStyle = this.activeColor; 
        this.canvasCtx.lineWidth = 4;
        this.canvasCtx.globalAlpha = 0.8;
        this.canvasCtx.stroke();
    },
    drawIdle() {
        if(this.isMicOn || !this.canvasCtx) return;
        this.canvasCtx.clearRect(0,0,this.canvas.width, this.canvas.height);
    },
    stopVisualizer() {
        if(this.audioContext) this.audioContext.close();
    },

    // --- MICRÓFONO ---
    iniciarVoz() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return alert("Navegador no soportado");
        if (this.reconocimiento) this.reconocimiento.abort();
        
        this.reconocimiento = new SpeechRecognition();
        this.reconocimiento.lang = 'es-ES';
        this.reconocimiento.continuous = true; 
        this.reconocimiento.interimResults = false;

        this.reconocimiento.onstart = () => {
            this.isMicOn = true;
            this.micStatus = "Escuchando...";
            this.initVisualizer();
        };
        this.reconocimiento.onresult = (event) => {
            const t = event.results[event.resultIndex][0].transcript;
            this.procesarMensaje(t);
        };
        this.reconocimiento.onend = () => {
            if (this.isMicOn) { try { this.reconocimiento.start(); } catch(e){} }
            else { this.stopVisualizer(); this.micStatus = "Listo"; }
        };
        this.reconocimiento.start();
        this.isMicOn = true;
    },
    toggleMic() {
        if (this.isMicOn) {
            this.isMicOn = false;
            if(this.reconocimiento) this.reconocimiento.stop();
        } else {
            this.iniciarVoz();
        }
    },
    hablar(texto) {
        if ("speechSynthesis" in window) {
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(texto);
            u.lang = 'es-ES';
            window.speechSynthesis.speak(u);
        }
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* --- LAYOUT GLOBAL & FONDO AURORA --- */
.app-layout {
  display: flex; width: 100vw; height: 100vh; 
  background-color: #111827; 
  color: #e3e3e3; font-family: 'Plus Jakarta Sans', sans-serif; overflow: hidden;
  position: relative;
}

/* El fondo animado vive aquí */
.aurora-bg {
  position: absolute; inset: 0; pointer-events: none; z-index: 0;
  background: #111827; /* Base oscura */
  overflow: hidden;
}

.aurora-blob {
  position: absolute; border-radius: 50%;
  filter: blur(80px); opacity: 0.6; /* Aumenté opacidad para que se note más */
  background: var(--active-color); /* Color dinámico desde Vue */
  transition: background-color 1s ease;
  animation: float 10s infinite alternate cubic-bezier(0.4, 0, 0.2, 1);
}

.blob-1 { width: 60vw; height: 60vw; top: -10%; left: -10%; animation-delay: 0s; }
.blob-2 { width: 50vw; height: 50vw; bottom: -10%; right: -10%; animation-delay: -2s; opacity: 0.4; }
.blob-3 { width: 40vw; height: 40vw; top: 40%; left: 40%; transform: translate(-50%, -50%); animation-delay: -4s; opacity: 0.3; }

.visualizer-canvas { position: absolute; top:0; left:0; width:100%; height:100%; pointer-events: none; z-index: 1; }
.noise-overlay {
  position: absolute; inset: 0; pointer-events: none; z-index: 2; opacity: 0.04;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}

/* --- SIDEBAR --- */
.sidebar {
  width: 280px; background: rgba(17, 24, 39, 0.9); backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255,255,255,0.08);
  display: flex; flex-direction: column;
  transition: transform 0.3s ease; flex-shrink: 0; z-index: 20;
}
.sidebar.sidebar-closed { margin-left: -280px; }

.sidebar-top { padding: 20px 15px; }
.new-chat-btn {
  width: 100%; padding: 12px 15px; background: #2563eb; border: none; border-radius: 10px;
  color: white; cursor: pointer; display: flex; align-items: center; gap: 10px; font-size: 0.95rem; font-weight: 600;
  transition: 0.2s; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
}
.new-chat-btn:hover { background: #1d4ed8; transform: translateY(-1px); }

.sidebar-content { flex: 1; overflow-y: auto; padding: 0 10px; }
.history-label { font-size: 0.8rem; font-weight: 600; color: #9ca3af; margin: 15px 10px 8px; text-transform: uppercase; letter-spacing: 0.05em; }
.empty-history { font-size: 0.9rem; color: #6b7280; padding: 20px; text-align: center; }

.history-item {
  display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 8px;
  cursor: pointer; color: #d1d5db; font-size: 0.95rem; transition: 0.2s;
  white-space: nowrap; overflow: hidden; position: relative;
}
.history-item:hover, .history-item.active { background: rgba(255,255,255,0.08); color: white; }
.chat-title { overflow: hidden; text-overflow: ellipsis; max-width: 150px; }
.chat-actions { margin-left: auto; opacity: 0; transition: opacity 0.2s; }
.history-item:hover .chat-actions { opacity: 1; }
.action-icon { background: none; border: none; cursor: pointer; font-size: 1rem; color: #9ca3af; padding: 4px; }
.action-icon:hover { color: #ef4444; }

.sidebar-footer { padding: 15px; border-top: 1px solid rgba(255,255,255,0.08); }
.nav-item {
  display: flex; align-items: center; gap: 12px; background: none; border: none;
  color: #9ca3af; cursor: pointer; font-size: 0.95rem; padding: 10px; width: 100%; text-align: left;
  border-radius: 8px; transition: 0.2s; font-weight: 500;
}
.nav-item:hover { background: rgba(255,255,255,0.05); color: #e5e7eb; }

/* --- MAIN CONTENT --- */
.main-content {
  flex: 1; display: flex; flex-direction: column; position: relative; z-index: 10;
  background: transparent;
}

.top-bar {
  display: flex; align-items: center; justify-content: space-between; padding: 12px 24px;
}
.menu-toggle { background: none; border: none; color: #e5e7eb; cursor: pointer; padding: 4px; border-radius: 4px; }
.menu-toggle:hover { background: rgba(255,255,255,0.1); }
.model-selector { display: flex; align-items: center; gap: 8px; }
.model-name { font-size: 1rem; font-weight: 600; color: #f3f4f6; }
.status-pill { font-size: 0.75rem; padding: 2px 8px; border-radius: 10px; font-weight: 600; text-transform: uppercase; }
.status-ready { background: rgba(31, 41, 55, 0.8); color: #9ca3af; }
.status-recording { background: #ef4444; color: white; animation: pulse-status 1.5s infinite; }
.status-loading { background: #fbbf24; color: #1f2937; }

/* --- CHAT AREA --- */
.chat-scroll-container {
  flex: 1; overflow-y: auto; display: flex; flex-direction: column; align-items: center;
  scroll-behavior: smooth;
}
/* AUMENTÉ EL PADDING-BOTTOM AQUÍ A 180px PARA EVITAR QUE EL CHAT SE CUBRA */
.chat-inner { width: 100%; max-width: 850px; padding: 20px 40px 180px; display: flex; flex-direction: column; gap: 30px; }

.empty-state { text-align: center; margin-top: 15vh; color: #9ca3af; animation: fadeIn 0.5s ease-out; }
.logo-circle { width: 72px; height: 72px; background: rgba(255,255,255,0.05); border-radius: 50%; margin: 0 auto 24px; display: flex; align-items: center; justify-content: center; }
.empty-state h2 { font-size: 1.8rem; font-weight: 600; color: #f3f4f6; margin-bottom: 8px; }
.empty-state p { font-size: 1.1rem; margin-bottom: 32px; }

.suggestions-grid { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
.suggestion-card {
  background: rgba(31, 41, 55, 0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 16px 20px;
  color: #e5e7eb; cursor: pointer; width: 200px; text-align: left; display: flex; flex-direction: column; gap: 12px; transition: 0.2s;
}
.suggestion-card:hover { background: rgba(55, 65, 81, 0.9); transform: translateY(-2px); border-color: rgba(255,255,255,0.2); }
.suggestion-card .icon { font-size: 1.5rem; align-self: flex-end; }

/* MENSAJES */
.messages-feed { display: flex; flex-direction: column; gap: 30px; } 

.message-row { display: flex; gap: 16px; width: 100%; animation: slideUp 0.3s ease-out; }
.row-user { justify-content: flex-end; }
.row-ai { justify-content: flex-start; }

.avatar { 
  width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  background: #111827; flex-shrink: 0; color: #9ca3af; font-weight: bold; font-size: 0.8rem; border: 1px solid rgba(255,255,255,0.1);
}
.row-user .avatar { display: none; }

.message-content { display: flex; flex-direction: column; gap: 4px; max-width: 75%; }
.sender-name { font-size: 0.85rem; font-weight: 600; color: #c4c7c5; margin-left: 10px; }
.row-user .sender-name { display: none; }

.bubble {
  font-size: 1.15rem; line-height: 1.6; color: #f3f4f6; white-space: pre-wrap;
  padding: 14px 22px; border-radius: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  width: fit-content; 
}
.bubble-user { 
  background: #2563eb; color: white; 
  border-bottom-right-radius: 4px; margin-left: auto;
}
.bubble-ai { 
  background: #374151; color: #f3f4f6; 
  border-bottom-left-radius: 4px; border: 1px solid rgba(255,255,255,0.05); margin-right: auto;
}

.pulse-dot { width: 10px; height: 10px; background: #60a5fa; border-radius: 50%; animation: pulse-status 1s infinite; }
.dot { display: inline-block; animation: bounce 1.4s infinite; margin: 0 2px; color: #9ca3af; }
.bubble.loading { padding: 15px 25px; background: rgba(55, 65, 81, 0.5); }

/* INPUT AREA */
.input-region {
  width: 100%; display: flex; flex-direction: column; align-items: center; padding: 0 20px 24px;
  /* Gradiente reducido para no tapar tanto */
  background: linear-gradient(to top, #111827 60%, transparent);
  position: absolute; bottom: 0; left: 0; z-index: 20;
}
.floating-actions { margin-bottom: 12px; }
.chip-btn {
  background: #1f2937; border: 1px solid #374151; color: #a8c7fa; padding: 8px 16px;
  border-radius: 20px; cursor: pointer; font-size: 0.9rem; transition: 0.2s; font-weight: 500;
  display: flex; align-items: center; gap: 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}
.chip-btn:hover { background: #374151; transform: translateY(-1px); }

.input-box-wrapper { width: 100%; max-width: 850px; position: relative; }
.input-box {
  background: #1f2937; border-radius: 28px; display: flex; align-items: center; padding: 8px;
  border: 1px solid #374151; transition: border-color 0.2s, box-shadow 0.2s;
}
.input-box:focus-within { border-color: #4b5563; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2); }

.input-icon {
  width: 44px; height: 44px; border-radius: 50%; border: none; background: transparent;
  color: #9ca3af; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: 0.2s; flex-shrink: 0;
}
.input-icon:hover { background: rgba(255,255,255,0.05); color: #e5e7eb; }
.input-icon.mic.active { background: #ef4444; color: white; box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); }

.mic-wave-container { display: flex; align-items: center; gap: 3px; height: 16px; }
.bar { width: 3px; background: white; border-radius: 2px; animation: wave 0.8s infinite ease-in-out; }
.bar:nth-child(1) { height: 10px; animation-delay: 0s; }
.bar:nth-child(2) { height: 16px; animation-delay: 0.1s; }
.bar:nth-child(3) { height: 12px; animation-delay: 0.2s; }

input {
  flex: 1; background: transparent; border: none; color: #f3f4f6; font-size: 1.05rem; padding: 0 12px; outline: none;
}
.send-btn { background: none; border: none; color: #3b82f6; cursor: pointer; padding: 10px; }
.send-btn:disabled { color: #4b5563; cursor: default; }

.disclaimer { font-size: 0.75rem; color: #6b7280; text-align: center; margin-top: 10px; }

/* Animaciones */
.fade-chat-enter-active, .fade-chat-leave-active { transition: opacity 0.2s ease; }
.fade-chat-enter-from, .fade-chat-leave-to { opacity: 0; }
@keyframes pulse-status { 0% { opacity: 0.8; transform: scale(0.95); } 50% { opacity: 1; transform: scale(1.05); } 100% { opacity: 0.8; transform: scale(0.95); } }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes wave { 0%, 100% { transform: scaleY(1); } 50% { transform: scaleY(1.5); } }
@keyframes float { 0% { transform: translate(0,0); } 100% { transform: translate(20px, 20px); } }

@media(max-width: 768px) {
  .sidebar { position: absolute; height: 100%; width: 85%; box-shadow: 10px 0 30px rgba(0,0,0,0.5); }
  .chat-inner { padding: 20px 15px 100px; }
  .message-content { max-width: 85%; }
  .suggestions-grid { flex-direction: column; align-items: center; }
  .suggestion-card { width: 100%; max-width: 300px; }
}
</style>