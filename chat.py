import os
from groq import Groq

from dotenv import load_dotenv
load_dotenv()

# in pytohn class names are in CamelCase;
# non-class names (e.g. functions/variables) are in snake_case
class Chat:
    client = Groq()
    def __init__(self):
        self.messages = [
                {
                    # most important content for sys prompt is length of response
                    "role": "system",
                    "content": "Write the output in 1-2 sentences."
                },
            ]
    def send_message(self, message):
        self.messages.append(
            {
                'role': 'user',
                'content': message
            }
        )
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model="llama-3.1-8b-instant",
        )
        result = chat_completion.choices[0].message.content
        self.messages.append({
            'role': 'assistant',
            'content': result
        })
        return result
