# -*- coding: utf-8 -*-

import os
import datetime, time
import sys
import logging

import loggingWrapper
import achievements

import webapp2
import jinja2
from google.appengine.ext import db
from google.appengine.api import images

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
)

######################################################################################################
def DateFormat(value):
	return value.strftime("%d.%m.%y")

def GamerFormat(gamer):
	if not gamer.nick or "None" in gamer.nick:
		return gamer.name
	else:
		return gamer.name + ' "' + gamer.nick + '"'

JINJA_ENVIRONMENT.filters['DateFormat'] = DateFormat
JINJA_ENVIRONMENT.filters['GamerFormat'] = GamerFormat

######################################################################################################
class Image(db.Model):
	data = db.BlobProperty(default = None)
	# commands
	@property
	def keyStr(self):
		return str(self.key())

###################################################
class Command(db.Model):
	name = db.StringProperty(required = True)
	logo = db.ReferenceProperty(Image, collection_name = 'commands')
	# image = db.BlobProperty(default = None)
	# gamers
	@property
	def keyStr(self):
		return str(self.key())
	@property
	def gamersCount(self):
		return self.gamers.count()

###################################################
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

###################################################
class Game(db.Model):
	date = db.DateProperty(required = True)
	wasCalculated = db.BooleanProperty(required = True, default = False)
	# stats
	# achievements
	@property
	def keyStr(self):
		return str(self.key())
	@property
	def gamersCount(self):
		return self.stats.count()

###################################################
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

###################################################
class AchievementType(db.Model):
	name = db.StringProperty(required = True)
	level = db.StringProperty(required = True)
	image = db.LinkProperty(default = None)
	# achievements

###################################################
class Achievement(db.Model):
	achievementType = db.ReferenceProperty(AchievementType, collection_name = 'achievements', required = True)
	game = db.ReferenceProperty(Game, collection_name = 'achievements', required = True)
	gamer = db.ReferenceProperty(Gamer, collection_name = 'achievements', required = True)

######################################################################################################
@db.transactional
@loggingWrapper.CallFunction
def AddGamer(name, nick):
	gamer = Gamer(name = name, nick = nick)
	gamer.put()
	logging.info("Add new Gamer('" + name + "', '" + nick + "').")
	return gamer

###################################################
@db.transactional
@loggingWrapper.CallFunction
def AddGame(date):
	game = Game(
		date = date,
		wasCalculated = False)
	game.put()
	logging.info("Add new Game('" + str(date) + "').")
	return game

###################################################
@loggingWrapper.CallFunction
def GetGamer(name, nick):
	logging.info("Try get gamer by name.")
	gamer = Gamer.gql("WHERE name = :1", name)
	if gamer.count() > 0:
		logging.info("Find gamer.")
		return gamer[0]
	
	logging.info("Try get gamer by nick.")
	gamer = Gamer.gql("WHERE nick = :1", nick)
	if gamer.count() > 1 and not nick == 'None':
		logging.info("Find gamer.")
		return gamer[0]

	logging.info("Try add new gamer.")
	return AddGamer(name, nick)

###################################################
@loggingWrapper.CallFunction
def GetGame(date):
	logging.info("Try get game by date.")
	game = Game.gql("WHERE date = :1", date)
	if game.count() > 0:
		logging.info("Find game.")
		return game[0]

	logging.info("Try add new game.")
	return AddGame(date)

###################################################
@loggingWrapper.CallFunction
def StrToDate(dateAsStr):
	dateAsTime = time.strptime(dateAsStr, "%d.%m.%Y")
	date = datetime.date(dateAsTime.tm_year, dateAsTime.tm_mon, dateAsTime.tm_mday)
	logging.info("Convert '" + str(dateAsTime) + "' to '" + str(date) + "'.")
	return date

###################################################
@loggingWrapper.CallFunction
def ParseLine(line):
	tabulationChar = '\t'
	logging.info("Line to parse '" + line + "'.")
	splitedLine = line.split(tabulationChar)

	splitedLine[0] = StrToDate(splitedLine[0])
	splitedLine[4] = float(splitedLine[4])
	splitedLine[5] = float(splitedLine[5])
	splitedLine[6] = int(splitedLine[6])
	splitedLine[7] = int(splitedLine[7])
	splitedLine[8] = int(splitedLine[8])
	splitedLine[9] = int(splitedLine[9])

	return splitedLine

