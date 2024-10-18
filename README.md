Claro, a continuación te presento una versión actualizada del archivo `README.md` para tu proyecto `bot-llm`. Esta versión refleja los cambios realizados, utilizando la clase `PromptCompressor` en lugar de `Optimizer`, y actualiza los endpoints y las instrucciones correspondientes.

---

# Bot LLMLingua

## Descripción

**Bot LLMLingua** es una aplicación desarrollada en Python que ofrece una API para comprimir prompts utilizando la librería [LLMLingua](https://github.com/microsoft/LLMLingua) de Microsoft. Esta herramienta está diseñada para optimizar textos antes de enviarlos a modelos de lenguaje grandes, reduciendo el número de tokens y, por ende, los costos asociados a la inferencia.

## Índice

- [Instalación](#instalación)
- [Uso](#uso)
  - [Ejecutar el Bot](#ejecutar-el-bot)
  - [Probar el Endpoint `/compress`](#probar-el-endpoint-compress)
  - [Documentación de la API](#documentación-de-la-api)
- [Consideraciones](#consideraciones)
  - [Entornos Virtuales](#entornos-virtuales)
  - [Gestión de Dependencias](#gestión-de-dependencias)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

## Instalación

### Prerrequisitos

- **Python 3.7** o superior
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar el repositorio)

### Pasos de Instalación

1. **Clonar el Repositorio**

   Abre una terminal y ejecuta el siguiente comando para clonar el repositorio:

   ```bash
   git clone https://github.com/tu_usuario/bot-llm.git
   cd bot-llm
   ```

2. **Crear un Entorno Virtual (Recomendado)**

   Aunque puedes instalar las dependencias directamente en tu entorno global, se recomienda utilizar un entorno virtual para evitar conflictos de dependencias.

   ```bash
   python -m venv venv
   ```

   **Activar el Entorno Virtual:**

   - **En Windows:**

     ```bash
     venv\Scripts\activate
     ```

   - **En macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

3. **Instalar las Dependencias**

   Una vez activado el entorno virtual, instala las dependencias necesarias utilizando el archivo `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

   **Contenido del archivo `requirements.txt`:**

   ```plaintext
   fastapi
   uvicorn
   llmlingua
   torch
   transformers
   nltk
   tiktoken
   numpy
   rank_bm25
   sentence-transformers
   cohere
   voyageai
   jinaai/jina-embeddings-v2-base-en
   ```

   > **Nota:** Asegúrate de que todas las dependencias están correctamente listadas en el archivo `requirements.txt`. Si utilizas métodos de recuperación específicos (como `voyageai` o `cohere`), verifica que las claves de API necesarias estén configuradas adecuadamente.

4. **Descargar Recursos Adicionales**

   Algunos modelos y recursos utilizados por `llmlingua` pueden requerir descargas adicionales. Asegúrate de seguir las instrucciones específicas en la [documentación oficial de LLMLingua](https://github.com/microsoft/LLMLingua) para configurar correctamente los modelos.

## Uso

### Ejecutar el Bot

Una vez instaladas las dependencias, puedes iniciar el bot ejecutando el siguiente comando desde la raíz del proyecto:

```bash
python src\bot.py
```

Este comando iniciará el servidor FastAPI en `http://0.0.0.0:8000`. Deberías ver una salida similar a la siguiente:

```plaintext
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     LLMLingua PromptCompressor inicializado correctamente.
```

### Probar el Endpoint `/compress`

Puedes interactuar con la API utilizando un navegador web, `curl` o herramientas como **Postman**.

#### Usando el Navegador

Abre tu navegador y accede a la siguiente URL, reemplazando `Tu%20prompt%20aquí` con el texto que deseas comprimir:

```
http://localhost:8000/compress?prompt=Tu%20prompt%20aquí&rate=0.5
```

#### Usando `curl`

Abre una terminal y ejecuta:

```bash
curl "http://localhost:8000/compress?prompt=Tu%20prompt%20aquí&rate=0.5"
```

#### Usando Postman

1. **Abrir Postman.**
2. **Crear una nueva solicitud** de tipo **GET**.
3. **Ingresar la URL:**

   ```
   http://localhost:8000/compress?prompt=Tu%20prompt%20aquí&rate=0.5
   ```

4. **Enviar la solicitud** y verificar la respuesta.

### Respuesta Esperada

Deberías recibir una respuesta JSON similar a la siguiente:

```json
{
  "compressed_prompt": "Tu prompt comprimido aquí"
}
```

### Documentación de la API

FastAPI genera automáticamente documentación interactiva que facilita la prueba y comprensión de tus endpoints.

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

Abre estas URLs en tu navegador para explorar y probar los endpoints de tu API de manera interactiva.

## Consideraciones

### Entornos Virtuales

Aunque has decidido **no utilizar entornos virtuales**, es altamente recomendable considerarlo en proyectos futuros para evitar conflictos de dependencias y mantener tu entorno global limpio. Los entornos virtuales te permiten aislar las dependencias de cada proyecto, facilitando la gestión y evitando conflictos como el que has enfrentado.

#### Cómo Crear y Activar un Entorno Virtual

1. **Crear el Entorno Virtual:**

   ```bash
   python -m venv venv
   ```

2. **Activar el Entorno Virtual:**

   - **En Windows:**

     ```bash
     venv\Scripts\activate
     ```

   - **En macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

3. **Instalar las Dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Desactivar el Entorno Virtual:**

   ```bash
   deactivate
   ```

### Gestión de Dependencias

Para visualizar y gestionar las dependencias de tus paquetes, considera utilizar herramientas como [`pipdeptree`](https://github.com/naiquevin/pipdeptree):

```bash
pip install pipdeptree
pipdeptree
```

Esto te ayudará a identificar y resolver conflictos de dependencias de manera más eficiente.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos para contribuir al proyecto:

1. **Fork** del repositorio.
2. **Crear una rama** para tu feature:

   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

3. **Commit** de tus cambios:

   ```bash
   git commit -m "Añadir nueva funcionalidad"
   ```

4. **Push** a la rama:

   ```bash
   git push origin feature/nueva-funcionalidad
   ```

5. **Crear un Pull Request** en el repositorio original.

### Guía de Contribución

1. **Clonar el Repositorio:**

   ```bash
   git clone https://github.com/wicouy/bot-llm
   cd bot-llm
   ```

2. **Crear una Rama para tu Feature:**

   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

3. **Implementar tus Cambios** y **Commit**:

   ```bash
   git commit -m "Descripción de los cambios realizados"
   ```

4. **Push** a tu Fork:

   ```bash
   git push origin feature/nueva-funcionalidad
   ```

5. **Crear un Pull Request** describiendo tus cambios y por qué deberían ser incorporados al proyecto.

## Licencia

Este proyecto está licenciado bajo la [MIT License](LICENSE).
