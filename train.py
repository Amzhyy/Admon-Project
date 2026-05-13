import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# 1. Carga de datos
df = pd.read_csv('phishing_dataset.csv')

# 2. Selección de Variables
# X: Factores que influyen
# y: Lo que queremos predecir
X = df[['attack_type_id', 'clics_previos_usuario', 'duracion_dias_campana', 'rol_usuario_id']]
y = df['label_resultado_cayo']

# 3. División de datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Creación y Entrenamiento del modelo
modelo = LogisticRegression()
modelo.fit(X_train, y_train)

# 5. Evaluación del modelo
y_pred = modelo.predict(X_test)
precision = accuracy_score(y_test, y_pred)

print(f"--- RESULTADOS DEL MODELO ---")
print(f"Precisión del modelo: {precision * 100:.2f}%")
print("\nMatriz de Confusión:")
print(confusion_matrix(y_test, y_pred))
print("\nReporte de Clasificación:")
print(classification_report(y_test, y_pred))

#  EJEMPLO DE PREDICCIÓN REAL
# Supongamos un nuevo usuario:
# Ataque: Urgencia (1), Clicks previos: 5, Duración: 3 días, Rol: Analista (2)
nuevo_usuario = np.array([[1, 5, 3, 2]])
probabilidad = modelo.predict_proba(nuevo_usuario)[0][1] # Probabilidad de caer (clase 1)

print(f"\n--- SIMULACIÓN DE PREDICCIÓN ---")
print(f"Probabilidad de que este usuario CAIGA en el phishing: {probabilidad * 100:.2f}%")

# 7. Visualización de la curva Logística
plt.figure(figsize=(8, 5))
plt.scatter(df['clics_previos_usuario'], df['label_resultado_cayo'], alpha=0.3, label='Datos Reales')

# Crear una línea de probabilidad suave
x_range = np.linspace(df['clics_previos_usuario'].min(), df['clics_previos_usuario'].max(), 300).reshape(-1, 1)
# Para graficar, fijamos las otras variables al promedio
x_plot = pd.DataFrame({
    'attack_type_id': [1]*300,
    'clics_previos_usuario': x_range.flatten(),
    'duracion_dias_campana': [7]*300,
    'rol_usuario_id': [2]*300
})
prob_plot = modelo.predict_proba(x_plot)[:, 1]

plt.plot(x_range, prob_plot, color='red', linewidth=3, label='Curva de Probabilidad')
plt.title('Probabilidad de Caída según Clics Previos')
plt.xlabel('Número de Clics Previos')
plt.ylabel('Probabilidad (0 a 1)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()
import pickle

# Guardar modelo
with open('modelo_phishing.pkl', 'wb') as f:
    pickle.dump(modelo, f)

print("Modelo guardado correctamente")