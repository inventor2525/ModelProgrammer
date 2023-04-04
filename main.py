from ModelProgrammer.Programmer import *
import os

if __name__ == '__main__':
	app = QApplication(sys.argv)
	
	# Ensure our config directory exists:
	os.makedirs(os.path.expanduser("~/.config/ModelProgrammer"), exist_ok=True)
	
	# Check if the database exists, if not, load the demo database if it exists:
	database_version = '1'
	database_path = os.path.expanduser(f"~/.config/ModelProgrammer/Programmer_v{database_version}.db")
	if os.path.exists(database_path):
		print(f"Loading user database at {database_path}.")
		db = ConversationDB(database_path)
	else:
		print(f"v{database_version} user database not found.")
		old_db_path = os.path.expanduser("~/.config/ModelProgrammer/Programmer_v0.db")
		if os.path.exists(old_db_path):
			print("Migrating old database. (This may take a while)")
			db = ConversationDB(database_path)
			db.migrate_data(old_db_path)
		elif os.path.exists("demo.db"):
			print("Loading demo database.")
			
			# Copy the demo database to the user's database_path:
			with open("demo.db", 'rb') as f:
				data = f.read()
			with open(database_path, 'wb') as f:
				f.write(data)
			db = ConversationDB(database_path)
		else:
			print("Demo database not found either. Creating new database.")
			db = ConversationDB(database_path)
	
	# Load the latest conversation:
	conversation = db.load_conversation(db.latest_conversation)
	
	# Start the Programmer UI:
	programmer = Programmer(db, conversation)
	
	sys.exit(app.exec_())