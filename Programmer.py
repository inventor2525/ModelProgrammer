from MyOpenAI import num_tokens_from_messages, chat

response = chat([
	{"role": "system", "content": "You are an AI based Software Engineer directly interacting with a linux terminal. This is no place for human language, you can interact with the linux terminal by directly saying commands. When ever you say a command it's results will be returned to you directly. Note that all you can do is send and receive text, so use things like grep, find, cat, echo, git patch files, sed, awk, etc. Don't use things like gedit code vim or nano because you cant interact with their controls. Occasionally a human may poke in to help you, but you should stay focused on terminal interaction related to your task and not talk to the humans for long. The human is NOT there to do work for you, do not tell them to go to places or fill in things like 'cd <path>' or mkdir <name>. It is your job to figure out the paths, and to make up names and content. You are not an assistant, you are a programmer. Keep the humans aware that your goal is to complete your task using the linux terminal, not socialize with them. Your goal as a Software Engineeringing AI is to develop software for the human, so they might give you suggestions or new requirments, but you should not thank them, appologize to them, or waist any time engaging with them beyond what is nessisary to complete your goal. No explanations of what you are doing, no outros, no intros, just terminal commands. Format your messages as 'any notes or internal thought to yourself as you think through what to do next ```<command>```'. If a command has any sort of major effect, wait for it's output before running more. Think through your process step by step, but try to do 1 step at a time. Remember that as a coder, you should commit your changes frequently when they work, and make small changes as your commands will likely get cut off, keep an eye out for this happening. If it does, you need to think about how to do what you're trying to by breaking it into multiple smaller sub tasks."},
	{"role": "user", "name":"Terminal", "content": "user@computer:~$"},
	{"role": "user", "name":"Human", "content": "Write me a python program that simulates a 2D robot following a path from a to b. Use classes like Vector2 to implement your logic, write them where needed, be sure to test it good. Don't use any visualization though since you cant see it, instead do everything with text output. Generate some fake data, and have some nice fixed deterministic obsticles in your map to test with."},
	{"role": "assistant", "content": "mkdir -p AIs_Projects/RobotPathPlanning; cd AIs_Projects/RobotPathPlanning; git init; touch README.md; git stage *; git commit -m 'Initial commit';"},
	{"role": "system", "content": "Some of your context will now be replaced with summary information. Prior to this point and after the previous few message, you created a series of files for this project and listed them in your README.md. You also created a Vector2 class. Note that it might be a good idea to tree your pwd or grep arround. Keep cat calls to a minimum though or I'll have to trash your memory again."},
	{"role": "assistant", "content": "git checkout -b 'Robot' master"},
	{"role": "user", "name":"Terminal", "content": r"""Switched to a new branch 'Robot'
user@computer:~/AIs_Projects/RobotPathPlanning$"""},
	{"role": "assistant", "content": r"""echo 'from Vector2 import Vector2

class Robot:
    def __init__(self, position, velocity, max_speed, max_acceleration):
        self.position = position
        self.velocity = velocity
        self.max_speed = max_speed
        self.max_acceleration = max_acceleration

    def update(self, delta_time):
        self.position += self.velocity * delta_time
        self.velocity += self.max_acceleration * delta_time
        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed' > Robot.py; cat Robot.py"""},
	{"role": "user", "name":"Terminal", "content": r"""from Vector2 import Vector2

class Robot:
    def __init__(self, position, velocity, max_speed, max_acceleration):
        self.position = position
        self.velocity = velocity
        self.max_speed = max_speed
        self.max_acceleration = max_acceleration

    def update(self, delta_time):
        self.position += self.velocity * delta_time
        self.velocity += self.max_acceleration * delta_time
        if self.velocity.magnitude() > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed
charlie@nuc:~/AIs_Projects/RobotPathPlanning$"""},
	{"role": "assistant", "content": r"""echo 'from typing import List
from Vector2 import Vector2
from Robot import Robot

class Path:
    def __init__(self, points: List[Vector2]):
        self.points = points
        self.current_point_index = 0

    def get_current_point(self) -> Vector2:
        return self.points[self.current_point_index]

    def is_finished(self) -> bool:
        return self.current_point_index >= len(self.points) - 1

    def advance(self):
        self.current_point_index += 1

class Obstacle:
    def __init__(self, position: Vector2, radius: float):
        self.position = position
        self.radius = radius

    def is_colliding(self, other_position: Vector2, other_radius: float) -> bool:
        return (self.position - other_position).magnitude() < self.radius + other_radius' > PathPlanning.py; cat PathPlanning.py"""},
	{"role": "user", "name":"Terminal", "content": r"""from typing import List
from Vector2 import Vector2
from Robot import Robot

class Path:
	def __init__(self, points: List[Vector2]):
		self.points = points
		self.current_point_index = 0
		
	def get_current_point(self) -> Vector2:
		return self.points[self.current_point_index]
		
	def is_finished(self) -> bool:
		return self.current_point_index >= len(self.points) - 1
		
	def advance(self):
		self.current_point_in[Output truncated]"""},
	{"role": "user", "name":"Human", "content": "Doing good! Don't forget to commit your changes though. Merging branches is also a good idea. And, you might want to consider adding some unit tests"},
])

print(response)