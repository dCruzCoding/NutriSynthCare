# 🌐 NutriSynthCare: Aplicación Web Interactiva de Salud y Nutrición 🚀

Este documento detalla la aplicación web desarrollada para NutriSynthCare, que proporciona una interfaz de usuario interactiva para la entrada de datos de pacientes y la visualización de informes personalizados de salud y nutrición. Esta aplicación es el punto de interacción principal para el usuario final con los modelos de IA y el sistema de ontología del proyecto.

## 1. ¿Qué es la Aplicación Web? 🤔

La aplicación web de NutriSynthCare es una interfaz de usuario (UI) construida con **Flask** (un microframework web de Python) y **HTML/CSS** para el frontend. Su propósito es permitir a los usuarios (simulados como profesionales de la salud o individuos) introducir datos de nuevos pacientes y, en tiempo real, obtener un informe detallado que incluye su perfil de riesgo, condiciones de salud detectadas y recomendaciones nutricionales personalizadas, generadas por el backend de IA y ontología.

## 2. Propósito y Funcionalidad Principal ✨

El objetivo central de la aplicación web es democratizar el acceso a las capacidades analíticas y de recomendación de NutriSynthCare, ofreciendo:

* **Entrada de Datos de Pacientes:** 📝 Un formulario web intuitivo para que los usuarios puedan introducir información demográfica y de salud de un nuevo paciente (como edad, sexo, peso, altura, nivel de estrés, etc.).
* **Procesamiento en Tiempo Real:** ⚡️ Al enviar el formulario, la aplicación interactúa con el módulo `core_functions.py` del backend para procesar los datos, calcular métricas (ej. IMC), predecir el perfil del paciente mediante clustering, detectar condiciones de salud y generar recomendaciones nutricionales usando la ontología.
* **Generación y Visualización de Informes Personalizados:** 📊 El resultado del procesamiento se presenta al usuario en un informe HTML estructurado, claro y fácil de entender, que detalla todos los aspectos relevantes para la salud y nutrición del paciente.

## 3. Componentes Clave de la Aplicación Web 🏗️

La estructura de la aplicación web se compone de los siguientes archivos y directorios:

* **`app.py`:**
    * Este es el archivo principal de la aplicación Flask.
    * Configura las rutas URL (endpoints) para la página de inicio (`/`) y para procesar los datos del formulario (`/process_new_patient`).
    * Maneja las solicitudes HTTP (GET para mostrar el formulario, POST para procesar los datos).
    * Renderiza las plantillas HTML para la interfaz de usuario.
    * Es el "puente" entre el frontend y la lógica de negocio contenida en `core_functions.py`.
* **`core_functions.py`:**
    * Contiene toda la lógica de backend compleja:
        * Carga y entrenamiento (o inicialización) de los modelos de IA (Scaler, OneHotEncoder, Autoencoder, K-Means).
        * Cálculo del Índice de Masa Corporal (IMC) a partir de peso y altura.
        * Normalización y codificación de los datos del paciente para los modelos.
        * Asignación del perfil de clustering al paciente.
        * Cálculo del riesgo cardiovascular.
        * Detección de condiciones de salud específicas del paciente.
        * Interacción con la ontología para obtener recomendaciones nutricionales.
        * Generación del contenido HTML del informe final.
    * Este módulo es compartido con otras partes del proyecto y actúa como el cerebro de análisis y recomendación.
* **`templates/` (Carpeta):**
    * Contiene los archivos HTML que definen la interfaz de usuario.
    * **`index.html`:** La página principal que muestra el formulario de entrada de datos para un nuevo paciente.
    * **`report.html`:** La plantilla utilizada para mostrar el informe de salud y nutrición personalizado una vez que los datos del paciente han sido procesados.
* **`static/` (Carpeta - Implícita):**
    * Aunque no se ha especificado explícitamente en el código compartido, una aplicación Flask típica contendría una carpeta `static/` para archivos CSS (para el estilo de la interfaz) y JavaScript (para interactividad adicional, si la hubiera).

