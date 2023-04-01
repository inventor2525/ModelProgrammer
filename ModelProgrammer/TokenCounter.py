import tiktoken
from ModelProgrammer.Conversation import Message, Conversation

def tokens_in_string(s:str) -> int:
	"""Note: This is not exact. See code in ChatBot.py for more details."""
	
	encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
	tokens = encoding.encode(s)
	return len(tokens)
	
def tokens_in_message(message:Message) -> int:
	"""Note: This is not exact. See code in ChatBot.py for more details."""
	
	return tokens_in_string(message.content)