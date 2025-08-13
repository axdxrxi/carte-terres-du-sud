from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import io

app = Flask(__name__)

def interpret_energy_data(df):
    """
    Simulate AI interpretation of energy consumption data.
    This function analyzes the data and returns insights as text.
    """
    insights = []
    if 'consumption' not in df.columns:
        return "Le fichier ne contient pas de colonne 'consumption'. Veuillez vérifier les données."

    total_consumption = df['consumption'].sum()
    avg_consumption = df['consumption'].mean()
    max_consumption = df['consumption'].max()
    min_consumption = df['consumption'].min()

    insights.append(f"Consommation totale: {total_consumption:.2f} kWh.")
    insights.append(f"Consommation moyenne: {avg_consumption:.2f} kWh.")
    insights.append(f"Consommation maximale: {max_consumption:.2f} kWh.")
    insights.append(f"Consommation minimale: {min_consumption:.2f} kWh.")

    # Simple interpretation
    if avg_consumption > 100:
        insights.append("La consommation moyenne est élevée, il serait utile d'examiner les appareils énergivores.")
    else:
        insights.append("La consommation moyenne est raisonnable.")

    # Detect anomalies (simple)
    anomalies = df[df['consumption'] > avg_consumption * 1.5]
    if not anomalies.empty:
        insights.append(f"Attention: {len(anomalies)} point(s) de consommation anormale détecté(s).")

    return " ".join(insights)

@app.route('/', methods=['GET', 'POST'])
def index():
    interpretation = None
    data_preview = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            try:
                content = file.read()
                df = pd.read_csv(io.StringIO(content.decode('utf-8')))
                data_preview = df.head().to_html(classes='table table-striped')
                interpretation = interpret_energy_data(df)
            except Exception as e:
                interpretation = f"Erreur lors du traitement du fichier: {str(e)}"
        else:
            interpretation = "Aucun fichier téléchargé."

    return render_template('index.html', interpretation=interpretation, data_preview=data_preview)

if __name__ == '__main__':
    app.run(debug=True)
