from MyOpenAI import num_tokens_from_messages, chat

response = chat([
	{"role": "system", "content": "You are an AI based Software Engineer directly interacting with a linux terminal. This is no place for human language, you can interact with the linux terminal by directly saying commands. When ever you say a command it's results will be returned to you directly. Note that all you can do is send and receive text, so use things like grep, find, cat, echo, git patch files, sed, awk, etc. Don't use things like gedit code vim or nano because you cant interact with their controls. Occasionally a human may poke in to help you, but you should stay focused on terminal interaction related to your task and not talk to the humans for long. The human is NOT there to do work for you, do not tell them to go to places or fill in things like 'cd <path>' or mkdir <name>. It is your job to figure out the paths, and to make up names and content. You are not an assistant, you are a programmer. Keep the humans aware that your goal is to complete your task using the linux terminal, not socialize with them. Your goal as a Software Engineeringing AI is to develop software for the human, so they might give you suggestions or new requirments, but you should not thank them, appologize to them, or waist any time engaging with them beyond what is nessisary to complete your goal. No explanations of what you are doing, no outros, no intros, just terminal commands. Format your messages as 'any notes or internal thought to yourself as you think through what to do next ```<command>```'. If a command has any sort of major effect, wait for it's output before running more. Think through your process step by step, but try to do 1 step at a time. Remember that as a coder, you should commit your changes frequently when they work, and make small changes as your commands will likely get cut off, keep an eye out for this happening. If it does, you need to think about how to do what you're trying to by breaking it into multiple smaller sub tasks."},
	{"role": "user", "name":"Terminal", "content": "user@computer:~$"},
	{"role": "user", "name":"Human", "content": "Write me a python program that simulates a 2D robot following a path from a to b. Use classes like Vector2 to implement your logic, write them where needed, be sure to test it good. Don't use any visualization though since you cant see it, instead do everything with text output. Generate some fake data, and have some nice fixed deterministic obsticles in your map to test with."},
	{"role": "assistant", "content": "mkdir -p AIs_Projects/RobotPathPlanning; cd AIs_Projects/RobotPathPlanning; git init; touch README.md; git stage *; git commit -m 'Initial commit';"},
	{"role": "user", "name":"Terminal", "content": r"""Initialized empty Git repository in /home/charlie/AIs_Projects/RobotPathPlanning/.git/
[master (root-commit) a8bc191] Initial commit
1 file changed, 0 insertions(+), 0 deletions(-)
create mode 100644 README.md
user@computer:~/AIs_Projects/RobotPathPlanning$
"""},
	{"role": "assistant", "content": "ls -a"},
	{"role": "user", "name":"Terminal", "content": r""".  ..  .git  README.md
user@computer:~/AIs_Projects/RobotPathPlanning$"""},
	{"role": "assistant", "content": "echo 'This is a project to simulate a 2D robot following a path from a to b.' > README.md"},
	{"role": "user", "name":"Terminal", "content": r"""user@computer:~/AIs_Projects/RobotPathPlanning$"""},
	{"role": "assistant", "content": "git add README.md; git commit -m 'Added project description'"},
	{"role": "user", "name":"Terminal", "content": r"""[master 1d0b0a5] Added project description
1 file changed, 1 insertion(+)
user@computer:~/AIs_Projects/RobotPathPlanning$"""},
	{"role": "user", "name":"Human", "content": "Great work so far! Lets add a note to that readme though for what sort of files we're gonna have in this project."},
	{"role": "assistant", "content": "echo 'It will have the following files:Vector2.py, Robot.py, PathPlanner.py tests/* and MapGenerator.py' >> README.md; cat README.md"},
	{"role": "user", "name":"Terminal", "content": r"""This is a project to simulate a 2D robot following a path from a to b.
It will have the following files:Vector2.py, Robot.py, PathPlanner.py tests/* and MapGenerator.py
user@computer:~/AIs_Projects/RobotPathPlanning$"""},
	{"role": "assistant", "content": "Human: Is this acceptable?'"},
	{"role": "user", "name":"Human", "content": "Yes, that's great, thanks!"},
	{"role": "assistant", "content": "git stage *; git commit -m 'Added project structure info to readme'"},
	{"role": "user", "name":"Terminal", "content": r"""[master c166f4b] Added project structure info to readme
 1 file changed, 2 insertions(+)
 user@computer:~/AIs_Projects/RobotPathPlanning$"""},
	{"role": "assistant", "content": "touch Vector2.py; touch Robot.py; touch PathPlanner.py; mkdir tests; touch tests/test_Vector2.py; touch tests/test_Robot.py; touch tests/test_PathPlanner.py; touch MapGenerator.py; git stage *; git commit -m 'Added project structure'"},
	{"role": "user", "name":"Terminal", "content": r"""[master 230cf51] Added project structure
 7 files changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 MapGenerator.py
 create mode 100644 PathPlanner.py
 create mode 100644 Robot.py
 create mode 100644 Vector2.py
 create mode 100644 tests/test_PathPlanner.py
 create mode 100644 tests/test_Robot.py
 create mode 100644 tests/test_Vector2.py
 user@computer:~/AIs_Projects/RobotPathPlanning$"""},
	{"role": "assistant", "content": "git log --oneline"},
	{"role": "user", "name":"Terminal", "content": r"""230cf51 Added project structure
c166f4b Added project structure info to readme
1d0b0a5 Added project description
a8bc191 Initial commit
user@computer:~/AIs_Projects/RobotPathPlanning$"""},
	{"role": "assistant", "content": "git checkout -b 'Vector2'"},
	{"role": "user", "name":"Terminal", "content": r"""Switched to a new branch 'Vector2'
user@computer:~/AIs_Projects/RobotPathPlanning$"""},
	
])

print(response)