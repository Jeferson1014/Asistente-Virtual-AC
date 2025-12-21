<template>
  <div class="asistente-container">
    <h2>Asistente de Ayuda Psicológica</h2>

    <button @click="toggleMic" :style="btnMicStyle">
      {{ isMicOn ? 'Apagar Micrófono' : 'Activar Micrófono' }}
    </button>

    <p :style="micStatusStyle">{{ micStatus }}</p>

    <div v-if="mensajeCapturado" class="message-box">
      <h3>Tu mensaje:</h3>
      <p class="user-text">{{ mensajeCapturado }}</p>
    </div>

    <button @click="enviarMensaje" :disabled="!mensajeCapturado || cargando" class="btn-enviar">
      {{ cargando ? 'Pensando...' : 'Enviar al Asistente' }}
    </button>

    <div v-if="respuesta" class="response-container">
      <h3>Respuesta del Asistente:</h3>
      <div class="response-box">
        <p>{{ respuesta }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      mensajeCapturado: '', // Mensaje que el usuario dice
      respuesta: '',        // Respuesta del asistente
      reconocimiento: null, // Instancia de reconocimiento de voz
      micStatus: 'Micrófono apagado', 
      isMicOn: false, 
      isSpeaking: false, 
      cargando: false,
    };
  },
  computed: {
    micStatusStyle() {
      return {
        color: this.isMicOn ? '#ff7043' : '#ccc',
        fontWeight: 'bold',
        marginTop: '10px'
      };
    },
    btnMicStyle() {
      return {
        backgroundColor: this.isMicOn ? '#d32f2f' : '#007bff'
      }
    }
  },
  methods: {
    // Iniciar el reconocimiento de voz
    iniciarVoz() {
      if (!('webkitSpeechRecognition' in window)) {
        alert('Tu navegador no soporta reconocimiento de voz. Usa Chrome.');
        return;
      }
      
      // Si ya existe, lo reiniciamos
      if (this.reconocimiento) {
        this.reconocimiento.stop();
      }

      this.reconocimiento = new webkitSpeechRecognition();
      this.reconocimiento.continuous = false; // False para que corte al terminar de hablar una frase
      this.reconocimiento.lang = 'es-ES';
      this.reconocimiento.interimResults = false;

      this.reconocimiento.onstart = () => {
        this.micStatus = 'Escuchando... ¡Habla ahora!';
      };

      this.reconocimiento.onresult = (event) => {
        const texto = event.results[0][0].transcript;
        this.mensajeCapturado = texto; 
        console.log("Texto detectado:", texto);
      };

      this.reconocimiento.onerror = (event) => {
        console.error('Error de reconocimiento: ', event.error);
        this.detenerVoz();
      };

      this.reconocimiento.onend = () => {
        this.isMicOn = false;
        this.micStatus = 'Micrófono apagado (Fin de la frase)';
      };

      this.reconocimiento.start();
      this.isMicOn = true;
    },

    // Detener reconocimiento de voz manual
    detenerVoz() {
      if (this.reconocimiento) {
        this.reconocimiento.stop();
        this.isMicOn = false;
        this.micStatus = 'Micrófono apagado';
      }
    },

    toggleMic() {
      if (this.isMicOn) {
        this.detenerVoz();
      } else {
        this.iniciarVoz();
      }
    },

    // Enviar mensaje al backend
    async enviarMensaje() {
      if (!this.mensajeCapturado.trim()) return;

      this.cargando = true;
      this.respuesta = ''; // Limpiar respuesta anterior

      try {
        // NOTA: Asegúrate de que el puerto 8000 sea el correcto
        const res = await axios.post('http://localhost:8000/api/assistant/', {
          mensaje: this.mensajeCapturado, // Enviamos 'mensaje' (Correcto)
        });

        console.log("Respuesta Backend:", res.data);

        // --- CORRECCIÓN CLAVE AQUÍ ---
        // Tu backend devuelve { response: "...", status: "success" }
        // Si usas la otra vista, podría ser { message: "..." }
        // Usamos || para que funcione con ambos casos.
        this.respuesta = res.data.response || res.data.message; 
        
        // Hablar la respuesta
        this.hablar(this.respuesta);

      } catch (error) {
        console.error('Error axios:', error);
        this.respuesta = 'Ocurrió un error al conectar con el servidor.';
        if (error.response && error.response.data) {
           console.log("Detalle error:", error.response.data);
        }
      } finally {
        this.cargando = false;
      }
    },

    // Síntesis de voz
    hablar(texto) {
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel(); // Cancelar habla anterior
        
        const utterance = new SpeechSynthesisUtterance(texto);
        utterance.lang = "es-ES";
        utterance.rate = 1.0; // Velocidad normal
        
        utterance.onend = () => {
          this.isSpeaking = false;
        };
        
        this.isSpeaking = true;
        window.speechSynthesis.speak(utterance);
      } else {
        alert("Tu navegador no soporta síntesis de voz.");
      }
    }
  }
};
</script>

<style scoped>
.asistente-container {
  padding: 20px;
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}

button {
  padding: 12px 24px;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  margin: 10px;
  transition: transform 0.2s;
}

button:hover {
  transform: scale(1.05);
  opacity: 0.9;
}

button:disabled {
  background-color: #cccccc !important;
  cursor: not-allowed;
  transform: none;
}

.btn-enviar {
  background-color: #28a745; /* Verde */
}

.message-box {
  background: rgba(255, 255, 255, 0.2);
  padding: 15px;
  border-radius: 10px;
  margin: 20px 0;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.user-text {
  font-style: italic;
  font-size: 1.1em;
  color: #333; /* Color oscuro para legibilidad */
}

.response-box {
  background-color: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  margin-top: 10px;
}

.response-box p {
  color: #2c3e50;
  font-size: 1.1em;
  line-height: 1.5;
}

h3 {
  color: #555;
}
</style>