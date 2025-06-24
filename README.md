# 🩺🥗 NutriSynthCare: Bases Sintéticas y Recomendaciones Nutricionales

**NutriSynthCare** es un entorno de simulación que explora perfiles clínicos de la población española a través de **dos bases de datos sintéticas**: una sobre **diabetes** y otra sobre **riesgo cardiovascular**, generadas a partir de literatura científica previa al COVID-19.

Estas bases se combinan y se completan mediante técnicas de **imputación avanzada** para generar un único dataset mixto y coherente. A partir de él, el sistema permite:

- Detectar **perfiles clínicos** mediante técnicas de reducción de dimensionalidad y agrupamiento no supervisado.
- Generar **recomendaciones nutricionales personalizadas**, utilizando una ontología que relaciona condiciones de salud con nutrientes y alimentos.

> ⚠️ **Advertencia**: Los datos utilizados son completamente sintéticos y no deben emplearse para decisiones médicas. Este proyecto tiene fines educativos y exploratorios.


## ⚙️ Flujo del Proyecto y Técnicas Aplicadas

### 🔄 Fusión e Imputación de Datos Sintéticos

- **Modelos utilizados**: `XGBoost`, `Random Forest`, `Redes Neuronales (PyTorch)`  
- **Técnicas de imputación**: Regresión múltiple, clasificación supervisada, imputación con `MICE` y `MICE-NN`  
- **Optimización**: Búsqueda de hiperparámetros con `Optuna`

> Las bases de diabetes y riesgo cardiovascular se fusionan y se completan para generar un dataset único y coherente sobre el que se realizan el resto de análisis.

### 🧠 Recomendaciones Nutricionales Basadas en Ontologías

Se emplea un enfoque semántico para sugerir alimentos adaptados al perfil clínico del paciente.

- **Ontologías construidas con `rdflib`**  
  * Relaciones entre **condiciones de salud** (como diabetes o hipertensión) y **nutrientes** (fibra, omega-3, etc.)  
  * Mapeo de nutrientes a **alimentos específicos**

- **Proceso de recomendación**  
  * A partir de los datos clínicos imputados, se detectan condiciones presentes  
  * Se infieren recomendaciones nutricionales alineadas con cada condición de salud

- **Visualización inicial en App Web**  
  * Se ha desarrollado una **interfaz web básica con Flask** que permite consultar las recomendaciones nutricionales desde un navegador.  
  * Esta interfaz está en una **fase muy inicial**, pero ilustra el potencial de uso práctico del sistema.


### 📊 Agrupamiento de Perfiles Clínicos

Para identificar grupos homogéneos de pacientes y facilitar intervenciones personalizadas:

- **Técnicas aplicadas**  
  * Reducción de dimensionalidad con un `Autoencoder`  
  * Agrupamiento con `K-Means` sobre variables latentes

- **Objetivo del clustering**  
  * Descubrir patrones de salud comunes  
  * Generar perfiles clínicos útiles para análisis posteriores o recomendaciones específicas

    
## 🛠️ Tecnologías Utilizadas

| Categoría                 | Tecnologías                                                |
|--------------------------|------------------------------------------------------------|
| Creación y Gestión de Datos | `pandas`, `numpy`, `seaborn`, `matplotlib`, `scipy`, `sklearn` |
| Imputación y Modelado    | `xgboost`, `imblearn`, `joblib`, `os`, `optuna`, `pytorch` |
| Visualización            | `matplotlib`, `seaborn`                                    |
| Clustering               | `tensorflow`                                               |
| Ontologías               | `rdflib`                                                   |
| AppWeb                   | `flask`                                                    |


## 🧰 Requisitos Mínimos

Para ejecutar NutriSynthCare, se recomienda contar con el siguiente entorno y librerías instaladas. Puedes instalar todas las dependencias fácilmente usando el archivo `requirements.txt` incluido en este repositorio.

### Requisitos de sistema

- Python 3.8 o superior
- Al menos 8 GB de RAM (recomendado para procesamiento y modelado)
- Espacio libre en disco de al menos 1 GB

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

**Librerias incluidas:** *pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, xgboost, imblearn, joblib, optuna, torch (PyTorch), tensorflow, rdflib, flask*



## 🧾 Versión

v1.1 · Última actualización: junio de 2025

## 🚀 Próximas Mejoras: Versión 1.2

El desarrollo de NutriSynthCare continúa. Estas son las principales líneas de mejora previstas:

- 🗓️ **Adaptación post-COVID**  
  Incorporar cambios en los perfiles clínicos y patrones de salud tras la pandemia.

- 🌍 **Ampliación del contexto socioeconómico**  
  Añadir variables sobre situación económica, acceso a alimentos y entorno social.

- 💰 **Componente económico en las recomendaciones**  
  Ajustar las sugerencias alimenticias a las posibilidades económicas de cada individuo, buscando recomendaciones realistas y sostenibles.



## 🤝 Contribuciones

¿Te interesa mejorar este proyecto? ¡Cualquier idea es bienvenida\!

* Haz un fork del repositorio.  
* Crea una rama: `git checkout -b mejora/nueva-idea`.  
* Sube tus cambios: `git commit -m 'Nueva mejora'` y `git push`.  
* Abre un Pull Request explicando tus contribuciones.

Especialmente útiles son mejoras en la creación de ontologías, visualizaciones y estrategias de imputación.


## 📜 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](http://LICENSE) para más detalles.


## 👥 Autores

Este proyecto ha sido desarrollado por:

- [Daniel Cruz (dCruzCoding)](https://github.com/dCruzCoding)  
- [Aníbal García](https://github.com/Aniballll)

¡Gracias por visitar el repositorio!
