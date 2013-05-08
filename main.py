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
class News(db.Model):
	date = db.DateProperty(required = True, default = datetime.datetime.now().date())
	title = db.StringProperty(required = True)
	body = db.Text()

###################################################
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
class MainPage(webapp2.RequestHandler):
	def get(self):
		gamers = Gamer.all().order('name')
		commands = Command.all().order('name')
		statistics = Statistic.all().order('-rating')
		games = Game.all().order('date')
		news = News.all().order('date')

		template_values = {
			'gamers': gamers,
			'commands': commands,
			'games': games,
			'statistics': statistics,
			'news': news,
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