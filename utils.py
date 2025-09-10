import base64
import io
import os

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, State, callback, dcc, html


def chat_container(text, type_):
    return html.Div(text, id="chat-item", className=type_)


def navbar():
    logo_path = os.path.join('assets', 'United Fintech_id-LRcwe1b_5.png')
    return dbc.Navbar(
        dbc.Container([
            html.Div([
                html.Img(src="/assets/United Fintech_id-LRcwe1b_5.png", height="40px"),
            ], style={"flex": "0 0 auto", "display": "flex", "alignItems": "center"}),
            html.Div(
                html.H6([
                    html.B("DOLFIN"),
                    " | AI financial insights"
                ],
                    style={
                        "color": "white",
                        "margin": 0,
                        "fontWeight": 300,
                        "fontSize": "1.2rem",
                        "textAlign": "center",
                    },
                ),
                style={
                    "flex": "1 1 auto",
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                },
            ),
            html.Div([], style={"flex": "0 0 40px"}),  # Spacer for symmetry
        ], fluid=True, style={"display": "flex", "alignItems": "center"}),
        color="#211E32",
        dark=True,
        className="",
        style={
            "backgroundColor": "#211E32",
            "background": "linear-gradient(90deg, #211E32 0%, #26233B 50%, #1B192C 100%)",
            "padding": "0.5rem 0",
            "marginBottom": 0,
            "boxShadow": "inset 0 -1px 0 rgba(255,255,255,0.04)",  # tiny bottom separator
        },
    )


def mini_navbar_note():
    return html.Div(
        [
            html.Span([
                "Note: Only upload ",
                html.B("mock data"),
                " as Dolfin is currently using a public OpenAI API key for development & testing purposes, but we will switch to UF's private OpenAI API key soon"
            ])
        ],
        style={
            "background": "#dae2f5",
            "color": "black",
            "padding": "0.4rem 1rem",
            "fontSize": "0.95rem",
            "fontWeight": 400,
            "width": "100%",
            "position": "sticky",
            "top": 0,
            "zIndex": 1001,
            "textAlign": "center",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.03)",
            "marginTop": 0
        }
    )


def jumbotron():
    return html.Div(
        dbc.Container(
            [
                # Title moved to navbar
                dcc.Markdown(
                    "Uses [Dash Chart Editor](https://github.com/BSd3v/dash-chart-editor)"
                    " and [OpenAI's API](https://platform.openai.com/docs/api-reference) to interact in real-time with "
                    "a dataset by asking questions about its contents.",
                    className="lead",
                    style={"fontSize": "1rem"},
                ),
                html.Hr(className="my-2"),
                html.P(
                    "Start using the application by interacting with the sample dataset, or upload your own."
                ),
                html.P(
                    [
                        dbc.Button(
                            "Learn more",
                            style={"background-color": "#238BE6"},
                            href="https://plotly.com/examples/generative-ai-chatgpt/",
                        ),
                        dbc.Button(
                            "Upload your own CSV",
                            id="modal-demo-button",
                            style={
                                "background-color": "#238BE6",
                                "margin-left": "10px",
                            },
                        ),
                    ],
                    className="lead",
                    style={"display": "flex"},
                ),
            ],
            fluid=True,
            className="py-3",
        ),
        className="bg-light rounded-3",
    )


def upload_modal():
    return html.Div(
        [
            dmc.Modal(
                title="Upload Modal",
                id="upload-modal",
                size="lg",
                zIndex=10000,
                children=[
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div(
                            ["Drag and Drop or ", html.A("Select Files")]
                        ),
                        style={
                            "width": "100%",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "margin": "10px",
                            "font-family": "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial,"
                            " sans-serif, Apple Color Emoji, Segoe UI Emoji",
                        },
                        # Allow multiple files to be uploaded
                        multiple=False,
                    ),
                    dmc.Space(h=20),
                    html.Div(id="summary"),
                    dmc.Group(
                        [
                            dmc.Button(
                                "Close",
                                color="red",
                                variant="outline",
                                id="modal-close-button",
                            ),
                        ],
                        position="right",
                    ),
                ],
            ),
        ]
    )


def generate_prompt(df, question):
    # Generate insights
    insights = []

    # Basic DataFrame Information
    insights.append(
        f"The DataFrame contains {len(df)} rows and {len(df.columns)} columns."
    )
    insights.append("Here are the first 5 rows of the DataFrame:\n")
    insights.append(df.head().to_string(index=False))

    # Summary Statistics
    insights.append("\nSummary Statistics:")
    insights.append(df.describe().to_string())

    # Column Information
    insights.append("\nColumn Information:")
    for col in df.columns:
        insights.append(f"- Column '{col}' has {df[col].nunique()} unique values.")

    # Missing Values
    missing_values = df.isnull().sum()
    insights.append("\nMissing Values:")
    for col, count in missing_values.items():
        if count > 0:
            insights.append(f"- Column '{col}' has {count} missing values.")

    # Most Common Values in Categorical Columns
    categorical_columns = df.select_dtypes(include=["object"]).columns
    for col in categorical_columns:
        top_value = df[col].mode().iloc[0]
        insights.append(f"\nMost common value in '{col}' column: {top_value}")

    insights_text = "\n".join(insights)

    # Compliment and Prompt
    prompt = (
        "You are a data analyst and chart design expert helping users build charts and answer "
        "questions about arbitrary datasets. The user's question will be provided. Ensure you "
        "answer the user's question accurately and given the context of the dataset. The user "
        "will use the results of your commentary to work on a chart or to research the data "
        "using Dash Chart Editor, a product built by Plotly. If the user's question doesn't "
        " make sense, feel free to make a witty remark about Plotly and Dash. Your response "
        "should use Markdown markup. Limit your response to only 1-3 sentences. Address the "
        "user directly as they can see your response."
    )

    prompt = f"{prompt}\n\nContext:\n\n{insights_text}\n\nUser's Question: {question}"

    return prompt


@callback(
    Output("chart-editor", "dataSources"),
    Output("summary", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def update_output(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))

    preview = html.Div(
        [
            html.H5(filename),
            dag.AgGrid(
                rowData=df.to_dict("records"),
                columnDefs=[{"field": i} for i in df.columns],
                defaultColDef={"sortable": True, "resizable": True, "editable": True},
            ),
        ]
    )

    return df.to_dict("list"), preview


@callback(
    Output("upload-modal", "opened"),
    Input("modal-demo-button", "n_clicks"),
    Input("modal-close-button", "n_clicks"),
    State("upload-modal", "opened"),
    prevent_initial_call=True,
)
def modal_demo(nc1, nc2, opened):
    return not opened


@callback(Output("chat-submit", "disabled"), Input("question", "value"))
def disable_submit(question):
    return not bool(question)
