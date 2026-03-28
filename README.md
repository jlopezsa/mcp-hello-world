# 🧑‍🔬 Aplicacion Multi-Server MCP Client

![motion architecture](./images/model_mcp_client.drawio.svg)

Este proyecto reproduce el laboratorio **Build an MCP Application** del curso [Build AI Agents using MCP (IBM-Coursera)](https://www.coursera.org/learn/build-ai-agents-using-mcp)  con el objetivo de desarrollar habilidades en la implementación de agentes y clientes MCP, tanto locales como remotos.

Este proyecto muestra un ejemplo sencillo de un cliente MCP construido en Python. El programa conecta dos servidores MCP, obtiene sus herramientas, las combina en un solo agente y permite conversar con ese agente desde consola.

## ✨ Descripción

El archivo `mcp_hello_world/main.py` implementa un cliente MCP que conecta varios servidores, reúne sus herramientas en un solo agente conversacional y permite interactuar con él desde consola usando un modelo de lenguaje con memoria de conversación.

1. Carga variables de entorno con `python-dotenv`.
2. Define la configuracion de dos servidores MCP:
   `context7`: expone herramientas para consultar documentacion tecnica.
   `met-museum`: expone herramientas para consultar informacion de la coleccion del Metropolitan Museum.
3. Crea clientes `MultiServerMCPClient` para cada servidor y otro cliente combinado.
4. Construye un modelo de lenguaje con `ChatOpenAI` usando los valores de entorno.
5. Descubre las herramientas disponibles en cada servidor con `get_tools()`.
6. Crea un agente ReAct con `create_react_agent(...)`.
7. Agrega memoria en proceso con `InMemorySaver` para conservar el historial de conversacion dentro del mismo hilo.
8. Ejecuta una primera consulta de bienvenida y luego abre un menu interactivo en consola para seguir preguntando.

## 📂 Estructura

### 1. Carga de configuracion

El programa lee estas variables desde `.env`:

- `OPENAI_API_KEY`: clave del proveedor compatible con OpenAI.
- `ORCHESTATOR_BASE_URL`: URL base del endpoint del modelo.
- `ORCHESTATOR_MODEL`: nombre del modelo que se va a usar.

En `.env.example` ya existe una referencia basica:

```env
OPENAI_API_KEY=
ORCHESTATOR_MODEL=openai/gpt-4.1-nano
ORCHESTATOR_BASE_URL=https://openrouter.ai/api/v1
```

### 2. Servidores MCP usados

El ejemplo integra dos tipos de transporte MCP:

- `Context7` usando `streamable_http`, ideal para conectarse a un servidor remoto por URL.
- `Met Museum` usando `stdio`, arrancando el servidor con `npx`.

Esto es util porque demuestra que un mismo agente puede trabajar con herramientas expuestas por servidores distintos, incluso si usan mecanismos de transporte diferentes.

### 3. Agente con herramientas

El agente se crea con el patron ReAct, lo que significa que puede:

- razonar sobre la pregunta del usuario,
- decidir si necesita usar una herramienta,
- invocar la herramienta adecuada,
- responder con el resultado.

Las herramientas disponibles salen de la combinacion de ambos servidores MCP, por eso el agente puede responder preguntas relacionadas tanto con documentacion tecnica como con la coleccion del museo.

### 4. Memoria de conversacion

`InMemorySaver` guarda el historial de mensajes usando el `thread_id` configurado en:

```python
config = {"configurable": {"thread_id": "conversation_id"}}
```

Eso permite que, dentro de la misma ejecucion, el agente recuerde el contexto de preguntas anteriores.

## 🚀 Flujo de ejecucion

Cuando se ejecuta el programa ocurre lo siguiente:

1. Se inicializa la funcion principal asincrona.
2. Se crean los clientes MCP.
3. Se consultan e imprimen las herramientas encontradas.
4. Se crea el agente con modelo, herramientas y memoria.
5. Se envia un mensaje inicial para que el agente se presente.
6. Se muestra un menu interactivo:
   `1` para hacer preguntas.
   `2` para salir.

## Como ejecutar el proyecto

### 1. Instalar dependencias

```bash
poetry install
```

### 2. Configurar variables de entorno

Crea tu archivo `.env` a partir de `.env.example` y completa los valores necesarios.

### 3. Ejecutar el cliente

```bash
poetry run mcp-hello-world
```

## Valor didactico del ejemplo

Este ejemplo sirve para entender rapidamente:

- como conectar multiples servidores MCP desde Python,
- como unificar herramientas de distintos origenes,
- como integrar un modelo de lenguaje con LangChain,
- como crear un agente conversacional con memoria,
- como construir una interfaz minima de linea de comandos para probar herramientas MCP.

## Posibles mejoras

Si quieres evolucionar este ejemplo, algunos siguientes pasos naturales serian:

- manejar errores cuando falten variables de entorno,
- validar que `npx` este instalado antes de iniciar el servidor `met-museum`,
- permitir cambiar el `thread_id` por sesion,
- agregar logs mas claros para diagnostico,
- incluir pruebas para la inicializacion del cliente y del agente.
