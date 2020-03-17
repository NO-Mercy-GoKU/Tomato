from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
bot = ChatBot(
	'Tomato',
	storage_adapter='chatterbot.storage.SQLStorageAdapter',
	database_uri='sqlite:///database.sqlite3',
	logic_adapters=[
	{
		"import_path": "chatterbot.logic.BestMatch"
	}
	],
	trainer='chatterbot.trainers.ListTrainer')
#bot.set_trainer(ListTrainer)
trainer=ListTrainer(bot)

app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello, World!"
@app.route("/sms", methods=['POST'])
def sms_reply():
	msg = request.form.get('Body')
	print(msg)
	reply=bot.get_response(msg)
	print(reply)
	resp = MessagingResponse()
	resp.message(str(reply))
	return str(resp)
if __name__ == "__main__":
	app.run(debug=True)
