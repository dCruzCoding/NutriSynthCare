# 🧠 NutriSynthCare: Componente de Ontología y Sistema de Recomendaciones Nutricionales 🥗

Este documento describe en detalle el componente de ontología desarrollado para el proyecto NutriSynthCare. La ontología es un pilar fundamental para la generación de recomendaciones nutricionales personalizadas, formalizando el conocimiento en el ámbito de la salud y la dieta.

## 1. ¿Qué es una Ontología en este Contexto? 🤔

En el proyecto NutriSynthCare, la ontología es una representación estructurada y formal del conocimiento en el dominio de la nutrición y las condiciones de salud. Utiliza el lenguaje RDF (Resource Description Framework) para definir entidades y sus relaciones, permitiendo al sistema "entender" y "razonar" sobre la información para generar recomendaciones.

Está implementada en Python 🐍 utilizando la librería `rdflib`, construyendo un grafo de conocimiento que interconecta condiciones de salud, nutrientes y alimentos.

## 2. Propósito y Finalidad de la Ontología ✨

La ontología ha sido diseñada con los siguientes objetivos principales:

* **Formalizar el Conocimiento:** 📚 Codificar de manera explícita y machine-readable las relaciones validadas entre diversas condiciones de salud (como diabetes, hipertensión, riesgo cardiovascular, etc.) y su impacto nutricional, así como la composición nutricional de ciertos alimentos. Esto se basa en un conocimiento experto simulado a partir de la literatura científica.
* **Facilitar la Inferencia y el Razonamiento:** 💡 Actuar como un motor de conocimiento que permite al sistema inferir recomendaciones. Cuando el perfil de un paciente revela ciertas condiciones de salud, la ontología permite al sistema "consultar" estas condiciones y determinar automáticamente qué nutrientes son beneficiosos para mejorar esa condición y cuáles podrían ser perjudiciales.
* **Personalización de Recomendaciones Nutricionales:** 🎯 Al combinar el conocimiento de la ontología con las condiciones de salud detectadas en un paciente individual (identificadas a través del procesamiento de sus datos y el clustering), el sistema puede generar un conjunto de recomendaciones dietéticas altamente personalizadas y basadas en evidencia (simulada).

## 3. Componentes Clave de la Ontología 🏗️

La ontología de NutriSynthCare se compone de las siguientes clases (tipos de entidades) y propiedades (relaciones):

### 3.1. Clases (Entidades) 🏷️

* **`Food` (Alimento):** 🍎 Representa alimentos concretos que pueden ser parte de una dieta.
    * Ejemplos: `Salmon` (Salmón), `Walnuts` (Nueces), `Lentils` (Lentejas), `Spinach` (Espinacas), `Yogurt`, `Oats` (Avena), `Blueberries` (Arándanos), `Almonds` (Almendras).
* **`Nutrient` (Nutriente):** 💊 Representa macronutrientes y micronutrientes, así como otros componentes dietéticos relevantes.
    * Ejemplos de nutrientes beneficiosos: `Fiber` (Fibra), `Omega3`, `Calcium` (Calcio), `Magnesium` (Magnesio), `Protein` (Proteína), `VitaminD` (Vitamina D), `Potassium` (Potasio), `Antioxidants` (Antioxidantes).
    * Ejemplos de nutrientes a limitar: `Sodium` (Sodio), `SaturatedFat` (Grasa Saturada), `SimpleSugars` (Azúcares Simples).
* **`Condition` (Condición de Salud/Riesgo):** 🤒 Representa estados de salud, enfermedades o niveles de riesgo asociados.
    * Ejemplos: `Diabetes`, `Hypertension` (Hipertensión), `HighCholesterol` (Colesterol Alto), `Overweight` (Sobrepeso), `Underweight` (Bajo Peso).
    * Niveles de Riesgo Cardiovascular: `CardiovascularRisk_Low`, `CardiovascularRisk_Moderate`, `CardiovascularRisk_High`, `CardiovascularRisk_VeryHigh`.
