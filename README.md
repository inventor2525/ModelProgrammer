# ModelProgrammer

ModelProgrammer (MP) is an experimental interactive AI-powered programmer and a supporting QT based conversation UI to enable fine tuning and development of large language models for linux terminal interaction.

Currently MP only supports OpenAI's ChatGPT 3 model but ideally it will support others (including open weight models) in the future.

## Long Term Vision

To sit down and tell a chat bot your project idea and have it write it for you while debugging and committing it's work while seamlessly being able to collaborate with it, giving it code reviews, helping each other debug, etc.

## Features
- AI-powered programmer using OpenAI's ChatGPT 3 API
- The AI can run terminal commands after the user confirms their safety
- User can edit commands the AI writes before they are run.
- The user can play the part of the AI to 'coax' an un-tuned LLM into development rather than conversation
- Auto stores all conversation and message data in SQLite db for latter experimentation & model fine tuning, including changes to any messages.

<p align="center">
  <img src="Screenshot.png" alt="Screenshot of the chatbot UI" />
</p>

## Installation

1. Obtain an API key for OpenAI [here](https://platform.openai.com/account/api-keys)
1. Start a linux system where you want to run this program.
1. Place the api key in a text file as such:
	```bash
	mkdir -p ~/.config/ModelProgrammer
	echo "<your_api_key_here>" > ~/.config/ModelProgrammer/API_key.txt
	```
	> Note this is loaded from the \_\_init\_\_.py file if you wish to change it.
1. Install ModelProgrammer in your favorite python 3.10 virtual environment
	```bash
	git clone https://github.com/yourusername/ModelProgrammer.git
	cd ModelProgrammer
	pip install -e ./
	```

## Usage

1. cd into ModelProgrammer
1. Run:
	```python 
	python3 main.py
	```
## Ok, it's going
### How use thing?
1. Type messages at the bottom and they will send to the model when the check box next to the send button is ticked. (un tick it to build up a fake conversation without sending)
1. Change the drop down at the bottom to assistant and the terminal will respond to you when you add the message and then click run (the Run Send and Add button are all the same button)
1. Uncheck messages to not have them sent to the model (easy context saving)
1. Edit messages and click checkmark to save them (they'll immediately be in the database)

# Whats Next?

First the user interface will gain greater ability to mix and match pieces of previous conversations, review responses, and allow the model to more cleanly and consistently interact with both the terminal and the user at the same time.

This really needs to be constrained to a safe environment. Thinking the AI can only interact inside a docker container!

Then, and during development training data will be collected to improve model interaction with the terminal.

3 key immediate areas of focus are:
1. Correctly making small edits using eof inserts or patch files or other means
1. The model tends to prefer to edit the test rather than the code
1. It doesn't explore it's environment enough (tree, git logs, docs, ls etc) and needs to be able to summarize what it has so far rather than relying totally on context.

As the UI becomes quicker to work with, with less back and forth or work in cleaning up the models mistakes, the UI essentially becomes a data labeling and dataset curating tool for a human supervised boot strapped training method for AI coding.

One unique thing that could be done for instance is any time a change by the AI causes a test to fail, its final version once it gets the test to pass, could be paired with the original request to teach it better programming. You basically just filter out all the code that caused a failed test to make a dataset for fine tuning using code it iterated on for you.

## License

This project is licensed under the GNU General Public License v3.0 or any later version - see the [LICENSE](LICENSE) file for details.

# Disclaimer

I make no warranty of this, it can execute fully arbitrary code, so use at your own risk! Always check the commands this thing is going to run before it runs them!