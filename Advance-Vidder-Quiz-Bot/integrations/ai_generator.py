# Powered by Viddertech

import logging
import json
import openai
import config

logger = logging.getLogger(__name__)

async def generate_quiz_from_text_content(text_content: str, num_questions: int) -> dict | None:
    """
    Uses OpenAI API to generate a quiz from a large block of text.

    :param text_content: The text scraped from an article or extracted from a document.
    :param num_questions: The number of questions to generate.
    :return: The structured quiz data as a dictionary, or None on failure.
    """
    if not config.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is not configured.")
        raise Exception("AI features are not configured by the bot owner.")

    openai.api_key = config.OPENAI_API_KEY

    # Truncate text to avoid exceeding token limits, focusing on the most relevant part.
    max_chars = 12000 # Roughly 3000 tokens, leaving room for prompt and response.
    truncated_text = text_content[:max_chars]

    prompt = f"""
    Based on the following text, create a quiz with exactly {num_questions} questions.
    The quiz must have a creative and relevant title based on the text's content.
    Each question must have between 3 and 5 options.
    One option must be correct.

    Provide the output in a single, minified JSON object with no markdown formatting or other text.
    The JSON object must follow this exact structure:
    {{
      "title": "A Creative Title Based on the Text",
      "questions": [
        {{
          "text": "Question 1 text?",
          "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
          "correct": 0
        }},
        {{
          "text": "Question 2 text?",
          "options": ["Option A", "Option B", "Option C"],
          "correct": 2
        }}
      ]
    }}
    The 'correct' field is the 0-based index of the correct option in the 'options' array.

    Here is the text to analyze:
    ---
    {truncated_text}
    ---
    """

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        quiz_json_str = response.choices[0].message['content']

        # Clean the response in case the AI adds markdown backticks
        if quiz_json_str.startswith("```json"):
            quiz_json_str = quiz_json_str[7:-4]

        quiz_data = json.loads(quiz_json_str)

        # Basic validation
        if 'title' in quiz_data and 'questions' in quiz_data and isinstance(quiz_data['questions'], list):
            logger.info(f"Successfully generated quiz '{quiz_data['title']}' from text content.")
            return quiz_data
        else:
            logger.error(f"AI response is missing required fields: {quiz_json_str}")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from AI response: {e}\nResponse was:\n{quiz_json_str}")
        return None
    except Exception as e:
        logger.error(f"Error generating quiz from AI: {e}")
        return None