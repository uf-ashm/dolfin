import json
import pickle

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import dcc, html

from constants import redis_instance
from openai_client import openai_client, create_error_notification

dash.register_page(__name__)


def layout(layout=None):
    layout = redis_instance.get(layout)
    layout = pickle.loads(layout)

    figures = [i["props"]["children"][0]["props"]["figure"] for i in layout[1:]]

    question = (
        "The following is a Plotly Dash layout with several charts. Summarize "
        "the charts for me and provide some maximums, mimumuns, trends, "
        "notable outliers, etc. Describe the data and content as the user doesn't know it's a layout."
        "The data may be truncated to comply with a max character count. "
        f"There should be {len(figures)} charts to follow:\n\n\n"
    )

    # Generate fallback info
    fallback_info = f"Layout contains {len(figures)} charts. Chart data has been processed and is ready for analysis."
    
    # Use safe chat completion with error handling
    response_content = openai_client.safe_chat_completion(
        messages=[{"role": "user", "content": question + json.dumps(figures)[0:3900]}],
        model="gpt-4o-mini",
        fallback_info=fallback_info,
        question="Summarize the charts and provide insights"
    )

    # Check if response contains error indicators
    if "⚠️" in response_content or "API" in response_content or "quota" in response_content.lower():
        # Show error notification and fallback response
        response = html.Div([
            create_error_notification(response_content),
            dcc.Markdown(
                f"**Basic Chart Summary** (AI service unavailable)\n\n"
                f"This layout contains {len(figures)} interactive charts. "
                f"Each chart has been processed and is ready for analysis. "
                f"For detailed AI-powered insights, please ensure your OpenAI API key is valid and has sufficient quota.",
                className="chat-item answer"
            )
        ])
    else:
        response = dcc.Markdown(response_content)

    return dmc.LoadingOverlay(
        [
            dbc.Button(
                children="Home",
                href="/",
                style={"background-color": "#238BE6", "margin": "10px"},
            ),
            html.Div([response, html.Div(layout[1:])], style={"padding": "40px"}),
        ]
    )
