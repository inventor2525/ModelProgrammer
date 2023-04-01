from ModelProgrammer.Programmer import *

if __name__ == '__main__':
	app = QApplication(sys.argv)
	
	db = ConversationDB("Programmer_v0.db")
	conversation = db.load_conversation(db.latest_conversation)
	programmer = Programmer(db, conversation)
	
	sys.exit(app.exec_())