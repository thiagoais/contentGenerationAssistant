import time
import requests
import openai
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants for API Keys and OpenAI Assistants
PERPLEXITY_API_KEY = "pplx-YOUR_API_KEY"

# OpenAI Assistant IDs for Social Media Platforms
ASSISTANT_IDS = {
    "twitter": "asst_DJcbGlXUa1M0Vr5gfpt6mTbZ",
    "linkedin": "asst_SJLLPvjXKgBeBEyllKK6sPTS",
    "instagram": "asst_HkwV4kP6lF6utTeGunb6Zklt",
    "facebook": "asst_HUUDvFV5XQxPLtEMoDLSvSkq"
}

# Function to get article summary using Perplexity Chat Completion API
def summarize_article(url: str, model: str = "pplx-7b-online") -> str:
    """
    Summarizes an article using Perplexity's Chat Completion API.

    Args:
        url (str): URL of the article.
        model (str): The Perplexity model name (e.g., pplx-7b-online).

    Returns:
        str: The summarized content.
    """
    try:
        endpoint = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that summarizes articles."},
                {"role": "user", "content": f"Summarize the following article: {url}"}
            ],
            "max_tokens": 300,
            "temperature": 0.2
        }

        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        # Parse the response to extract the summary
        summary = data["choices"][0]["message"]["content"].strip()
        return summary

    except requests.RequestException as e:
        print(f"Error with Perplexity API: {e}")
        raise
    except (KeyError, IndexError) as e:
        print(f"Unexpected Perplexity response format: {e}")
        raise

def summarize_text(input_text: str, model: str = "pplx-7b-online") -> str:
    """
    Summarizes custom text using Perplexity's Chat Completion API.

    Args:
        input_text (str): The text to summarize.
        model (str): The Perplexity model name (e.g., pplx-7b-online).

    Returns:
        str: The summarized content.
    """
    try:
        endpoint = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Summarize the following text: {input_text}"}
            ],
            "max_tokens": 300,
            "temperature": 0.2
        }

        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        # Parse the response to extract the summary
        summary = data["choices"][0]["message"]["content"].strip()
        return summary

    except requests.RequestException as e:
        print(f"Error with Perplexity API: {e}")
        raise
    except (KeyError, IndexError) as e:
        print(f"Unexpected Perplexity response format: {e}")
        raise


# Updated function to use the correct OpenAI chat API (openai.ChatCompletion -> openai.ChatCompletion.create)
def generate_post_with_new_api(summary: str, platform: str) -> str:
    """
    Uses OpenAI Assistant to generate social media posts.

    Args:
        summary (str): The article summary.
        platform (str): Social media platform (e.g., twitter, linkedin).

    Returns:
        str: Generated social media post.
    """
    try:
        # Check for the assistant ID for the platform
        assistant_id = ASSISTANT_IDS.get(platform)
        if not assistant_id:
            raise ValueError(f"No Assistant ID configured for platform: {platform}")

        # Initialize OpenAI client
        openai.api_key = "your-api-key-here"  # Ensure the API key is set

        # Initialize OpenAI Client (assuming the `openai` package is already configured)
        client = openai.Client()

        # Step 1: Create an Assistant
        try:
            assistant = client.beta.assistants.retrieve(assistant_id)
        except openai.error.OpenAIError as e:
            logger.error(f"Error retrieving assistant: {e}")
            raise

        # Step 2: Create a Thread
        try:
            thread = client.beta.threads.create()
        except openai.error.OpenAIError as e:
            logger.error(f"Error creating thread: {e}")
            raise

        # Step 3: Add a Message to a Thread
        try:
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=summary
            )
        except openai.error.OpenAIError as e:
            logger.error(f"Error adding message to thread: {e}")
            raise

        # Step 4: Run the Assistant
        try:
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )
        except openai.error.OpenAIError as e:
            logger.error(f"Error running the assistant: {e}")
            raise

        # Step 5: Poll for the run status until completed or failed
        while True:
            try:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status == "failed":
                    logger.error(f"Run failed: {run_status.last_error}")
                    return "Error: Run failed."
                time.sleep(2)  # Wait before checking again
            except openai.error.OpenAIError as e:
                logger.error(f"Error retrieving run status: {e}")
                return "Error: Unable to retrieve run status."
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error: {e}")
                return "Error: Network issue during run."

        # Step 6: Parse the Assistant's response
        try:
            messages = client.beta.threads.messages.list(thread_id=thread.id)
        except openai.error.OpenAIError as e:
            logger.error(f"Error retrieving messages: {e}")
            raise

        # Look for the assistant's response and return it
        response = None
        for message in reversed(messages.data):
            if message.role == 'assistant':
                for content in message.content:
                    if content.type == 'text':
                        response = content.text.value
                        break
            if response:
                break

        if response:
            return response
        else:
            logger.error("No assistant response found.")
            return "Error: No response from assistant."

    except ValueError as e:
        logger.error(f"ValueError: {e}")
        return str(e)
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return "Error: OpenAI API issue."
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {e}")
        return "Error: Network issue."
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return "Error: An unexpected error occurred."


# Main function
def main():
    """
    Main workflow: summarize the article and generate posts for different platforms.
    """
    print("\n--- Article to Social Media Post Generator ---\n")
    input_type = input("Is the source 1-URL or 2-TEXT?").strip()

    try:
        if input_type == 0:
            article_url = input("Enter the article URL: ").strip()
            #model = input("Enter the Perplexity model to use (default: pplx-7b-online): ").strip() or "pplx-7b-online"
            #model = input("Enter the Perplexity model to use (default or custom): ").strip() or "default"
            model = 'llama-3.1-sonar-small-128k-online'

            # Summarize the article
            print("\nSummarizing the article...\n")
            summary = summarize_article(article_url, model)
        else:
            model = 'llama-3.1-sonar-small-128k-online'
            # Summarize the text
            article_url = input("Enter the text: ").strip()
            print("\nSummarizing the text...\n")
            summary = summarize_text(article_url, model)

        print("Article Summary:\n", summary)

        # Generate posts for platforms
        posts = {}
        for platform in ASSISTANT_IDS.keys():
            print(f"\nGenerating post for {platform.capitalize()}...")
            posts[platform] = generate_post_with_new_api(summary, platform)
            print(f"{platform.capitalize()} Post:\n{posts[platform]}\n")

        # Display all posts
        print("\n--- Final Posts ---\n")
        for platform, post in posts.items():
            print(f"{platform.capitalize()}:\n{post}\n{'-' * 40}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()