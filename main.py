import webapp2
from google.appengine.ext import db
import jinja2
import os
import datetime, time
import sys
import logging

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

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

	@property
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
@db.transactional
def AddGamer(name, nick):
	gamer = Gamer(name = name, nick = nick)
	gamer.put()
	return gamer

@db.transactional
def AddGame(date):
	game = Game(date = date)
	game.put()
	return game

def GetGamer(name, nick):
	gamer = Gamer.gql("WHERE name = :1", name)
	if gamer.count() > 0:
		return gamer[0]

	return AddGamer(name, nick)

def GetGame(date):
	logging.info("date = '" + str(date) + "'")
	game = Game.gql("WHERE date = :1", date)
	logging.info('game.count() = ' + str(game.count()))
	if game.count() > 0:
		return game[0]

	return AddGame(date)

def StrToDate(dateAsStr):
	# logging.info("dateAsStr = '" + dateAsStr + "'")
	dateAsTime = time.strptime(dateAsStr, "%d.%m.%Y")
	# logging.info("dateAsTime = '" + str(dateAsTime) + "'")
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
	text = text.replace('%', '')
	text = text.replace(',', '.')
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
		try:
			Parse(self.request.get('stats'))
			self.redirect('/')

			txn.commit();
		except:
			template_values = {
				'errors': unicode(sys.exc_info()[1]),
			}

			template = JINJA_ENVIRONMENT.get_template('add.html')
			self.response.write(template.render(template_values))

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
		achievements = []
		for gamer in command.gamers:
			stats.extend(gamer.stats)
			achievements.extend(gamer.achievements)

		template_values = {
			'command': command,
			'stats': stats,
			'achievements': achievements,
		}

		template = JINJA_ENVIRONMENT.get_template('command.html')
		self.response.write(template.render(template_values))
	
app = webapp2.WSGIApplication(
	[('/', MainPage),
	('/add', AddPage),
	('/gamer', GamerPage),
	('/game', GamePage),
	('/command', CommandPage),
	# ('/editCommand', EditCommandPage),
	],
	debug = True)