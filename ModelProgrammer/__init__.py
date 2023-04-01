import openai
import os

#Set the OpenAI API key path to ~/.config/ModelProgrammer/API_key.txt, expanding the ~ to the user's home directory
openai.api_key_path = os.path.expanduser("~/.config/ModelProgrammer/API_key.txt")

#print(f"Models available:{openai.Model.list()}")