This application uses [Dash Chart Editor](https://github.com/BSd3v/dash-chart-editor)

<p align="center">
  finbot -> dolfin : AI-powered financial analysis tool for YTD excel workbooks
</p>

Once a dataset is uploaded, context on that dataset is added to the prompt for the chat window, and users can interact with the dataset with natural language. After building charts, users can click the "Copy link" button to save those charts to a permanent link, using Redis to save state.


## Usage
> Note: You must provide an [OpenAI API key](https://platform.openai.com/account/api-keys) as an environment variable at `$OPEN_AI_KEY`.

Install the dependencies with:
```
pip install -r requirements.txt
```

And run the application with:
```
python app.py
```

Or, provide your API key directly if it is not in your environment:
```
OPEN_AI_KEY=... python app.py
```
