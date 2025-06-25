import pandas as pd
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.cluster import KMeans
from rdflib import Graph, Namespace, RDF, RDFS
import os

# --- Definición de Variables (¡Globales para acceso por otras funciones!) ---
variables_numericas = ['Edad', 'IMC', 'HbA1c', 'PAS', 'PAD', 'Colesterol_Total', 'LDL', 'HDL', 'Insulina', 'Trigliceridos']
variables_categoricas = ['Sexo', 'Actividad_Fisica', 'Nivel_Estres', 'Riesgo_Cardiovascular', 'source_Diabetes', 'Tipo_Diabetes', 'Año_Registro']

# --- RANGOS REALISTAS PARA LA VISUALIZACIÓN ---
realistic_ranges = {
    'Edad': {'min': 18, 'max': 90},
    'IMC': {'min': 15.0, 'max': 50.0},
    'HbA1c': {'min': 4.0, 'max': 15.0},
    'PAS': {'min': 80, 'max': 200},
    'PAD': {'min': 50, 'max': 120},
    'Colesterol_Total': {'min': 100.0, 'max': 300.0},
    'LDL': {'min': 50, 'max': 250},
    'HDL': {'min': 20, 'max': 100},
    'Insulina': {'min': 2.0, 'max': 300.0},
    'Trigliceridos': {'min': 30.0, 'max': 1000.0}
}

# --- Variables globales para los modelos y datos (se inicializan en initialize_models) ---
df_diabetes_original_for_display = None
df_autoencoder_processed = None
encoder = None
scaler = None
autoencoder = None
encoder_model = None
kmeans = None
df_diabetes_original_for_display_rescaled = None # Asegurarse de que esta también sea global y se inicialice

# --- Ontología: Definición de Namespaces (¡AHORA GLOBALES!) ---
FOOD = Namespace("http://example.org/food/")
NUT = Namespace("http://example.org/nutrient/")
COND = Namespace("http://example.org/condition/")
EX = Namespace("http://example.org/ex/")
PROF = Namespace("http://example.org/profile/")
g = Graph() # El grafo también debe ser global, se rellenará en initialize_models

# --- FUNCIÓN DE RE-ESCALADO A RANGO REALISTA ---
def rescale_to_realistic_range(df_input, columns_to_rescale, ranges):
    df_rescaled = df_input.copy()
    for col in columns_to_rescale:
        if col in df_rescaled.columns and col in ranges:
            current_min = df_rescaled[col].min()
            current_max = df_rescaled[col].max()
            
            if current_max == current_min:
                df_rescaled[col] = (ranges[col]['min'] + ranges[col]['max']) / 2
                continue

            df_rescaled[col] = (df_rescaled[col] - current_min) / (current_max - current_min)
            df_rescaled[col] = df_rescaled[col] * (ranges[col]['max'] - ranges[col]['min']) + ranges[col]['min']
            df_rescaled[col] = np.clip(df_rescaled[col], ranges[col]['min'], ranges[col]['max'])
    return df_rescaled

