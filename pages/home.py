import random

import dash_chart_editor as dce
import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, State, callback, dcc, html, no_update, register_page

import utils
from openai_client import openai_client, create_error_notification

df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/solar.csv")


register_page(__name__, path="/")

layout = html.Div(
    [
        utils.jumbotron(),
        dmc.Paper(
            [
                html.Div(
                    [
                        dce.DashChartEditor(
                            id="chart-editor",
                            dataSources=df.to_dict("list"),
                        ),
                        dmc.Affix(
                            dmc.Button("Save this chart", id="add-to-layout"),
                            position={"bottom": 20, "left": 20},
                        ),
                    ],
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Img(
                                    src="/assets/chat-gpt.png",
                                    height="28px",
                                    style={"marginRight": "1px"}
                                ),
                                html.P("Ask OpenAI", className="lead", style={"margin": 0}),
                                html.Span(
                                    "gpt-4o-mini",
                                    style={
                                        "background": "#edf1f2",
                                        "color": "#333",
                                        "borderRadius": "12px",
                                        "padding": "2px 10px",
                                        "fontSize": "0.85rem",
                                        "marginLeft": "auto",
                                        "fontWeight": 200,
                                        "letterSpacing": "0.02em",
                                        "alignSelf": "center"
                                    }
                                ),
                            ],
                            style={"display": "flex", "alignItems": "center", "marginBottom": "8px", "gap": "0.5rem"}
                        ),
                        dmc.Textarea(
                            placeholder=random.choice(
                                [
                                    '"Are there any outliers in this dataset?"',
                                    '"What trends do you see in this dataset?"',
                                    '"Anything stand out about this dataset?"',
                                    '"Do you recommend specific charts given this dataset?"',
                                    '"What columns should I investigate further?"',
                                ]
                            ),
                            autosize=True,
                            minRows=2,
                            id="question",
                        ),
                        dmc.Group(
                            [
                                dmc.Button(
                                    "Submit",
                                    id="chat-submit",
                                    disabled=True,
                                ),
                            ],
                            position="right",
                        ),
                        dmc.LoadingOverlay(
                            html.Div(
                                id="chat-output",
                            ),
                        ),
                    ],
                    id="chat-container",
                ),
            ],
            shadow="xs",
            id="flex",
        ),
        utils.upload_modal(),
        html.Div(id="current-charts"),
        html.Div(
            html.A(
                "Chat gpt icons created by Freepik - Flaticon",
                href="https://www.flaticon.com/free-icons/chat-gpt",
                title="chat gpt icons",
                target="_blank",
                style={"fontSize": "0.9rem", "color": "#888", "textAlign": "center", "display": "block", "marginTop": "40px"}
            )
        ),
    ],
    id="padded",
)


@callback(
    Output("chat-output", "children"),
    Output("question", "value"),
    Input("chat-submit", "n_clicks"),
    State("chart-editor", "dataSources"),
    State("question", "value"),
    State("chat-output", "children"),
    prevent_initial_call=True,
)
def chat_window(n_clicks, data, question, cur):
    df = pd.DataFrame(data)
    prompt = utils.generate_prompt(df, question)
    
    # Generate fallback info for error cases
    fallback_info = f"Dataset has {len(df)} rows and {len(df.columns)} columns. Columns: {', '.join(df.columns)}"
    
    # Use the safe chat completion with error handling
    response = openai_client.safe_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-4o-mini",
        fallback_info=fallback_info,
        question=question
    )

    # Check if response contains error indicators
    if "⚠️" in response or "API" in response or "quota" in response.lower():
        # Show error notification
        error_notification = create_error_notification(response)
        question_response = [
            error_notification,
            dcc.Markdown(question, className="chat-item question"),
        ]
    else:
        # Normal response
        question_response = [
            dcc.Markdown(response, className="chat-item answer"),
            dcc.Markdown(question, className="chat-item question"),
        ]

    return (question_response + cur if cur else question_response), None


@callback(
    Output("chart-editor", "saveState"),
    Input("add-to-layout", "n_clicks"),
    prevent_initial_call=True,
)
def save_figure_to_chart_editor(n):
    if n:
        return True


@callback(
    Output("current-charts", "children"),
    Input("add-to-layout", "n_clicks"),
    State("chart-editor", "figure"),
    State("current-charts", "children"),
    prevent_initial_call=True,
)
def save_figure(n_clicks, figure, cur):

    if not figure:
        return no_update
    
    data = figure.get("data", []) if isinstance(figure, dict) else getattr(figure, "data", [])
    if not data:
        return no_update
    
    def _has_points(trace):
        # works for bar/scatter/line/area, heatmap, pie, etc.
        if isinstance(trace, dict):
            x, y, z, vals = trace.get("x"), trace.get("y"), trace.get("z"), trace.get("values")
        else:
            x, y, z, vals = getattr(trace, "x", None), getattr(trace, "y", None), getattr(trace, "z", None), getattr(trace, "values", None)
        candidates = [x, y, z, vals]
        return any(
            (isinstance(c, (list, tuple)) and len(c) > 0) or getattr(c, "size", 0) > 0
            for c in candidates if c is not None
        )

    if not any(_has_points(t) for t in data):
        return no_update

    item = [dmc.Paper([dcc.Graph(figure=figure)])]

    header = [
        html.Div(
            [
                html.H2("Saved figures"),
                dcc.Clipboard(
                    id="save-clip",
                    title="Copy link",
                    style={"margin-left": "10px"},
                ),
            ],
            style={"display": "flex"},
        )
    ]
    return cur + item if cur else header + item
