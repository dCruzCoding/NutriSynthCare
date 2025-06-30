# 🏗️🩺 Creación database sintética (NutriSynthCare)

Este directorio contiene notebooks con el código para la creación de bases de datos sintéticas, su combinación y el proceso de imputación de valores faltantes. Forma parte del proyecto **[NutriSynthCare](https://github.com/dCruzCoding/NutriSynthCare)**, desarrollado por [Daniel Cruz](https://github.com/dCruzCoding) y [Aníbal García](https://github.com/Aniballll).

## 🗃️ Bases de Datos Sintéticas

### **db\_diabetes**

* **Filas**: 8000
* **Numéricas**: Edad, IMC, HbA1c, Insulina, Colesterol\_Total, LDL, HDL, Triglicéridos, PAS, PAD, Registro.  
* **Categóricas**: Sexo, Cuartil\_Edad.  
* **Target**: `Tipo_Diabetes` (categórica, 4 niveles).

### **db\_cardio**

* **Filas**: 8000
* **Numéricas**: Año\_Registro, Edad, Ingresos\_Anuales, IMC, Colesterol\_Total, Triglicéridos, PAS, PAD.  
* **Categóricas**: Sexo, Comunidad\_Autonoma, Actividad\_Fisica, Tramo\_Edad, Nivel\_Estres, Diabetes.  
* **Target**: `Riesgo_Cardiovascular` (categórica, 4 niveles).

### **db\_cardiabetes** *(union de anteriores)*

* **Filas**: 15964
* **Numéricas**: Año\_Registro, Edad, IMC, Colesterol\_Total, Triglicéridos, PAS, PAD, HbA1c, Insulina, LDL, HDL.
* **Categóricas**: Sexo, Diabetes, Cohorte, Actividad\_Fisica (reducida a 3 niveles), Nivel\_Estres, Tipo\_Diabetes (ampliada a 5 niveles).  
* **Target**: `Riesgo_Cardiovascular` (reducida a 2 niveles)

## 🔄 Pipeline de Generación de la Base de Datos Final

El siguiente esquema resume el proceso completo desde la creación hasta la preparación del dataset final:

```
\+------------------------+      \+------------------------------+

|  DB Sintética: Diabetes |      | DB Sintética: Riesgo Cardio |

\+------------------------+      \+------------------------------+
            |                               |
            '------------.  .---------------'
                         |  |
                          vv

            \+-----------------------------+
             |     UNIÓN DE LAS BASES      |
             | (Outer Join por columnas    |
             |        comunes)             |
            \+-----------------------------+
                          |
                          v

     \+-----------------------------------------+

     |  Dataset combinado con valores faltantes |

     \+-----------------------------------------+

                          |
                          v

\+----------------------------------------------------------+

|       PROCESO DE IMPUTACIÓN POR FASES (Num \+ Cat)        |

|                                                           |

|  🔢 Numéricas: Imputación por regresión o exclusión.     |

|  🔣 Categóricas: Imputación por clasificadores ML:       |

|     \- Contexto (Actividad, Estrés, etc.)                 |

|     \- Tipo\_Diabetes (Random Forest)                      |

|     \- Riesgo\_Cardiovascular (XGBoost)                    |

\+----------------------------------------------------------+

                         |
                         v

     \+------------------------------------------+

     |    DATASET FINAL IMPUTADO Y PREPARADO    |

     \+------------------------------------------+
```


## 📂 Archivos Relevantes (/Creación_databases)

Este directorio contiene los siguientes notebooks, organizados por fases del proceso:

### 🏗️ 1. Creación de Bases Sintéticas

* [`1.1_Crear_db_diabetes.ipynb`](./1.1_Crear_db_diabetes.ipynb)
  → Generación de la base de datos sintética **`db_diabetes`**, incluyendo variables clínicas relacionadas con la diabetes.

* [`1.2_Crear_db_cardio.ipynb`](./1.2_Crear_db_cardio.ipynb)
  → Generación de la base **`db_cardio`**, centrada en factores de riesgo cardiovascular y datos sociodemográficos.

---

### 🔗 2. Unión de Bases

* [`2_Uniendo_dbs.ipynb`](./2_Uniendo_dbs.ipynb)
  → Unión de ambas bases mediante *outer join* por columnas comunes.
  → Exploración de relaciones y coherencia entre variables. *(No se realiza imputación en esta fase).*

---

### 🩹 3. Imputación de Valores Faltantes (por fases)

* [`3.1_Imputacion1_RLM.ipynb`](./3.1_Imputacion1_RLM.ipynb)
  → Imputación de variables **numéricas** mediante regresión lineal múltiple y estrategias complementarias.

* [`3.2_Imputacion3_XGBoost.ipynb`](./3.2_Imputacion3_XGBoost.ipynb)
  → Imputación de **variables categóricas secundarias** utilizando clasificadores **XGBoost**.
  💾 Esta notebook guarda los siguientes modelos entrenados:

  * `xgb_mejor_modelo.pkl`: para la imputación de `Actividad_Fisica`
  * `xgb_modelo_nivel_estres.pkl`: para la imputación de `Nivel_Estres`

* [`3.3_Imputacion4_RandomForest.ipynb`](./3.3_Imputacion4_RandomForest.ipynb)
  → Imputación específica de la variable `Tipo_Diabetes` con modelos **Random Forest**.

* [`3.4_ImputacionFinal_RiesgoCardiovascular.ipynb`](./3.4_ImputacionFinal_RiesgoCardiovascular.ipynb)
  → Imputación de la variable **`Riesgo_Cardiovascular`**, considerada como **target principal** del dataset.

* [`3.5_Reescalado_varNormalizadas.ipynb`](./3.5_Reescalado_varNormalizadas.ipynb)
  → Reescalado, según cohorte, de variables que fueron normalizadas para facilitar el proceso de unión de ambas databases.

---

### 🧠 4. Imputación con Redes Neuronales

📁 [`Probando_RNs/`](./Probando_RNs)

* [`4.1_Imputando_RiesgoCardio_con_RNN.ipynb`](./Probando_RNs/4.1_Imputando_RiesgoCardio_con_RNN.ipynb)
  → Imputación de `Riesgo_Cardiovascular` utilizando **Redes Neuronales Recurrentes (RNN)**.

* [`4.2_Imputando_ALL_con_MICE-NN.ipynb`](./Probando_RNs/4.2_Imputando_ALL_con_MICE-NN.ipynb)
  → Imputación de **todas las variables** mediante el enfoque **MICE-NN** (Multiple Imputation by Chained Equations con redes neuronales).

> ⚠️ **¡OJO!**
> Las bases de datos usadas aquí son versiones específicas de las originales, preparadas para el punto justo del desarrollo donde tiene sentido aplicar cada código de imputación con redes neuronales:
>
> * `dbfinal_testing_MICE-NN.csv` para el notebook 4.2
> * `dbfinal_testing_nn.csv` para el notebook 4.1
---

### 🧾 Archivos con las databases

* [`db_diabetes.csv`](./db_diabetes.csv):
  Base de datos sintética sobre diabetes.

* [`db_cardio.csv`](./db_cardio.csv):
  Base de datos sintética sobre riesgo cardiovascular.

* [`db_cardiabet.csv`](./db_cardiabet.csv):
  Dataset final fusionado y procesado, listo para análisis y recomendaciones.

---

### 📚 Referencias

* [`Referencias DIABETES-CARDIO.docx`](./Referencias%20DIABETES-CARDIO.docx):
  Documento con las referencias bibliográficas utilizadas para la creación de ambas bases sintéticas.
