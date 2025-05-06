import dash
from dash import dcc, html, dash_table, Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv("outputs/segmented_users.csv")

app = dash.Dash(__name__)

# KPI'lar
def kpi_card(title, value, color="#2a9d8f"):
    return html.Div([
        html.H4(title, style={"margin-bottom": "0", "color": color}),
        html.H2(f"{value:,}", style={"margin-top": "0"})
    ], style={"display": "inline-block", "margin": "20px", "padding": "20px", "background": "#f4f4f4", "border-radius": "10px", "box-shadow": "2px 2px 8px #ddd"})

segment_counts = df['segment'].value_counts()
total_users = len(df)
high_value = segment_counts.get("High Value", 0)
churn_risk = segment_counts.get("Churn Risk", 0)
growth_pot = segment_counts.get("Growth Potential", 0)

# Pie chart
fig_pie = px.pie(segment_counts.reset_index(), names="segment", values="count", title="Segment Dağılımı")

# Churn histogram (segmentlere göre renkli)
fig_churn = px.histogram(df, x="pred_churn", color="segment", barmode="overlay", nbins=10, title="Churn Tahmini Dağılımı")

# Dropdown filtreler
segment_options = [{"label": s, "value": s} for s in df["segment"].unique()]
country_options = [{"label": c, "value": c} for c in df["country"].unique()] if "country" in df.columns else []

app.layout = html.Div([
    html.H1("Kullanıcı Segmentasyonu Dashboard", style={"textAlign": "center"}),
    html.Div([
        kpi_card("Toplam Kullanıcı", total_users, "#264653"),
        kpi_card("High Value", high_value, "#2a9d8f"),
        kpi_card("Churn Risk", churn_risk, "#e76f51"),
        kpi_card("Growth Potential", growth_pot, "#f4a261")
    ], style={"textAlign": "center"}),
    html.Div([
        html.Div([
            dcc.Graph(figure=fig_pie)
        ], style={"width": "45%", "display": "inline-block"}),
        html.Div([
            dcc.Graph(figure=fig_churn)
        ], style={"width": "54%", "display": "inline-block"})
    ]),
    html.Hr(),
    html.Div([
        html.Label("Segment Filtrele:"),
        dcc.Dropdown(options=segment_options, value=segment_options[0]["value"], id="segment-filter", style={"width": "300px", "display": "inline-block"}),
        html.Label("  Ülke Filtrele:", style={"margin-left": "30px"}),
        dcc.Dropdown(options=country_options, id="country-filter", style={"width": "300px", "display": "inline-block"}) if country_options else html.Span()
    ], style={"margin": "20px"}),
    html.Div(id="filtered-table")
])

@app.callback(
    Output("filtered-table", "children"),
    Input("segment-filter", "value"),
    Input("country-filter", "value") if country_options else Input("segment-filter", "value")
)
def update_table(segment, country=None):
    dff = df[df["segment"] == segment]
    if country and "country" in df.columns:
        dff = dff[dff["country"] == country]
    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in dff.columns],
        data=dff.head(100).to_dict("records"),
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left"},
        style_header={"backgroundColor": "#f4f4f4", "fontWeight": "bold"}
    )

if __name__ == "__main__":
    app.run(debug=True)
