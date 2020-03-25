"""
Created on Tue Mar 24 21:44:39 2020

@author: MahaKAAL
"""
import requests
from time import sleep
from bs4 import BeautifulSoup
from chatterbot import ChatBot
from chatterbot.comparisons import levenshtein_distance, jaccard_similarity, sentiment_comparison, synset_distance
from chatterbot.response_selection import get_first_response
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import datetime
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(2)
executed=False
wished=False
bot = ChatBot(
	'Tomato',
	storage_adapter='chatterbot.storage.SQLStorageAdapter',
	database_uri='sqlite:///update_corpus_database.sqlite3',

	preprocessors=[
		'chatterbot.preprocessors.clean_whitespace'
	],

	logic_adapters=[
		{
			"import_path": "chatterbot.logic.BestMatch",
			"statement_comparison_function": levenshtein_distance,
			"statement_comparison_function": synset_distance,
			"response_selection_method": get_first_response,
			'default_response': 'I am sorry, but I do not understand.',
			'maximum_similarity_threshold': 0.50
		},
{
			"import_path": "chatterbot.logic.BestMatch",
			"statement_comparison_function": jaccard_similarity,
			"statement_comparison_function": levenshtein_distance,
			"statement_comparison_function": sentiment_comparison,
			"response_selection_method": get_first_response,
			'default_response': 'I am sorry, but I do not understand.',
			'maximum_similarity_threshold': 0.50
		},
		{

			"import_path": "chatterbot.logic.MathematicalEvaluation",
		}
	],)
app = Flask(__name__)
@app.route("/")
def hello():
	return "<Head>Hello folks! This is a new api of chatbot, Tomato. Just request a post method at /sms and get your reply.</Head>"
