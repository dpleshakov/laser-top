# -*- coding: utf-8 -*-

import os
import logging
import sys

import loggingWrapper
import achievements

import webapp2
import jinja2
from google.appengine.ext import db

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
class AdminPage(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('adminPage.html')
		self.response.write(template.render())

###################################################
class AddPage(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('add.html')
		self.response.write(template.render())

	def post(self):
		try:
			Parse(self.request.get('stats'))
			self.redirect('/')
		except:
			template_values = {
				'errors': unicode(sys.exc_info()[1]),
			}

			template = JINJA_ENVIRONMENT.get_template('add.html')
			self.response.write(template.render(template_values))

###################################################
class AddCommand(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('addCommand.html')
		self.response.write(template.render())

	def post(self):
		try:
			commandName = self.request.get('commandName')
			existingCommand = Command.gql("WHERE name = :1", commandName)
			if existingCommand.count() == 0:
				Command(
					name = commandName
				).put()
			self.redirect('/')
		except:
			template_values = {
				'errors': unicode(sys.exc_info()[1]),
			}

			template = JINJA_ENVIRONMENT.get_template('addCommand.html')
			self.response.write(template.render(template_values))

###################################################
class EditCommandPage(webapp2.RequestHandler):
	def get(self):
		commandKeyStr = self.request.get('key')
		command = db.get(db.Key(encoded = commandKeyStr))

		gamers = Gamer.all().filter('command != ', command)

		template_values = {
			'command': command,
			'gamers': gamers,
		}

		template = JINJA_ENVIRONMENT.get_template('editCommand.html')
		self.response.write(template.render(template_values))

	def post(self):
		commandKeyStr = self.request.get('commandKey')
		command = db.get(db.Key(encoded = commandKeyStr))

		addedGamerKeyStr = self.request.get('addedGamer')
		if addedGamerKeyStr:
			addedGamer = db.get(db.Key(encoded = addedGamerKeyStr))
			addedGamer.command = command
			addedGamer.put()

		logo = self.request.get("logo")
		if logo:
			logo = Image(data = images.resize(logo, 20, 20))
			logo.put()

			command.logo = logo
			command.put()
		
		self.redirect('/editCommand?key=' + command.keyStr)

###################################################
class RecalculateAchievementsPage(webapp2.RequestHandler):
	def get(self):
		try:
			achievements.RecalculateAchievements()
		except:
			logging.error("Error in RecalculateAchievements: " + str(sys.exc_info()[1]))

		self.redirect('/admin')

###################################################
class InitializationAchievementsPage(webapp2.RequestHandler):
	def get(self):
		achievements.GenerateAchievementsTypes()

		self.redirect('/admin')

######################################################################################################
app = webapp2.WSGIApplication(
	[('/admin', AdminPage),
	('/admin/add', AddPage),
	('/admin/editCommand', EditCommandPage),
	('/admin/addCommand', AddCommand),
	('/admin/recalculateAchievements', RecalculateAchievementsPage),
	('/admin/initializationAchievements', InitializationAchievementsPage),
	],
	debug = True)