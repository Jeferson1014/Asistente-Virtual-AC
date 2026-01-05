from rest_framework import serializers
from .models import Usuario, Tarea, Conversacion, Mensaje

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = '__all__'
class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ['id', 'remitente', 'texto', 'fecha']

class ConversacionSerializer(serializers.ModelSerializer):
    # Incluimos los mensajes anidados para cargar todo el chat de una vez
    # O podemos hacerlo ligero solo con el título si son muchos
    class Meta:
        model = Conversacion
        fields = ['id', 'titulo', 'fecha_creacion']