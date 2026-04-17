"""A REPL-based chat interface that supports tool use for file system operations."""

import os   # noqa: F401

from groq import Groq
from dotenv import load_dotenv

from tools.calculate import calculate, tool_definition as calculate_def
from tools.ls import ls, tool_definition as ls_def
from tools.cat import cat, tool_definition as cat_def
from tools.grep import grep, tool_definition as grep_def

load_dotenv()

TOOLS = [calculate_def, ls_def, cat_def, grep_def]
TOOL_MAP = {
    'calculate': calculate,
    'ls': ls,
    'cat': cat,
    'grep': grep,
}


class Chat:
    '''
    A chat interface that uses the Groq API with support for tool use.

    Supports automatic tool calling via the LLM and manual slash commands.

    >>> chat = Chat()
    >>> chat.send_message('my name is bob', temperature=0.0)
    "I don't have any information about you, but I can chat with you. What would you like to talk about?"
    >>> def monkey_input(prompt, user_inputs=['Hello, I am monkey.', 'Goodbye.']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> Hello, I am monkey.
    Hello monkey, it's nice to meet you. What would you like to do today?
    chat> Goodbye.
    Goodbye monkey. It was nice chatting with you.
    <BLANKLINE>
    '''
    client = Groq()

    def __init__(self):
        self.messages = [
            {
                'role': 'system',
                'content': 'Write the output in 1-2 sentences.'
            },
        ]

    def send_message(self, message, temperature=0.8):
        """Send a message and return the assistant response, handling tool calls if needed."""
        self.messages.append({'role': 'user', 'content': message})
        while True:
            chat_completion = self.client.chat.completions.create(
                messages=self.messages,
                model='llama-3.1-8b-instant',
                temperature=temperature,
                tools=TOOLS,
                tool_choice='auto',
            )
            choice = chat_completion.choices[0]
            if choice.finish_reason == 'tool_calls':
                self.messages.append(choice.message)
                for tool_call in choice.message.tool_calls:
                    name = tool_call.function.name
                    import json
                    args = json.loads(tool_call.function.arguments)
                    result = TOOL_MAP[name](**args)
                    self.messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'content': result,
                    })
            else:
                result = choice.message.content
                self.messages.append({'role': 'assistant', 'content': result})
                return result


def run_slash_command(chat, user_input):
    """
    Run a slash command manually and add the output to the chat context.

    >>> chat = Chat()
    >>> output = run_slash_command(chat, '/ls .')
    >>> 'chat.py' in output
    True
    >>> run_slash_command(chat, '/cat /etc/passwd')
    'Error: unsafe path'
    >>> run_slash_command(chat, '/unknowncmd')
    'Error: unknown command'
    """
    parts = user_input[1:].split()
    command = parts[0]
    args = parts[1:]
    if command not in TOOL_MAP:
        return 'Error: unknown command'
    result = TOOL_MAP[command](*args)
    chat.messages.append({'role': 'user', 'content': f'/{command} {" ".join(args)}'})
    chat.messages.append({'role': 'assistant', 'content': result})
    return result


def repl(temperature=0.8):
    """Run the interactive chat REPL, supporting both messages and slash commands."""
    import readline  # noqa: F401
    chat = Chat()
    try:
        while True:
            user_input = input('chat> ')
            if user_input.startswith('/'):
                print(run_slash_command(chat, user_input))
            else:
                response = chat.send_message(user_input, temperature=temperature)
                print(response)
    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == '__main__':
    repl()
