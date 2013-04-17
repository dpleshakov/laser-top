import webapp2
from google.appengine.ext import db
import jinja2
import os
import datetime, time

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

###################################################
class Command(db.Model):
	name = db.StringProperty(required = True)
	# gamers

	@property
	def keyStr(self):
		return str(self.key())

	@property
	def gamersCount(self):
		return self.gamers.count()

class Gamer(db.Model):
	name = db.StringProperty(required = True)
	nick = db.StringProperty()
	command = db.ReferenceProperty(Command, collection_name = 'gamers')
	# stats
	# achievements

	@property
	def keyStr(self):
		return str(self.key())

	@property
	def gamesCount(self):
		return self.stats.count()

class Game(db.Model):
	date = db.DateProperty(required = True)
	# stats
	# achievements

	@property
	def keyStr(self):
		return str(self.key())

	@property:
	def gamersCount(self):
		return self.stats.count()

class Statistic(db.Model):
	game = db.ReferenceProperty(Game, collection_name = 'stats', required = True)
	color = db.StringProperty(required = True)
	gamer = db.ReferenceProperty(Gamer, collection_name = 'stats', required = True)
	rating = db.FloatProperty(required = True)
	accuracy = db.FloatProperty(required = True)
	damage = db.IntegerProperty(required = True)
	countOfDeaths = db.IntegerProperty(required = True)
	countOfInjuries = db.IntegerProperty(required = True)
	usedCartridge = db.IntegerProperty(required = True)

class AchievementType(db.Model):
	name = db.StringProperty(required = True)
	level = db.StringProperty(required = True)
	image = db.LinkProperty(default = None)
	# achievements
	
class Achievement(db.Model):
	achievementType = db.ReferenceProperty(AchievementType, collection_name = 'achievements', required = True)
	game = db.ReferenceProperty(Game, collection_name = 'achievements', required = True)
	gamer = db.ReferenceProperty(Gamer, collection_name = 'achievements', required = True)

###################################################
def GetGamer(name, nick):
	gamer = Gamer.gql("WHERE name = :1", name)
	if gamer.count() > 0:
		return gamer[0]

	gamer = Gamer(name = name, nick = nick)
	gamer.put()

	return gamer

def GetGame(date):
	game = Game.gql("WHERE date = :1", date)
	if game.count() > 0:
		return game[0]

	game = Game(date = date)
	game.put()

	return game

def StrToDate(dateAsStr):
	dateAsTime = time.strptime(dateAsStr, "%d.%m.%Y")
	return datetime.date(dateAsTime.tm_year, dateAsTime.tm_mon, dateAsTime.tm_mday)

def ParseLine(line):
	char = '\t'
	splitedLine = line.split(char)

	stat = Statistic(
			game = GetGame(StrToDate(splitedLine[0])),
			color = splitedLine[1],
			gamer = GetGamer(splitedLine[2], splitedLine[3]),
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
	text.replace(' ', '')
	text.replace('%', '')
	text.replace(',', '.')
	splitedText = text.split(char)
	for line in splitedText:
		ParseLine(line)

###################################################
class MainPage(webapp2.RequestHandler):
	def get(self):
		orderBy = self.request.get('orderBy')
		if not orderBy:
			orderBy = 'rating'
		isDescending = self.request.get('isDescending') != "False"
		# if isDescending is null:
		# 	isDescending = False

		descendingQuery = ''
		if isDescending:
			descendingQuery = " DESC"

		gamers = db.GqlQuery("SELECT * FROM Gamer")
		commands = db.GqlQuery("SELECT * FROM Command")
		statistics = db.GqlQuery("SELECT * FROM Statistic ORDER BY " + orderBy + descendingQuery)

		template_values = {
			'gamers': gamers,
			'commands': commands,
			'statistics': statistics,
			'orderBy': orderBy,
			'isDescending': not isDescending,
		}

		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

class AddPage(webapp2.RequestHandler):
	
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('add.html')
		self.response.write(template.render())

	def post(self):
		Parse(self.request.get('stats'))
		self.redirect('/')

class GamerPage(webapp2.RequestHandler):

	def get(self):
		gamerKeyStr = self.request.get('key')
		gamer = db.get(db.Key(encoded = gamerKeyStr))

		template_values = {
			'gamer': gamer
		}

		template = JINJA_ENVIRONMENT.get_template('gamer.html')
		self.response.write(template.render(template_values))

class GamePage(webapp2.RequestHandler):

	def get(self):
		gameKeyStr = self.request.get('key')
		game = db.get(db.Key(encoded = gameKeyStr))

		template_values = {
			'game': game
		}

		template = JINJA_ENVIRONMENT.get_template('game.html')
		self.response.write(template.render(template_values))

class CommandPage(webapp2.RequestHandler):

	def get(self):
		commandKeyStr = self.request.get('key')
		command = db.get(db.Key(encoded = gameKeyStr))
		stats = []
		for gamer in command.gamers:
			stats.extend(gamer.stats)

		template_values = {
			'command': command,
			'stats': stats,
		}

		template = JINJA_ENVIRONMENT.get_template('command.html')
		self.response.write(template.render(template_values))

app = webapp2.WSGIApplication(
	[('/', MainPage),
	('/add', AddPage),
	('/Gamer', GamerPage),
	('/Game', GamePage),
	('/Command', CommandPage),
	],
	debug = True)