import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

def get_live_data():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,dogecoin&vs_currencies=usd&include_24hr_change=true"
    return requests.get(url).json()

app.layout = html.Div(
    style={
        "backgroundColor": "#0e1117",
        "minHeight": "100vh",
        "padding": "20px",
        "color": "white",
        "fontFamily": "Segoe UI, sans-serif",
    },
    children=[
        html.H1("💹 CryptoPulse Tracker",
                style={"textAlign": "center", "marginBottom": "30px"}),

        html.Div(
            id="price-cards",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                "gap": "20px",
                "justifyContent": "center",
            },
        ),

        html.Div(
            [
                html.Label("Select cryptocurrency:",
                           style={"fontSize": "18px"}),
                dcc.Dropdown(
                    id="crypto-dropdown",
                    options=[
                        {"label": "Bitcoin (BTC)", "value": "bitcoin"},
                        {"label": "Ethereum (ETH)", "value": "ethereum"},
                        {"label": "Dogecoin (DOGE)", "value": "dogecoin"},
                    ],
                    value="bitcoin",
                    style={"color": "black", "marginBottom": "10px"},
                ),
                html.Label("Select time range:",
                           style={"fontSize": "18px"}),
                dcc.Dropdown(
                    id="days-dropdown",
                    options=[
                        {"label": "1 Day", "value": "1"},
                        {"label": "7 Days", "value": "7"},
                        {"label": "30 Days", "value": "30"},
                    ],
                    value="7",
                    style={"color": "black"},
                ),
            ],
            style={"marginBottom": "30px"},
        ),

        dcc.Graph(id="price-chart", style={"height": "500px"}),
        dcc.Interval(id="update-interval", interval=60 * 1000, n_intervals=0),
    ],
)

@app.callback(
    Output("price-cards", "children"),
    Input("update-interval", "n_intervals")
)
def update_cards(n):
    data = get_live_data()
    cards = []
    for coin, info in data.items():
        price = info["usd"]
        change = info["usd_24h_change"]
        color = "lime" if change >= 0 else "red"

        cards.append(
            html.Div(
                style={
                    "backgroundColor": "#1e2130",
                    "borderRadius": "12px",
                    "padding": "20px",
                    "textAlign": "center",
                    "boxShadow": "0 0 10px rgba(0,0,0,0.6)",
                },
                children=[
                    html.H3(coin.capitalize(), style={"marginBottom": "10px"}),
                    html.H2(f"${price:,.2f}",
                            style={"color": "white", "marginBottom": "5px"}),
                    html.P(f"{change:.2f}% (24h)",
                           style={"color": color, "fontSize": "18px"}),
                ],
            )
        )
    return cards


@app.callback(
    Output("price-chart", "figure"),
    [Input("crypto-dropdown", "value"),
     Input("days-dropdown", "value"),
     Input("update-interval", "n_intervals")]
)
def update_graph(selected_crypto, selected_days, n):
    url = f"https://api.coingecko.com/api/v3/coins/{selected_crypto}/market_chart?vs_currency=usd&days={selected_days}&interval=daily"
    data = requests.get(url).json()

    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["price"],
        mode="lines+markers",
        line=dict(color="#00cc96", width=3),
        marker=dict(size=5),
        name=selected_crypto.capitalize()
    ))

    fig.update_layout(
        title=f"{selected_crypto.capitalize()} Price Trend (Last {selected_days} Days)",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=40),
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white", size=14),
        hovermode="x unified",
    )

    return fig

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8080)
