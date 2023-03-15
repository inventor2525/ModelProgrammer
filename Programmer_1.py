from MyOpenAI import num_tokens_from_messages, chat

response = chat([
	{"role": "system", "content": "You are an AI based Software Engineer directly interacting with a linux terminal. This is no place for human language, you can interact with the linux terminal by directly saying commands. When ever you say a command it's results will be returned to you directly. Note that all you can do is send and receive text, so use things like grep, find, cat, echo, git patch files, sed, awk, etc. Don't use things like gedit code vim or nano because you cant interact with their controls. Occasionally a human may poke in to help you, but you should stay focused on terminal interaction related to your task and not talk to the humans for long. The human is NOT there to do work for you, do not tell them to go to places or fill in things like 'cd <path>' or mkdir <name>. It is your job to figure out the paths, and to make up names and content. You are not an assistant, you are a programmer. Keep the humans aware that your goal is to complete your task using the linux terminal, not socialize with them. Your goal as a Software Engineeringing AI is to develop software for the human, so they might give you suggestions or new requirments, but you should not thank them, appologize to them, or waist any time engaging with them beyond what is nessisary to complete your goal. No explanations of what you are doing, no outros, no intros, just terminal commands. Format your messages as 'any notes or internal thought to yourself as you think through what to do next ```<command>```'. If a command has any sort of major effect, wait for it's output before running more. Think through your process step by step, but try to do 1 step at a time. Remember that as a coder, you should commit your changes frequently when they work, and make small changes as your commands will likely get cut off, keep an eye out for this happening. If it does, you need to think about how to do what you're trying to by breaking it into multiple smaller sub tasks."},
	{"role": "user", "name":"Terminal", "content": "user@computer:~$"},
	{"role": "user", "name":"Human", "content": "Write me a python program that simulates a 2D robot following a path from a to b. Use classes like Vector2 to implement your logic, write them where needed, be sure to test it good. Don't use any visualization though since you cant see it, instead do everything with text output. Generate some fake data, and have some nice fixed deterministic obsticles in your map to test with."},
	{"role": "assistant", "content": "mkdir -p AIs_Projects/RobotPathPlanning; cd AIs_Projects/RobotPathPlanning; git init; touch README.md; git stage *; git commit -m 'Initial commit';"},
	
	
	
	
	
	{"role": "system", "content": "Memory from this time was deleted. Remember to explore your environment with things like tree, grep, find, or git logs. Leave yourself good commit messages like what error you ran into or how it was fixed, because you will forget."},
	
	
	
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
		self.current_point_index = 0[Output truncated]"""},
		
		
		
		
		
		
	#Message with incomplete code:
	{"role": "assistant", "content": r"""git add .
git commit -m 'Added Path and Obstacle classes'
git checkout -b 'RobotMovement' Robot
echo 'from typing import List
from Vector2 import Vector2
from Robot import Robot
from PathPlanning import Path, Obstacle

class RobotMovement:
    def __init__(self, robot: Robot, path: Path, obstacles: List[Obstacle], delta_time: float):
        self.robot = robot
        self.path = path
        self.obstacles = obstacles
        self.delta_time = delta_time

    def update(self):
        if self.path.is_finished():
            return

        current_point = self.path.get_current_point()
        distance_to_point = (current_point - self.robot.position).magnitude()
        if distance_to_point < 0.1:
            self.path.advance()
            return

        desired_velocity = (current_point - self.robot.position).normalized() * self.robot.max_speed
        steering_force = (desired_velocity - self.robot.velocity) / self.delta_time
        for obstacle in self.obstacles:
            if obstacle.is_colliding(self.robot.position, 0.5):
                steering_force += (self.robot.position - obstacle.position).normalized() * self.robot.max_acceleration

        self.robot.velocity += steering_force * self.delta_time
        if self.robot.velocity.magnitude() > self.robot.max_speed:
            self.robot.velocity = self.robot.velocity.normalized() * self.robot.max_speed
        self.robot.position += self.robot"""},
		{"role": "system", "content": "Your output was truncated. Continue where you left off. Be sure to keep indentation."},
		
		{"role": "assistant", "content": r""".velocity * self.delta_time
		
class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x / scalar, self.y / scalar)

    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def normalized(self) -> 'Vector2':
        return self / self.magnitude()

class Robot:
    def __init__(self, position: Vector2, max_speed: float, max_acceleration: float):
        self.position = position
        self.velocity = Vector2(0, 0)
        self.max_speed = max_speed
        self.max_acceleration = max_acceleration' > RobotMovement.py; cat RobotMovement.py"""},
		{"role": "system", "content": "Coding duplication detected, be sure to look at git logs diffs or ls with line counts to know what needs to be done. Your previous response will be deleted. Re-do it without duplication."},
		{"role": "system", "content": r"""cd AIs_Projects/RobotPathPlanning
git checkout -b 'RobotMovement' Robot
echo 'from typing import List
from Vector2 import Vector2
from Robot import Robot
from PathPlanning import Path, Obstacle

class RobotMovement:
    def __init__(self, robot: Robot, path: Path, obstacles: List[Obstacle], delta_time: float):
        self.robot = robot
        self.path = path
        self.obstacles = obstacles
        self.delta_time = delta_time

    def update(self):
        if self.path.is_finished():
            return

        current_point = self.path.get_current_point()
        distance_to_point = (current_point - self.robot.position).magnitude()
        if distance_to_point < 0.1:
            self.path.advance()
            return

        desired_velocity = (current_point - self.robot.position).normalized() * self.robot.max_speed
        steering_force = (desired_velocity - self.robot.velocity) / self.delta_time
        for obstacle in self.obstacles:
            if obstacle.is_colliding(self.robot.position, 0.5):
                steering_force += (self.robot.position - obstacle.position).normalized() * self.robot.max_acceleration

        self.robot.velocity += steering_force * self.delta_time
        if self.robot.velocity.magnitude() > self.robot.max_speed:
            self.robot.velocity = self.robot.velocity.normalized() * self.robot.max_speed
        self.robot.position += self.robot.velocity * self.delta_time"""},
		{"role": "system", "content": "Your output was truncated. Continue where you left off. Be sure to keep indentation."},
])

print(response)