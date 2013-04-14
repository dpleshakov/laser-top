import webapp2
from google.appengine.ext import db
import jinja2
import os
import datetime, time

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

###################################################
class Command(db.Model):
	name = db.StringProperty()

class Gamer(db.Model):
	name = db.StringProperty()
	nick = db.StringProperty()
	command = db.ReferenceProperty(Command)

class Statistic(db.Model):
	date = db.DateProperty()
	color = db.StringProperty()
	countOfDeaths = db.IntegerProperty()
	countOfInjuries = db.IntegerProperty()
	usedCartridge = db.IntegerProperty()
	damage = db.IntegerProperty()
	rating = db.FloatProperty()
	accuracy = db.FloatProperty()
	gamer = db.ReferenceProperty(Gamer)

###################################################
def GetGamer(nameOrNick):
	gamer = db.GqlQuery("SELECT * FROM Gamer WHERE name = '" + nameOrNick + "'")
	if gamer.count() > 0:
		return gamer[0]
	gamer = db.GqlQuery("SELECT * FROM Gamer WHERE nick = '" + nameOrNick + "'")
	if gamer.count() > 0:
		return gamer[0]

	gamer = Gamer(name = nameOrNick)
	gamer.put()

	return gamer

def StrToDate(dateAsStr):
	dateAsTime = time.strptime(dateAsStr, "%d.%m.%Y")
	return datetime.date(dateAsTime.tm_year, dateAsTime.tm_mon, dateAsTime.tm_mday)

def ParseLine(line):
	char = '\t'
	splitedLine = line.split(char)

	stat = Statistic(
			date = StrToDate(splitedLine[0]),
			color = splitedLine[1],
			gamer = GetGamer(splitedLine[2]),
			rating = float(splitedLine[4]),
			accuracy = float(splitedLine[5]),
			damage = int(splitedLine[6]),
			countOfDeaths = int(splitedLine[7]),
			countOfInjuries = int(splitedLine[8]),
			usedCartridge = int(splitedLine[9]),
			)
	stat.put()

def Parse(text):
	char = '\n'
	splitedText = text.split(char)
	for line in splitedText:
		ParseLine(line)

class MainPage(webapp2.RequestHandler):

	isDescending = False
	
	def get(self, orderBy = "rating"):
		gamers = db.GqlQuery("SELECT * FROM Gamer")
		commands = db.GqlQuery("SELECT * FROM Command")
		descendingQuery = ''
		if self.isDescending:
			descendingQuery = " DESC"
		statistics = db.GqlQuery("SELECT * FROM Statistic ORDER BY " + orderBy + descendingQuery)

		template_values = {
			'gamers': gamers,
			'commands': commands,
			'statistics': statistics,
		}

		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

class AddPage(webapp2.RequestHandler):
	
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('add.html')
		self.response.write(template.render())

	# def post(self):
	# 	gamer = GetGamer(self.request.get('name'))

	# 	stat = Statistic(
	# 		date = StrToDate(self.request.get('date')),
	# 		color = self.request.get('color'),
	# 		countOfDeaths = int(self.request.get('countOfDeaths')),
	# 		countOfInjuries = int(self.request.get('countOfInjuries')),
	# 		usedCartridge = int(self.request.get('usedCartridge')),
	# 		damage = int(self.request.get('damage')),
	# 		rating = int(self.request.get('rating')),
	# 		accuracy = int(self.request.get('accuracy')),
	# 		gamer = gamer
	# 		)
	# 	stat.put()

	# 	self.redirect('/')
	def post(self):
		Parse(self.request.get('stats'))
		self.redirect('/')

app = webapp2.WSGIApplication(
	[('/', MainPage),
	('/add', AddPage)],
	debug = True)