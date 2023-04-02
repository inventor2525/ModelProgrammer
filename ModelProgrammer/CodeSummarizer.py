import ast
import sys
import os
 
def get_annotation(annotation):
	if annotation:
		return ast.unparse(annotation)
	return ""

def extract_info(module, level=0):
	nodes_to_remove = []

	for node in ast.iter_child_nodes(module):
		if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
			print(f"{'Function' if level == 0 else 'Method'}: {node.name}")
			print(f"{'	' * level}Docstring: {ast.get_docstring(node)}")
			for arg in node.args.args:
				print(f"{'	' * level}	Argument: {arg.arg} {get_annotation(arg.annotation)}".rstrip())
			if node.returns:
				print(f"{'	' * level}	Returns: {get_annotation(node.returns)}")

		elif isinstance(node, ast.ClassDef):
			base_classes = ', '.join(ast.unparse(base) for base in node.bases)
			print(f"{'	' * level}Class: {node.name}({base_classes})")
			instance_vars = set()
			for body_node in node.body:
				if isinstance(body_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
					for stmt in body_node.body:
						if isinstance(stmt, ast.Assign):
							for target in stmt.targets:
								if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
									instance_vars.add(target.attr)
			if instance_vars:
				print(f"{'	' * level}	Instance Variables: {', '.join(sorted(instance_vars))}")
			extract_info(node, level + 1)

		if level == 0:
			nodes_to_remove.append(node)

	for node in nodes_to_remove:
		module.body.remove(node)


def describe_files(files, recursive=False):
	for path in files:
		if os.path.isfile(path) and path.endswith('.py'):
			print(f"File: {os.path.abspath(path)}")
			with open(path, 'r') as f:
				code = f.read()
			module = ast.parse(code)
			extract_info(module)
			print("\n")
		elif os.path.isdir(path):
			if recursive:
				for root, _, file_names in os.walk(path):
					sub_files = [os.path.join(root, name) for name in file_names if name.endswith('.py')]
					describe_files(sub_files, recursive)
			else:
				file_names = [f for f in os.listdir(path) if f.endswith('.py')]
				sub_files = [os.path.join(path, name) for name in file_names]
				describe_files(sub_files, recursive)

if __name__ == '__main__':
	args = sys.argv[1:]
	recursive = '-r' in args
	if recursive:
		args.remove('-r')
	describe_files(args, recursive)
