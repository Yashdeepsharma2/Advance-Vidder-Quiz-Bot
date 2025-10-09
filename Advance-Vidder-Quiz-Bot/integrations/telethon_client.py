# Powered by Viddertech

import logging
import asyncio
from telethon import TelegramClient, events, types
from telethon.errors.rpcerrorlist import SessionPasswordNeededError
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

import config

logger = logging.getLogger(__name__)

class VidderTelethonClient:
    """
    A class to manage the Telethon client for user-account interactions like cloning.
    """
    def __init__(self):
        self.client = TelegramClient(
            config.TELETHON_SESSION_PATH,
            config.TELEGRAM_API_ID,
            config.TELEGRAM_API_HASH
        )

    async def clone_quiz_from_bot(self, link: str) -> dict:
        """
        Connects, performs a full conversation with QuizBot to clone a quiz,
        and returns the structured quiz data.
        """
        cloned_quiz_data = {'title': f"Cloned from {link.split('/')[-1]}", 'questions': []}

        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                raise Exception("User account is not logged in. Please use /telelogin first.")

            quiz_bot_entity = await self.client.get_entity('QuizBot')

            async with self.client.conversation(quiz_bot_entity, timeout=300) as conv:
                await conv.send_message(f"/start {link.split('=')[-1]}")

                # Initial message, often contains "I'm ready" button
                initial_response = await conv.get_response()
                if initial_response.reply_markup:
                    # Click the "I'm ready!" or similar button
                    button = initial_response.reply_markup.rows[0].buttons[0]
                    await self.client(GetBotCallbackAnswerRequest(
                        peer=quiz_bot_entity,
                        msg_id=initial_response.id,
                        data=button.data
                    ))

                while True:
                    try:
                        # The poll message
                        poll_response = await conv.get_response(timeout=30)

                        if "That's all!" in poll_response.text or "You can now share this quiz" in poll_response.text:
                            logger.info("Reached the end of the quiz.")
                            break

                        if not poll_response.poll:
                            logger.warning(f"Expected a poll, but got text: {poll_response.text}")
                            continue

                        # The explanation message that follows the poll
                        explanation_response = await conv.get_response(timeout=30)

                        question_text = poll_response.poll.question
                        options = [opt.text for opt in poll_response.poll.options]
                        correct_answer_text = None

                        # Find the bold text in the explanation, which is the correct answer
                        if explanation_response.entities:
                            for entity, text_part in zip(explanation_response.entities, explanation_response.text.split('\n')[0].split()):
                                if isinstance(entity, (types.MessageEntityBold, types.MessageEntityTextUrl)):
                                    correct_answer_text = text_part.strip('.,*`')
                                    break

                        if not correct_answer_text:
                            logger.warning(f"Could not determine correct answer text for question: {question_text}")
                            continue

                        correct_option_index = -1
                        for i, opt_text in enumerate(options):
                            if correct_answer_text.lower() in opt_text.lower():
                                correct_option_index = i
                                break

                        if correct_option_index != -1:
                            cloned_quiz_data['questions'].append({
                                'text': question_text,
                                'options': options,
                                'correct': correct_option_index
                            })
                            logger.info(f"Successfully cloned question: {question_text}")
                        else:
                            logger.warning(f"Could not match answer '{correct_answer_text}' to options for question: {question_text}")

                    except asyncio.TimeoutError:
                        logger.info("Quiz cloning finished or timed out.")
                        break

        except Exception as e:
            logger.error(f"An error occurred during cloning: {e}")
            raise  # Re-raise the exception to be handled by the calling function
        finally:
            if self.client.is_connected():
                await self.client.disconnect()

        return cloned_quiz_data