# --- FUNCIÓN: Inicializar y entrenar todos los modelos (Se llama una única vez) ---
def initialize_models():
    global df_diabetes_original_for_display, df_autoencoder_processed, encoder, scaler, autoencoder, encoder_model, kmeans, g, df_diabetes_original_for_display_rescaled

    # --- Cargar datos ---
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'dbfinal_precov_COMPLETA.csv')
    try:
        print(f"Intentando cargar CSV desde: {csv_path}")
        df_diabetes = pd.read_csv(csv_path)
        print(f"CSV cargado exitosamente. Filas: {len(df_diabetes)}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: '{csv_path}' no encontrado. Asegúrate de que está en la misma carpeta.")
    
    # --- Asegurar que 'ID_Paciente' existe ---
    if 'ID_Paciente' not in df_diabetes.columns:
        df_diabetes['ID_Paciente'] = [f'P{i:04d}' for i in range(len(df_diabetes))]
        print("Se ha generado la columna 'ID_Paciente'.")

    df_diabetes_original_for_display = df_diabetes.copy()
    df_autoencoder_processed = df_diabetes.copy()

    # --- Preparación de datos para Autoencoder y K-Means ---
    existing_numeric_cols = [col for col in variables_numericas if col in df_autoencoder_processed.columns]
    existing_categorical_cols = [col for col in variables_categoricas if col in df_autoencoder_processed.columns]

    # Imputar nulos y preparar datos
    for col in existing_numeric_cols:
        df_autoencoder_processed[col] = pd.to_numeric(df_autoencoder_processed[col], errors='coerce')
        df_autoencoder_processed[col] = df_autoencoder_processed[col].fillna(df_autoencoder_processed[col].mean())

    for col in existing_categorical_cols:
        if col in df_autoencoder_processed.columns: # Asegurar que la columna existe antes de intentar convertir
            if df_autoencoder_processed[col].dtype == 'int64' or df_autoencoder_processed[col].dtype == 'float64':
                df_autoencoder_processed[col] = df_autoencoder_processed[col].astype(str)
            df_autoencoder_processed[col] = df_autoencoder_processed[col].fillna(df_autoencoder_processed[col].mode()[0])
        else: # Si la columna categórica no existe, la añadimos con un valor por defecto o la omitimos
            # Para este caso, si no está en el CSV original pero se espera, se manejará como parte del default_values en process_new_patient_data
            pass # No hacer nada si la columna no existe en el DF cargado

    # Entrenar Scaler y Encoder con los datos completos
    scaler = StandardScaler()
    X_numericas_scaled = scaler.fit_transform(df_autoencoder_processed[existing_numeric_cols])

    encoder = OneHotEncoder(drop='first', handle_unknown='ignore')
    X_categoricas_encoded = encoder.fit_transform(df_autoencoder_processed[existing_categorical_cols]).toarray()

    X_for_autoencoder = np.concatenate([X_numericas_scaled, X_categoricas_encoded], axis=1)

    # Autoencoder
    input_dim = X_for_autoencoder.shape[1]
    encoding_dim = 12 
    input_layer = Input(shape=(input_dim,))
    encoded = Dense(input_dim // 2, activation='relu')(input_layer)
    encoded = Dense(encoding_dim * 2, activation='relu')(encoded)
    encoded = Dense(encoding_dim, activation='relu')(encoded)
    decoded = Dense(encoding_dim * 2, activation='relu')(encoded)
    decoded = Dense(input_dim // 2, activation='relu')(decoded)
    decoded = Dense(input_dim, activation='linear')(decoded)
    autoencoder = Model(input_layer, decoded)
    encoder_model = Model(input_layer, encoded)
    autoencoder.compile(optimizer='adam', loss='mse')

    # Entrenamiento del Autoencoder (verbose=0 para no imprimir durante el inicio de la app)
    autoencoder.fit(X_for_autoencoder, X_for_autoencoder, epochs=150, batch_size=64, validation_split=0.2, verbose=0)

    # K-Means
    k_optimo = 4 # Usamos el k óptimo determinado previamente
    kmeans = KMeans(n_clusters=k_optimo, random_state=42, n_init=10)
    df_autoencoder_processed['Perfil'] = kmeans.fit_predict(encoder_model.predict(X_for_autoencoder))
    df_diabetes_original_for_display['Perfil'] = df_autoencoder_processed['Perfil']

    df_diabetes_original_for_display_rescaled = rescale_to_realistic_range(df_diabetes_original_for_display.copy(), existing_numeric_cols, realistic_ranges)

    # --- Construcción de la Ontología (poblar el grafo global 'g') ---
    g.bind("food", FOOD)
    g.bind("nut", NUT)
    g.bind("cond", COND)
    g.bind("ex", EX)
    g.bind("prof", PROF)

    g.add((FOOD.Food, RDF.type, RDFS.Class))
    g.add((NUT.Nutrient, RDF.type, RDFS.Class))
    g.add((COND.Condition, RDF.type, RDFS.Class))
    g.add((PROF.Profile, RDF.type, RDFS.Class))
    g.add((EX.hasCondition, RDF.type, RDF.Property))
    g.add((EX.beneficialFor, RDF.type, RDF.Property))
    g.add((EX.harmfulFor, RDF.type, RDF.Property))
    g.add((NUT.containsNutrient, RDF.type, RDF.Property))
    g.add((PROF.hasNutritionalRecommendation, RDF.type, RDF.Property))

    for profile_id in df_autoencoder_processed['Perfil'].unique():
        profile_uri = getattr(PROF, f"Profile_{profile_id}")
        g.add((profile_uri, RDF.type, PROF.Profile))

    # Nuevas condiciones de riesgo cardiovascular
    g.add((COND.CardiovascularRisk_Low, RDF.type, COND.Condition))
    g.add((COND.CardiovascularRisk_Moderate, RDF.type, COND.Condition))
    g.add((COND.CardiovascularRisk_High, RDF.type, COND.Condition))
    g.add((COND.CardiovascularRisk_VeryHigh, RDF.type, COND.Condition))

    nutrient_benefits = {
        "Fiber": ["Diabetes", "HighCholesterol", "Overweight", "CardiovascularRisk_High", "CardiovascularRisk_VeryHigh"], 
        "Omega3": ["Hypertension", "HighCholesterol", "Diabetes", "CardiovascularRisk_High", "CardiovascularRisk_VeryHigh"], 
        "Calcium": ["Hypertension", "Underweight"],
        "Magnesium": ["Hypertension", "Diabetes", "CardiovascularRisk_High", "CardiovascularRisk_VeryHigh"], 
        "Protein": ["Underweight", "Diabetes", "Overweight"],
        "VitaminD": ["HighCholesterol", "Diabetes", "Underweight", "CardiovascularRisk_High", "CardiovascularRisk_VeryHigh"], 
        "Potassium": ["Hypertension"],
        "Antioxidants": ["Diabetes", "HighCholesterol", "CardiovascularRisk_High", "CardiovascularRisk_VeryHigh"] 
    }

    for nutrient, conditions in nutrient_benefits.items():
        g.add((getattr(NUT, nutrient), RDF.type, NUT.Nutrient))
        for condition_name in conditions:
            g.add((getattr(NUT, nutrient), EX.beneficialFor, getattr(COND, condition_name)))
            
    nutrient_harms = {
        "Sodium": ["Hypertension", "CardiovascularRisk_High", "CardiovascularRisk_VeryHigh"], 
        "SaturatedFat": ["HighCholesterol", "Diabetes", "CardiovascularRisk_High", "CardiovascularRisk_VeryHigh"], 
        "SimpleSugars": ["Diabetes", "Overweight", "CardiovascularRisk_High", "CardiovascularRisk_VeryHigh"] 
    }

    for nutrient, conditions in nutrient_harms.items():
        g.add((getattr(NUT, nutrient), RDF.type, NUT.Nutrient))
        for condition_name in conditions:
            g.add((getattr(NUT, nutrient), EX.harmfulFor, getattr(COND, condition_name)))

    food_nutrients = {
        "Salmon": ["Omega3", "Protein", "VitaminD"],
        "Walnuts": ["Omega3", "Magnesium", "Antioxidants", "Protein", "Fiber"],
        "Lentils": ["Fiber", "Protein", "Magnesium"],
        "Spinach": ["Magnesium", "Calcium", "Fiber", "Antioxidants"],
        "Yogurt": ["Calcium", "Protein"],
        "Oats": ["Fiber", "Magnesium", "Protein"],
        "Blueberries": ["Antioxidants", "Fiber"],
        "Almonds": ["Magnesium", "Protein", "Fiber", "Antioxidants"],
    }

    for food, nutrients in food_nutrients.items():
        g.add((getattr(FOOD, food), RDF.type, FOOD.Food))
        for nutrient in nutrients:
            g.add((getattr(FOOD, food), NUT.containsNutrient, getattr(NUT, nutrient)))

# --- FUNCIÓN: Cálculo del Riesgo Cardiovascular por Niveles ---
def calculate_cardiovascular_risk(patient_data_row):
    risk_score = 0
    
    edad = patient_data_row.get('Edad', 0)
    imc = patient_data_row.get('IMC', 0)
    hba1c = patient_data_row.get('HbA1c', 0)
    pas = patient_data_row.get('PAS', 0)
    pad = patient_data_row.get('PAD', 0)
    ldl = patient_data_row.get('LDL', 0)
    hdl = patient_data_row.get('HDL', 0)
    trigliceridos = patient_data_row.get('Trigliceridos', 0)
    actividad_fisica = patient_data_row.get('Actividad_Fisica', 'No disponible')
    nivel_estres = patient_data_row.get('Nivel_Estres', 'No disponible')
    sexo = patient_data_row.get('Sexo', 'No disponible')
    
    # 1. Factores de Edad
    if edad >= 65:
        risk_score += 3
    elif edad >= 45:
        risk_score += 2
    elif edad >= 30:
        risk_score += 1
        
    # 2. Factores de IMC
    if imc >= 30: # Obesidad
        risk_score += 3
    elif imc >= 25: # Sobrepeso
        risk_score += 2
    
    # 3. Factores de Glucosa (HbA1c / Diabetes)
    # Convertir 'Diabetes' a int si es string '0' o '1'
    diabetes_val = patient_data_row.get('Diabetes')
    if isinstance(diabetes_val, str):
        try:
            diabetes_val = int(diabetes_val)
        except ValueError:
            diabetes_val = 0 # Default si la conversión falla
    
    if diabetes_val == 1 or hba1c > 6.5: # Diabetes
        risk_score += 4
    elif hba1c >= 5.7: # Pre-diabetes
        risk_score += 2

    # 4. Factores de Presión Arterial
    if pas >= 140 or pad >= 90: # Hipertensión Grado 2 o más
        risk_score += 4
    elif pas >= 130 or pad >= 80: # Hipertensión Grado 1
        risk_score += 2
        
    # 5. Factores de Lípidos
    if ldl > 160: # LDL muy alto
        risk_score += 3
    elif ldl > 130: # LDL alto
        risk_score += 2
        
    if hdl < 40 and sexo == 'Hombre': # HDL bajo en hombres
        risk_score += 2
    elif hdl < 50 and sexo == 'Mujer': # HDL bajo en mujeres
        risk_score += 2
        
    if trigliceridos > 200: # Triglicéridos altos
        risk_score += 2
    elif trigliceridos > 150: # Triglicéridos borderline
        risk_score += 1

    # 6. Factores de Estilo de Vida
    if actividad_fisica == 'Sedentario':
        risk_score += 2
    if nivel_estres == 'Alto':
        risk_score += 1
        
    # --- Mapeo del Score a Niveles de Riesgo ---
    if risk_score >= 12:
        return "CardiovascularRisk_VeryHigh"
    elif risk_score >= 8:
        return "CardiovascularRisk_High"
    elif risk_score >= 4:
        return "CardiovascularRisk_Moderate"
    else:
        return "CardiovascularRisk_Low"

# --- FUNCIÓN MEJORADA: Obtener condiciones del paciente individual ---
def get_patient_conditions(patient_data_row):
    conditions = set()

    hba1c = patient_data_row.get('HbA1c', 0)
    pas = patient_data_row.get('PAS', 0)
    ldl = patient_data_row.get('LDL', 0)
    imc = patient_data_row.get('IMC', 0)
    pad = patient_data_row.get('PAD', 0)
    
    # Lógica de Diabetes
    diabetes_val = patient_data_row.get('Diabetes')
    if isinstance(diabetes_val, str):
        try:
            diabetes_val = int(diabetes_val)
        except ValueError:
            diabetes_val = 0 # Default si la conversión falla

    if diabetes_val == 1 or hba1c > 6.5:
        conditions.add("Diabetes")

    # Consideramos PAS y PAD para hipertensión
    if pas > 130 or pad > 80:
        conditions.add("Hypertension")
    if ldl > 100:
        conditions.add("HighCholesterol")
    if imc > 25:
        conditions.add("Overweight")
    elif imc < 18.5:
        conditions.add("Underweight")
    
    # Calcular el riesgo cardiovascular dinámicamente
    calculated_cardio_risk_level = calculate_cardiovascular_risk(patient_data_row)
    conditions.add(calculated_cardio_risk_level)
        
    return list(conditions)

# Función para obtener los nutrientes recomendados
def get_recommended_nutrients_for_patient(patient_conditions):
    nutrients_to_increase = set()
    nutrients_to_decrease = set()

    # Asegurarse de que el grafo 'g' está inicializado
    if g is None:
        raise RuntimeError("Ontología (g) no inicializada. Llama a initialize_models() primero.")

    for condition_name in patient_conditions:
        # Asegurarse de que la condición existe como URI en la ontología
        # Usamos getattr de forma segura con un valor por defecto que no sea None
        condition_uri = getattr(COND, condition_name, None) 
        if condition_uri is not None: 
            beneficial_nuts = [subj for subj, pred, obj in g.triples((None, EX.beneficialFor, condition_uri))]
            nutrients_to_increase.update([str(n).split('/')[-1] for n in beneficial_nuts])

            harmful_nuts = [subj for subj, pred, obj in g.triples((None, EX.harmfulFor, condition_uri))]
            nutrients_to_decrease.update([str(n).split('/')[-1] for n in harmful_nuts])
        else:
            print(f"Advertencia: Condición '{condition_name}' no encontrada en la ontología COND.")
        
    return sorted(list(nutrients_to_increase)), sorted(list(nutrients_to_decrease))


# --- FUNCIÓN PRINCIPAL PARA GENERAR EL INFORME DE UN PACIENTE (Devuelve HTML) ---
def generate_patient_report_html(patient_id=None, patient_data_dict=None):
    """
    Genera el informe HTML para un paciente.
    Puede recibir un patient_id (para buscar en el DF existente) o patient_data_dict (para un paciente nuevo).
    """
    global df_diabetes_original_for_display_rescaled # Accede al DF re-escalado global
    
    patient_data_row = None
    patient_id_display = "Nuevo Paciente" # Default para nuevos pacientes

    if patient_id:
        # Asegurarse de que df_diabetes_original_for_display_rescaled no sea None
        if df_diabetes_original_for_display_rescaled is None:
            raise RuntimeError("Los modelos de IA no se han inicializado correctamente.")
        patient_data = df_diabetes_original_for_display_rescaled[df_diabetes_original_for_display_rescaled['ID_Paciente'] == patient_id]
        if patient_data.empty:
            return f"<p>No se encontraron datos para el paciente **{patient_id}**.</p>", patient_id
        patient_data_row = patient_data.iloc[0]
        patient_id_display = patient_id
    elif patient_data_dict:
        patient_data_row = pd.Series(patient_data_dict)
        # Asegurarse de que 'Perfil' tenga un valor por defecto si no está presente
        if 'Perfil' not in patient_data_row or pd.isna(patient_data_row['Perfil']):
             patient_data_row['Perfil'] = -1 # Un valor que indique "No Calculado"
    else:
        return "<p>No se proporcionó un ID de paciente ni datos de paciente.</p>", "Error"

    report_html = f"<h2>Informe Personalizado de Salud y Nutrición para Paciente {patient_id_display}</h2>"

    ## 1. Características del Paciente
    report_html += "<h3>1. Características del Paciente</h3>"
    report_html += "<hr>"
    display_cols = ['Edad', 'Sexo', 'IMC', 'HbA1c', 'PAS', 'PAD', 'Colesterol_Total', 'LDL', 'HDL', 'Insulina', 'Trigliceridos', 
                    'Diabetes', 'Actividad_Fisica', 'Nivel_Estres', 
                    'Riesgo_Cardiovascular', 'source_Diabetes', 'Tipo_Diabetes', 'Año_Registro', 'Perfil']
    
    report_html += "<ul>"
    for col in display_cols:
        value = patient_data_row.get(col, "No disponible")
        
        display_value = "No disponible"
        if pd.isna(value):
            display_value = "No disponible"
        elif col == 'Diabetes' or col == 'source_Diabetes':
            # Convertir a int si es posible antes de la comparación
            try:
                display_value = "Sí" if int(value) == 1 else "No"
            except (ValueError, TypeError):
                display_value = str(value) # Si no se puede convertir a int, mostrarlo tal cual
        elif col == 'Perfil':
            display_value = str(int(value)) if pd.notna(value) else "No Calculado"
            if int(value) == -1: # Si es el valor por defecto para "No Calculado"
                display_value = "No Calculado"
        elif isinstance(value, (int, float)):
            if col in ['Edad', 'PAS', 'PAD', 'LDL', 'HDL', 'Insulina']:
                display_value = str(int(value))
            else:
                display_value = f"{value:.2f}"
        else:
            display_value = str(value)
            
        report_html += f"<li><strong>{col.replace('_', ' ')}</strong>: {display_value}</li>"
    report_html += "</ul>"

    ## 2. Condiciones de Salud Detectadas
    detected_conditions = get_patient_conditions(patient_data_row)
    
    report_html += "<h3>2. Condiciones de Salud Detectadas</h3>"
    report_html += "<hr>"
    if detected_conditions:
        report_html += "<ul>"
        for cond in sorted(list(set(detected_conditions))):
            if cond.startswith("CardiovascularRisk_"):
                display_cond = "Riesgo Cardiovascular " + cond.replace("CardiovascularRisk_", "").replace("High", "Alto").replace("Low", "Bajo").replace("Moderate", "Moderado").replace("Very", "Muy ")
            else:
                display_cond = cond
            report_html += f"<li><strong>{display_cond}</strong></li>"
        report_html += "</ul>"
    else:
        report_html += "<p>Ninguna condición de salud específica detectada para este paciente basada en sus datos.</p>"

    ## 3. Recomendaciones Nutricionales
    nutrients_to_increase, nutrients_to_decrease = get_recommended_nutrients_for_patient(detected_conditions)

    report_html += "<h3>3. Recomendaciones Nutricionales</h3>"
    report_html += "<hr>"
    
    if nutrients_to_increase or nutrients_to_decrease:
        report_html += "<p>Basado en sus condiciones de salud, se recomienda prestar atención a los siguientes nutrientes:</p>"
        
        if nutrients_to_increase:
            report_html += "<p><strong>Aumentar el consumo de:</strong></p><ul>"
            for nut in nutrients_to_increase:
                report_html += f"<li><strong>{nut}</strong></li>"
            report_html += "</ul>"
        
        if nutrients_to_decrease:
            report_html += "<p><strong>Disminuir o limitar el consumo de:</strong></p><ul>"
            for nut in nutrients_to_decrease:
                report_html += f"<li><strong>{nut}</strong></li>"
            report_html += "</ul>"
    else:
        report_html += "<p>No se identificaron nutrientes específicos para recomendar en base a las condiciones detectadas.</p>"

    report_html += "<p><em>Recuerde que estas son recomendaciones generales. Consulte a un profesional de la salud para un plan nutricional personalizado.</em></p>"
    
    return report_html, patient_id_display

# --- NUEVA FUNCIÓN: Procesar datos de un nuevo paciente (con IMC desde peso/altura) ---
def process_new_patient_data(form_data):
    """
    Recibe un diccionario con los datos del formulario de un nuevo paciente,
    calcula IMC, los preprocesa, asigna un perfil y genera el HTML del informe.
    """
    global encoder, scaler, autoencoder, encoder_model, kmeans, df_autoencoder_processed 
    
    if encoder is None or scaler is None or encoder_model is None or kmeans is None or df_autoencoder_processed is None:
        raise RuntimeError("Modelos de IA o datos originales no inicializados. Llama a initialize_models() primero.")

    patient_row_dict = {}

    # Calcular IMC si se proporcionan peso y altura
    # ¡Importante! Usamos 'peso' y 'altura' que vienen del formulario para recalcular el IMC
    try:
        peso_str = form_data.get('peso')
        altura_str = form_data.get('altura')

        peso = float(peso_str) if peso_str is not None and peso_str.strip() != '' else 0.0
        altura_cm = float(altura_str) if altura_str is not None and altura_str.strip() != '' else 0.0

        if peso > 0 and altura_cm > 0:
            altura_m = altura_cm / 100 # Convertir cm a metros
            imc_calculated = round(peso / (altura_m ** 2), 2)
            patient_row_dict['IMC'] = imc_calculated
        else:
            patient_row_dict['IMC'] = 25.0 # Valor por defecto si peso/altura no son válidos
            print(f"Advertencia: Peso ({peso_str}) o altura ({altura_str}) no válidos o cero, IMC se estableció a un valor por defecto.")
    except (TypeError, ValueError) as e:
        print(f"Error al calcular IMC a partir de peso/altura: {e}. Peso: {form_data.get('peso')}, Altura: {form_data.get('altura')}")
        patient_row_dict['IMC'] = 25.0 # Valor por defecto en caso de error de conversión
        print("Advertencia: Error crítico en cálculo de IMC, IMC se estableció a un valor por defecto.")


    # Mapeo de Nivel_Estres de slider (1-5) a categorías ('Bajo', 'Medio', 'Alto')
    stress_map = {'1': 'Bajo', '2': 'Bajo', '3': 'Medio', '4': 'Alto', '5': 'Alto'}
    nivel_estres_val = form_data.get('nivel_estres')
    patient_row_dict['Nivel_Estres'] = stress_map.get(str(nivel_estres_val), 'Medio')

    # Convertir Edad a int (con robustez mejorada)
    edad_str = form_data.get('edad')
    try:
        if edad_str is not None and edad_str.strip() != '':
            patient_row_dict['Edad'] = int(edad_str)
        else:
            patient_row_dict['Edad'] = 30 # Valor por defecto si es None o vacía
            print("Advertencia: Edad es None o vacía, usando valor por defecto 30.")
    except ValueError:
        print(f"Advertencia: No se pudo convertir 'Edad' a int ('{edad_str}'). Usando valor por defecto 30.")
        patient_row_dict['Edad'] = 30


    # Mapeo de Diabetes a 0 o 1 (con robustez mejorada)
    diabetes_str = form_data.get('diabetes')
    try:
        if diabetes_str is not None and diabetes_str.strip() != '':
            patient_row_dict['Diabetes'] = int(diabetes_str)
        else:
            patient_row_dict['Diabetes'] = 0 # Valor por defecto si es None o vacía (asumiendo 'No')
            print("Advertencia: Diabetes es None o vacía, usando valor por defecto 0.")
    except ValueError:
        print(f"Advertencia: No se pudo convertir 'Diabetes' a int ('{diabetes_str}'). Usando valor por defecto 0.")
        patient_row_dict['Diabetes'] = 0

    # Mapeo de Actividad_Fisica
    actividad_fisica_val = form_data.get('actividad_fisica')
    patient_row_dict['Actividad_Fisica'] = actividad_fisica_val if actividad_fisica_val is not None and actividad_fisica_val.strip() != '' else 'Moderado' # Valor por defecto


    sexo_val = form_data.get('sexo')
    patient_row_dict['Sexo'] = sexo_val if sexo_val is not None and sexo_val.strip() != '' else 'Hombre' # Valor por defecto

    # Rellenar con valores predeterminados para las columnas que no se piden en el formulario
    default_values = {
        'HbA1c': 5.5, 'PAS': 120, 'PAD': 70, 'Colesterol_Total': 200, 
        'LDL': 100, 'HDL': 50, 'Insulina': 15, 'Trigliceridos': 100,
        'Consumo_Alcohol': 'No', 'Riesgo_Cardiovascular': 'Low', # Este se recalculará
        'source_Diabetes': 0, 'Tipo_Diabetes': 'No', 'Año_Registro': '2023',
    }

    # Combinar los datos del formulario con los valores por defecto
    for col in variables_numericas + variables_categoricas:
        if col not in patient_row_dict: # Si la columna no se ha definido ya (como IMC, Edad, Diabetes)
            if col in default_values:
                patient_row_dict[col] = default_values[col]
            else:
                # Esto debería ser raro si variables_numericas/categoricas están bien definidas
                # y default_values cubre lo no recogido del formulario.
                patient_row_dict[col] = np.nan 


    patient_df = pd.DataFrame([patient_row_dict])
    
    # Asegurarse de que los tipos de datos sean correctos para el preprocesamiento
    for col in variables_numericas:
        patient_df[col] = pd.to_numeric(patient_df[col], errors='coerce')
        if col in df_autoencoder_processed.columns: # Asegurarse de que la columna existe en el DF original para la media
             patient_df[col] = patient_df[col].fillna(df_autoencoder_processed[col].mean())
        else: # Fallback si la columna no estaba en el DF original (debería estar cubierta por variables_numericas)
             patient_df[col] = patient_df[col].fillna(0) 

    for col in variables_categoricas:
        if col in patient_df.columns: # Asegurarse de que la columna existe antes de intentar modificarla
            if patient_df[col].dtype == 'int64' or patient_df[col].dtype == 'float64':
                patient_df[col] = patient_df[col].astype(str)
            if col in df_autoencoder_processed.columns:
                patient_df[col] = patient_df[col].fillna(df_autoencoder_processed[col].mode()[0])
            else: # Fallback
                patient_df[col] = patient_df[col].fillna('No disponible')
        else: # Si la columna categórica no existe en patient_df pero es esperada por el modelo
            patient_df[col] = default_values.get(col, 'No disponible') # Usar un valor por defecto seguro


    # Ordenar las columnas de patient_df para que coincidan con el orden de entrenamiento
    # Esto es crucial para el scaler y encoder

    # --- CAMBIO APLICADO AQUÍ: Simplifica la obtención de nombres de características del encoder ---
    # `encoder.get_feature_names_out()` sin argumentos debería devolver los nombres correctos
    # basados en lo que fue entrenado.
    all_trained_categorical_features = list(encoder.get_feature_names_out()) 
    all_trained_cols = variables_numericas + all_trained_categorical_features
    
    # Preprocesamiento para el Autoencoder (usando los `scaler` y `encoder` entrenados)
    X_numericas_scaled_new = scaler.transform(patient_df[variables_numericas])
    
    # Para el encoder categórico, necesitamos un dataframe para que preserve los nombres de las columnas
    patient_categorical_df = patient_df[variables_categoricas]
    # Asegurarse de que los tipos sean string antes del OneHotEncoder
    for col in patient_categorical_df.columns:
        patient_categorical_df[col] = patient_categorical_df[col].astype(str)

    X_categoricas_encoded_new = encoder.transform(patient_categorical_df).toarray()
    
    X_for_autoencoder_new = np.concatenate([X_numericas_scaled_new, X_categoricas_encoded_new], axis=1)

    # Predecir perfil con el Autoencoder y K-Means entrenados
    encoded_features_new = encoder_model.predict(X_for_autoencoder_new, verbose=0) 
    patient_df['Perfil'] = kmeans.predict(encoded_features_new)

    # Recalcular el Riesgo Cardiovascular basado en los datos del nuevo paciente
    patient_df['Riesgo_Cardiovascular'] = patient_df.apply(calculate_cardiovascular_risk, axis=1)

    # Re-escalar las variables numéricas del nuevo paciente para visualización
    patient_df_rescaled = rescale_to_realistic_range(patient_df.copy(), variables_numericas, realistic_ranges)
    
    # Generar el informe HTML usando la función existente, con los datos ya preprocesados
    report_html, patient_display_id = generate_patient_report_html(patient_data_dict=patient_df_rescaled.iloc[0].to_dict())
    
    return report_html, patient_display_id