* **`Profile` (Perfil de Paciente):** 👤 Representa los grupos o segmentos de pacientes identificados por el clustering. (Aunque las recomendaciones actuales se basan más directamente en `Condition`, `Profile` es una clase extensible para futuras reglas ontológicas a nivel de grupo).

### 3.2. Propiedades (Relaciones) 🔗

* **`containsNutrient`:** Propiedad que vincula una instancia de `Food` con las instancias de `Nutrient`s que contiene.
    * Ejemplo: `Salmon containsNutrient Omega3`.
* **`beneficialFor`:** ✅ Propiedad que relaciona una instancia de `Nutrient` con una instancia de `Condition` para la cual ese nutriente es favorable o ayuda a gestionar.
    * Ejemplo: `Fiber beneficialFor Diabetes`.
* **`harmfulFor`:** 🚫 Propiedad que relaciona una instancia de `Nutrient` con una instancia de `Condition` para la cual ese nutriente es perjudicial o cuyo consumo debe ser limitado.
    * Ejemplo: `Sodium harmfulFor Hypertension`.
* **`hasNutritionalRecommendation` (en desarrollo):** 📈 Una propiedad que podría usarse en el futuro para vincular directamente `Profile`s de pacientes con un conjunto general de `Nutrient`s o `Food`s.

## 4. Funcionamiento del Sistema de Recomendaciones con la Ontología ⚙️

El proceso de generación de recomendaciones nutricionales mediante la ontología sigue estos pasos en el backend de la aplicación:

1.  **Carga e Inicialización:** 🚀 Durante el inicio de la aplicación, en la función `initialize_models()` de `core_functions.py`, se crea el grafo RDF (`g`) y se puebla con todas las clases, propiedades y relaciones predefinidas (ej., "Fibra es beneficiosa para Diabetes", "El Salmón contiene Omega3").
2.  **Detección de Condiciones del Paciente:** 🩺 Cuando se procesan los datos de un paciente (ya sea nuevo o existente), la función `get_patient_conditions()` analiza sus métricas de salud (IMC, HbA1c, presión arterial, etc.) y calcula su riesgo cardiovascular. Esto resulta en una lista de `Condition`s específicas para ese paciente (ej., `['Diabetes', 'Hypertension', 'CardiovascularRisk_Moderate']`).
3.  **Consulta a la Ontología:** 🔎 La función `get_recommended_nutrients_for_patient()` recibe esta lista de condiciones. Para cada condición, realiza consultas al grafo ontológico (`g`) para encontrar:
    * Todos los `Nutrient`s relacionados mediante la propiedad `beneficialFor` con esa `Condition`.
    * Todos los `Nutrient`s relacionados mediante la propiedad `harmfulFor` con esa `Condition`.
4.  **Generación de Recomendaciones:** 📝 El sistema compila estas listas de nutrientes recomendados para aumentar y nutrientes a disminuir. Estos son presentados al usuario en el informe final, a menudo complementados con ejemplos de `Food`s que contienen dichos `Nutrient`s (aunque la vinculación explícita de `Food`s a recomendaciones finales es una extensión futura o se realiza de forma textual).

### Ejemplo de Razonamiento Ontológico: 🤔➡️✅🚫

Si un paciente tiene `Diabetes` y `HighCholesterol`:
* La ontología identifica que `Fiber` es `beneficialFor` `Diabetes` y `HighCholesterol`.
* Identifica que `Omega3` es `beneficialFor` `Diabetes` y `HighCholesterol`.
* Identifica que `SaturatedFat` es `harmfulFor` `HighCholesterol`.
* Identifica que `SimpleSugars` es `harmfulFor` `Diabetes`.

El sistema consolidaría estas inferencias para recomendar "Aumentar Fibra, Omega3" y "Disminuir Grasa Saturada, Azúcares Simples".

## 5. Extensibilidad y Futuro 🚀

La naturaleza modular y declarativa de la ontología permite una fácil extensión. Se pueden añadir nuevas condiciones, nutrientes o alimentos, así como refinar las relaciones existentes, sin necesidad de reescribir la lógica de inferencia del sistema. Esto es crucial para la adaptabilidad del proyecto a nuevos conocimientos nutricionales o perfiles de pacientes.