## 3.1. Flujo de Interacción 🌊

1.  **Carga de la App:** Cuando se inicia `app.py`, se llama a `initialize_models()` en `core_functions.py` para cargar los datasets, entrenar los modelos de preprocesamiento (Scaler, OneHotEncoder), el Autoencoder y K-Means, y poblar la ontología.
2.  **Formulario:** El usuario accede a la ruta `/` en el navegador, y `app.py` renderiza `index.html`, mostrando el formulario.
3.  **Envío de Datos:** El usuario completa el formulario y lo envía (método POST a `/process_new_patient`).
4.  **Procesamiento:** `app.py` captura los datos del formulario y los pasa a `process_new_patient_data()` en `core_functions.py`. Esta función realiza todas las transformaciones, cálculos de riesgo, predicciones de perfil y consultas a la ontología.
5.  **Generación de Informe:** `process_new_patient_data()` devuelve el contenido HTML del informe y un ID de visualización para el paciente.
6.  **Visualización:** `app.py` recibe el HTML del informe y lo muestra en la página web, o lo renderiza en una plantilla `report.html`.

## 4. Tecnologías Utilizadas 🛠️

* **Frontend:** HTML, CSS (implícito).
* **Backend Web:** **Flask** (Python).
* **Lógica de Negocio/IA:** **Python**, con librerías como:
    * `pandas` y `numpy` para manipulación de datos.
    * `sklearn` (StandardScaler, OneHotEncoder, KMeans) para preprocesamiento y clustering.
    * `tensorflow.keras` para el Autoencoder.
    * `rdflib` para la implementación de la ontología y sus consultas.

## 5. Cómo Ejecutar la Aplicación Localmente 🚀

Para poner en marcha la aplicación web en tu entorno local, sigue estos pasos:

1.  **Clona el Repositorio:** Si aún no lo has hecho, clona el repositorio de NutriSynthCare a tu máquina local.
2.  **Navega al Directorio del Proyecto:** Abre tu terminal o línea de comandos y navega al directorio donde se encuentra `app.py` y `core_functions.py`.
    ```bash
    cd /ruta/a/tu/proyecto/Codigs y BBDD de Alimentacion e IPC
    ```
3.  **Crea y Activa un Entorno Virtual (Recomendado):**
    ```bash
    python -m venv env
    # En Windows:
    .\env\Scripts\activate
    # En macOS/Linux:
    source env/bin/activate
    ```
4.  **Instala las Dependencias:** Asegúrate de tener todas las librerías necesarias instaladas. Si tienes un `requirements.txt`, úsalo:
    ```bash
    pip install -r requirements.txt
    ```
    Si no, instala las principales manualmente:
    ```bash
    pip install flask pandas numpy scikit-learn tensorflow rdflib
    ```
5.  **Ejecuta la Aplicación Flask:**
    ```bash
    flask run
    ```
    O directamente:
    ```bash
    python app.py
    ```
    Si usas `python app.py`, el servidor se iniciará en modo desarrollo.
6.  **Accede a la Aplicación:** Abre tu navegador web y navega a la dirección que te indique la terminal (normalmente `http://127.0.0.1:5000/`).

## 6. Extensibilidad y Mejoras Futuras 📈

La arquitectura modular de la aplicación web facilita futuras expansiones. Algunas ideas para mejoras incluyen:

* **Persistencia de Datos:** Integración con una base de datos (SQL, NoSQL) para almacenar los perfiles de pacientes generados.
* **Interfaz de Usuario Avanzada:** Implementación de frameworks de JavaScript (React, Vue, Angular) para una experiencia de usuario más dinámica e interactiva.
* **Autenticación de Usuarios:** Añadir un sistema de login para profesionales de la salud.
* **Visualizaciones Interactivas:** Integrar gráficos (ej., con Plotly.js o D3.js) para visualizar los datos del paciente y las tendencias del perfil.
* **Manejo de Pacientes Existentes:** Funcionalidad para buscar y cargar informes de pacientes previamente registrados.

---
