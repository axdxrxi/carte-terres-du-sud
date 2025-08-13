import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go

# Charger les fichiers CSV
file_paths = {
    "Site 1": "./export_23-07-2025--15-46.csv",
    "Site 2": "./export_23-07-2025--16-06.csv"
}

def load_data(filepath):
    try:
        df = pd.read_csv(filepath, sep=';', encoding='utf-8')
        df.columns = [col.strip() for col in df.columns]
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        return df
    except Exception as e:
        print(f"Erreur lors du chargement de {filepath}: {e}")
        return pd.DataFrame()

datasets = {name: load_data(path) for name, path in file_paths.items()}

# Lancer l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Consommation Énergie"

app.layout = dbc.Container([
    html.H1("Tableau de bord des consommations énergétiques", className="text-center mt-4 mb-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Sélection du site :"),
            dcc.Dropdown(
                id='site-dropdown',
                options=[{'label': k, 'value': k} for k in datasets.keys()],
                value=list(datasets.keys())[0],
                clearable=False
            )
        ], width=4)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='electricity-graph')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='gas-graph')
        ], width=6)
    ])
], fluid=True)

@app.callback(
    Output('electricity-graph', 'figure'),
    Output('gas-graph', 'figure'),
    Input('site-dropdown', 'value')
)
def update_graphs(site_name):
    df = datasets[site_name]

    fig_elec = go.Figure()
    if 'Electricité (réel)' in df.columns:
        fig_elec.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Electricité (réel)'],
            mode='lines+markers',
            name='Électricité (réel)'
        ))
    if 'Electricité (estimé)' in df.columns:
        fig_elec.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Electricité (estimé)'],
            mode='lines',
            name='Électricité (estimé)',
            line=dict(dash='dot')
        ))
    fig_elec.update_layout(title="Consommation Électricité", xaxis_title="Date", yaxis_title="kWh")

    fig_gas = go.Figure()
    if 'Gaz (réel)' in df.columns:
        fig_gas.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Gaz (réel)'],
            mode='lines+markers',
            name='Gaz (réel)'
        ))
    if 'Gaz (estimé)' in df.columns:
        fig_gas.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Gaz (estimé)'],
            mode='lines',
            name='Gaz (estimé)',
            line=dict(dash='dot')
        ))
    fig_gas.update_layout(title="Consommation Gaz", xaxis_title="Date", yaxis_title="kWh")

    return fig_elec, fig_gas

if __name__ == '__main__':
    app.run(debug=True)
