# Dockerización del Servicio LLM

## Nota Importante sobre Llamafile

Para el contenedor Docker, necesitamos usar la versión Linux de llamafile. Siga estos pasos:

1. Descargar llamafile para Linux:

```bash
wget https://github.com/Mozilla-Ocho/llamafile/releases/download/1.0.0/llamafile-linux-x86_64
chmod +x llamafile-linux-x86_64
mv llamafile-linux-x86_64 src/llamafile/llamafile
```

2. Asegurarse de tener la estructura correcta:

```
src/
├── llamafile/
│   ├── llamafile      # Versión Linux para Docker
│   └── llamafile.exe  # Versión Windows para desarrollo local
```

## Estructura Actualizada

La aplicación detectará automáticamente qué versión de llamafile usar basado en el sistema operativo.
