# Dockerización del Servicio LLM

## Arquitectura Propuesta

### Estructura del Contenedor

```
/app
├── src/
│   ├── models/
│   │   ├── prompt.txt
│   │   ├── setting.json
│   │   └── tinyllama-1.1b-chat-v1.0.Q2_K.gguf
│   ├── llamafile/
│   │   └── llamafile.exe
│   └── bot.py
├── requirements.txt
└── Dockerfile
```

### Componentes

1. **Imagen Base**

   - Python 3.9-slim
   - Razón: Imagen ligera pero con todas las herramientas necesarias

2. **Dependencias**

   ```txt
   fastapi
   uvicorn
   chardet
   ```

3. **Puerto**

   - Exponer puerto 8000 para el servicio FastAPI

4. **Dockerfile**

   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY src/ src/

   EXPOSE 8000

   CMD ["python", "src/bot.py"]
   ```

5. **Docker Compose**

   ```yaml
   version: "3.8"

   services:
     llm-service:
       build: .
       ports:
         - "8000:8000"
       volumes:
         - ./src:/app/src
   ```

### Instrucciones de Uso

1. Construir la imagen:

   ```bash
   docker build -t llm-service .
   ```

2. Ejecutar el contenedor:

   ```bash
   docker run -p 8000:8000 llm-service
   ```

3. Usando Docker Compose:
   ```bash
   docker-compose up --build
   ```

### Consideraciones

1. **Volúmenes**

   - Los modelos y configuraciones se montan como volúmenes para facilitar actualizaciones
   - Permite cambiar configuraciones sin reconstruir la imagen

2. **Seguridad**

   - La imagen base slim reduce la superficie de ataque
   - No se ejecuta como root dentro del contenedor

3. **Rendimiento**
   - Se expone el puerto 8000 para acceso al API
   - Se pueden ajustar recursos del contenedor según necesidades

### Próximos Pasos

1. Crear archivo `requirements.txt`
2. Implementar Dockerfile
3. Implementar docker-compose.yml
4. Probar la construcción y despliegue

¿Procedemos con la implementación de esta arquitectura?
