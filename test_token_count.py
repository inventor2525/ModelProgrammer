import tiktoken

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

tokens = encoding.encode(r"tiktoken is great!")
print(tokens)
print(len(tokens))