@app.route("/sms", methods=['POST'])
def sms_reply():
	msg = request.form.get('Body')
	print(msg)
	reply=''
	if(msg!=None):
		if(('corona' in msg.lower().split())and(('stats' in msg.lower().split())or ('statistics' in msg.lower().split()) or ('news' in msg.lower().split()) or ('updates' in msg.lower().split()) or ('update' in msg.lower().split()) or ('statistic' in msg.lower().split()) or ('stat' in msg.lower().split()))):
			msg_body = show_all()
			first_part_body = msg_body[0][:len(msg_body[0]) // 2 + 14]
			second_part_body = msg_body[0][len(msg_body[0]) // 2 + 12:]
			third_part_body = msg_body[1]
			if('world' in msg.lower().split()):
				reply=first_part_body
			else:
				reply=third_part_body
		elif('schedule' in msg.lower().split() and 'all' in msg.lower().split()):
			requests.get("http://tomatotalk.herokuapp.com/jobs")
			reply="Alarms & Wishes are all set."
		else:
			reply=bot.get_response(msg)
			print(reply)
	resp = MessagingResponse()
	resp.message(str(reply))
	return str(resp)

@app.route('/jobs')
def run_jobs():
    executor.submit(alarms)
    executor.submit(wishes)
    return 'Alarms are launched in background!'

def wishes():
	print("Wishes are scheduled")
	if(True):
		dt=datetime.datetime
		if(dt.now().hour>6 and dt.now().hour<=22):
			wish='Good Night'
			sleeping_time=(22-dt.now().hour)*3600+(59-dt.now().minute)*60+(59-dt.now().second)
			print(sleeping_time)
			if(sleeping_time<0):
				wishes()
			sleep(sleeping_time)
			createMessage(wish)
		else:
			wish = 'Good Morning'
			sleeping_time=(5-dt.now().hour)*3600+(59-dt.now().minute)*60+(59-dt.now().second)
			print(sleeping_time)
			if (sleeping_time < 0):
				wishes()
			sleep(sleeping_time)
			createMessage(wish)

		print("Already done Wishing.")
		wishes()
'''
if(dt.now().hour>6):
			wish='Good Night'
			sleeping_time=(29-dt.now().hour)*3600+(59-dt.now().minute)*60+(59-dt.now().second)
		else:
			sleeping_time=(22-dt.now().hour)*3600+(59-dt.now().minute)*60+(59-dt.now().second)
			wish='Good Morning'

'''

def alarms():
	global executed
	print("Corona Alarms are scheduled!")
	print(executed)
	if(executed==False):
		executed = True
		dt=datetime.datetime
		if(dt.now().hour>=6):
			sleeping_time=(29-dt.now().hour)*3600+(59-dt.now().minute)*60+(59-dt.now().second)
		else:
			sleeping_time=(5-dt.now().hour)*3600+(59-dt.now().minute)*60+(59-dt.now().second)
		print(sleeping_time)
		if(sleeping_time<0):
			executed=False
			alarms()
		sleep(sleeping_time)
		msg_body = show_all()
		first_part_body=msg_body[0][:len(msg_body[0]) // 2 + 12]
		createMessage(first_part_body)
		second_part_body=msg_body[0][len(msg_body[0]) // 2 + 12:]
		createMessage(second_part_body)
		third_part_body=msg_body[1]
		createMessage(third_part_body)
		print("Updates Posted")
		executed=False
		alarms()


# World Data finding
def download_world_data():
	a = requests.get("https://www.worldometers.info/coronavirus/")
	got_data = a.text
	soup = BeautifulSoup(got_data, 'html.parser')
	data = soup.prettify()
	page_title = str(soup.title)
	page_title = page_title[7:-22]

	world_data = []
	for a in soup.find_all('table', attrs={'id': 'main_table_countries_today'}):
		for b in a.find_all('tr'):
			world_data.append(b.text.strip().split('\n'))
	return world_data


# pd_data_world=pd.DataFrame(world_data[1:-1],columns=world_data[0])
# pd_data_world.to_csv('corona_stats_world.csv')


def download_ind_data():
	# India Data Finding
	a1 = requests.get("https://www.mohfw.gov.in/")
	got_data2 = a1.text
	soup2 = BeautifulSoup(got_data2, 'html.parser')
	data2 = soup2.prettify()
	page_title2 = "CoronaVirus Update (Live): India State-wise"

	download_data = []
	for x in soup2.find_all('div', attrs={'id': 'cases'}):
		for y in (x.find_all('div', attrs={'class': 'table-responsive'})):
			for z in (y.find_all('tr')):
				download_data.append(z.text.strip().split('\n'))
	return download_data


# Visualising the data in CSV format
# pd_data=pd.DataFrame(download_data[1:-1],columns=download_data[0])
# pd_data.to_csv('corona_stats_india.csv')


def format_world_data():
	world_data = download_world_data()
	objects = []
	mydict = {}
	for x in range(1, len(world_data) - 1):
		for y in range(5):
			if (world_data[x][y] == '' or world_data[x][y] == ' '):
				mydict[world_data[0][y]] = '0'
			else:
				# 6 print(world_data[x][y])
				mydict[world_data[0][y]] = world_data[x][y].strip()

		objects.append(mydict)
		if (mydict['Country,Other'] == "India"):
			break
		mydict = {}
	# print(objects)
	return objects


def format_ind_data():
	download_data = download_ind_data()
	objects = []
	mydict = {}
	for x in range(1, len(download_data) - 1):
		for y in range(1, 6):
			if (download_data[x][y] == '' or download_data[x][y] == ' '):
				mydict[download_data[0][y]] = '0'
			else:
				# print(download_data[x][y])
				mydict[download_data[0][y]] = download_data[x][y].strip()

		objects.append(mydict)
		mydict = {}
	# print(objects)
	return objects


def show_world_data():
	values_got1 = format_world_data()
	returning = ""
	for x in values_got1:
		returning += (x.get('Country,Other') + "\n" + "Total Cases: " + x.get(
			'TotalCases') + "\n" + 'Total Deaths: ' + x.get('TotalDeaths') + "\n\n")
	return returning


def show_ind_data():
	values_got2 = format_ind_data()
	returning = ""
	for x in values_got2:
		returning += (x.get('Name of State / UT') + "\n" + "Total Cases: " + x.get(
			'Total Confirmed cases (Indian National)') + "\n" + 'Total Deaths: ' + x.get('Death') + "\n\n")
	return returning


def show_all():
	a = requests.get("https://www.worldometers.info/coronavirus/")
	got_data = a.text
	soup = BeautifulSoup(got_data, 'html.parser')
	data = soup.prettify()
	page_title = str(soup.title)
	page_title = page_title[7:-22]
	page_title2 = "CoronaVirus Update (Live): India State-wise"
	main_data1=page_title + "\n\n" + show_world_data()
	main_data2=page_title2 + "\n\n" + show_ind_data() + "\n\nStay Safe At Home."
	return ([main_data1,main_data2])

def createMessage(msg_body):
	pnlist=['+919635270177','+917908483889','+919679995500','+918436858480','+917001291866','+919732248317','+918609016486','+918579926004']
	account_sid = 'AC40f1ae77f284fb9522f629b5454cb991'
	auth_token = 'a6aa50dc31dc4e954c5dd2c9ef7f8ff9'
	client = Client(account_sid, auth_token)
	for x in pnlist:
		message = client.messages.create(from_='whatsapp:+14155238886',body=msg_body,to='whatsapp:'+x)
	#print(message.sid)
'''
print(show_world_data())
print(show_ind_data())

#Just By running show_world_data and show_ind_data function we can get the output
'''
#print(show_all())

if __name__ == "__main__":
	app.run()
