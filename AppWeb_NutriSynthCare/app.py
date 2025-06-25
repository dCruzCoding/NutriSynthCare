from flask import Flask, render_template, request, redirect, url_for
# Importa la función de generación de informe desde core_functions.py
# También necesitarás importar las nuevas funciones que crearemos en core_functions.py
from core_funtions import generate_patient_report_html, process_new_patient_data, initialize_models # <--- NUEVAS IMPORTACIONES
import os 

app = Flask(__name__) 

# Verifica si la carpeta 'templates' existe al inicio
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
if not os.path.exists(template_dir):
    print(f"ERROR: La carpeta 'templates' no se encontró en {template_dir}")
    print("Asegúrate de que tus archivos HTML (index.html, report.html) estén dentro de una carpeta 'templates' en el mismo directorio que app.py.")
    exit() 

# --- Inicializa los modelos de ML una única vez al inicio del servidor ---
# Esta función estará en core_functions.py y cargará/entrenará todo lo necesario
# para que esté disponible globalmente.
try:
    print("Inicializando modelos de IA...")
    initialize_models()
    print("Modelos de IA inicializados.")
except Exception as e:
    print(f"Error al inicializar modelos de IA: {e}")
    exit() # Salir si los modelos no se cargan

@app.route('/')
def index():
    return render_template('index.html')

# --- ESTA RUTA DE /create_new_patient YA NO ES NECESARIA con el nuevo index.html ---
# Porque la creación de pacientes está ahora en el mismo index.html.
# Si la quitas, asegúrate de que no haya enlaces internos que apunten a ella.
# @app.route('/create_new_patient')
# def create_new_patient():
#    return render_template('create_patient.html') # Renderiza el nuevo formulario


# --- RUTA EXISTENTE: Generar informe para paciente existente (por ID) ---
@app.route('/report', methods=['GET', 'POST'])
def report():
    patient_id = None
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
    elif request.method == 'GET' and 'patient_id' in request.args:
        patient_id = request.args.get('patient_id')

    if patient_id:
        report_content, patient_display_id = generate_patient_report_html(patient_id=patient_id) # generate_patient_report_html ahora devuelve 2 valores
        return render_template('report.html', patient_id=patient_display_id, report_content=report_content) # Usa patient_display_id
    else:
        return redirect(url_for('index'))

# --- RUTA CORRECTA PARA PROCESAR DATOS DEL NUEVO PACIENTE (la única que debe existir) ---
@app.route('/process_new_patient', methods=['POST'])
def process_new_patient():
    # Recoge los datos del formulario
    patient_data = {
        'Sexo': request.form.get('sexo'),
        'Edad': request.form.get('edad'),
        'peso': request.form.get('peso'),
        'altura': request.form.get('altura'),
        'IMC': request.form.get('imc'), # Viene del campo oculto
        'Nivel_Estres': request.form.get('nivel_estres'),
        'Diabetes': request.form.get('diabetes'),
        'Actividad_Fisica': request.form.get('actividad_fisica')
    }

    # --- ESTA LÍNEA DE DEPURACIÓN ES LA QUE NECESITAMOS VER EN EL TERMINAL ---
    print(f"Datos recibidos del formulario: {patient_data}")
    # --- FIN DE LÍNEA DE DEPURACIÓN ---

    try:
        report_content, patient_display_id = process_new_patient_data(patient_data)
        return render_template('report.html', patient_id=patient_display_id, report_content=report_content)
    except Exception as e:
        # Asegúrate de que el error completo se imprima en la consola para más detalles
        print(f"ERROR EN process_new_patient: {e}")
        import traceback # Agregado para imprimir el stack trace completo
        traceback.print_exc() 
        return render_template('report.html', patient_id="Error", report_content=f"<p>Hubo un error al procesar los datos del nuevo paciente: {e}</p><p>Asegúrate de que todos los campos sean válidos.</p>")


if __name__ == '__main__':
    app.run(debug=True)