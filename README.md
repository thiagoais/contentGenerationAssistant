# Project Setup Guide

## Running the Project with PyCharm

1. Clone the project folder
2. Create a virtual environment using Python:
python -m venv .venv
(or `python3 -m venv .venv` depending on your Python version)
3. Open the project in PyCharm
4. In PyCharm's terminal, install the required packages:
pip install -r requirements.txt

## API Key Configuration

The project requires API keys to function properly:

1. In `content_generator.py`, populate the `PERPLEXITY_API_KEY` variable with your key.
2. Create a hidden file named `.env` in the main project folder.
3. Add the following line to the `.env` file:
OPENAI_API_KEY="your-openai-api-key"

Replace `"your-openai-api-key"` with your actual OpenAI API key.