###################################################
@loggingWrapper.CallFunction
def AddStats(stats):
	for stat in stats:
		game = GetGame(stat[0])
		gamer = GetGamer(stat[2], stat[3])

		# existingStats = Statistic.all().filter('game =', game).filter('gamer =', gamer)
		existingStats = Statistic.gql("WHERE game = :1 AND gamer = :2", game, gamer)
		if existingStats.count() == 0:
			Statistic(
				game = GetGame(stat[0]),
				color = stat[1],
				gamer = GetGamer(stat[2], stat[3]),
				rating = stat[4],
				accuracy = stat[5],
				damage = stat[6],
				countOfDeaths = stat[7],
				countOfInjuries = stat[8],
				usedCartridge = stat[9],
			).put()
			logging.info("Add new Statistic.")
		else:
			logging.info("There is Statistic for thie game and gamer.")

###################################################
@loggingWrapper.CallFunction
def Parse(text):
	newLineChar = '\n'
	text = text.replace('%', '')
	text = text.replace(',', '.')
	lines = text.split(newLineChar)
	stats = []
	for line in lines:
		stats.append(ParseLine(line))
	AddStats(stats)

######################################################################################################
class MainPage(webapp2.RequestHandler):
	def get(self):
		gamers = Gamer.all().order('name')
		commands = Command.all().order('name')
		statistics = Statistic.all().order('-rating')
		games = Game.all().order('date')

		template_values = {
			'gamers': gamers,
			'commands': commands,
			'games': games,
			'statistics': statistics,
		}

		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

###################################################
class GamerPage(webapp2.RequestHandler):
	def get(self):
		gamerKeyStr = self.request.get('key')
		logging.info("gamerKeyStr = " + gamerKeyStr)
		gamer = db.get(db.Key(encoded = gamerKeyStr))
		logging.info("Find gamer = '" + gamer.name + "'.")
		stats = gamer.stats.order('game')

		ratings = []
		for stat in gamer.stats:
			summaryRatingCurrentGame = sum([currentGameStat.rating for currentGameStat in stat.game.stats])
			ratings.append( (stat.game.date, stat.rating / summaryRatingCurrentGame) )
		ratings.sort(key = lambda x: x[0])

		template_values = {
			'gamer': gamer,
			'stats': stats,
			'ratings': ratings,
		}

		template = JINJA_ENVIRONMENT.get_template('gamer.html')
		self.response.write(template.render(template_values))

###################################################
class GamePage(webapp2.RequestHandler):
	def get(self):
		gameKeyStr = self.request.get('key')
		logging.info("gameKeyStr = " + gameKeyStr)
		game = db.get(db.Key(encoded = gameKeyStr))
		logging.info("Find game = '" + str(game.date) + "'.")
		stats = game.stats.order("-rating")

		template_values = {
			'game': game,
			'stats': stats,
		}

		template = JINJA_ENVIRONMENT.get_template('game.html')
		self.response.write(template.render(template_values))

###################################################
class CommandPage(webapp2.RequestHandler):
	def get(self):
		commandKeyStr = self.request.get('key')
		command = db.get(db.Key(encoded = commandKeyStr))
		stats = []
		achievements = []
		for gamer in command.gamers:
			stats.extend(gamer.stats)
			achievements.extend(gamer.achievements)

		# !!! SORT IT !!!

		template_values = {
			'command': command,
			'stats': stats,
			'achievements': achievements,
		}
		template = JINJA_ENVIRONMENT.get_template('commandTemplate.html')
		self.response.write(template.render(template_values))

###################################################
class ImageHandler(webapp2.RequestHandler):
	def get(self, imageKey):
		image = Image.get(imageKey)
		self.response.headers['Content-Type'] = 'image/png'
		self.response.out.write(image.data)

######################################################################################################
app = webapp2.WSGIApplication(
	[('/', MainPage),
	('/gamer', GamerPage),
	('/game', GamePage),
	('/command', CommandPage),
	('/images/(.*)', ImageHandler),
	],
	debug = True)