In order to run using PyCharm
> clone the project folder
> create a virtual environment using python - python -m venv .venv (or python3 -m venv .venv depending on your python version)
> open the project in PyCharm
> On PyCharm terminal run the requirements installation - pip install -r requirements.txt
> The project needs API keys in order to work
>   Populate "PERPLEXITY_API_KEY" in content_generator.py with your key
>   Create a hidden file named ".env" in the main project folder and add a line:
>     OPENAI_API_KEY="your-openapi-key"
