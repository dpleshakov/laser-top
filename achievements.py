# -*- coding: utf-8 -*-

import datetime, time
import sys

import logging
import loggingWrapper

from google.appengine.ext import db

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
@loggingWrapper.CallFunction
def GetAchievementType(name, level):
	achievementType = AchievementType.all().filter('name = ', name).filter('level = ', level)[0]
	logging.info("Find achievementType = " + achievementType.name + "'")
	return achievementType

###################################################
@loggingWrapper.CallFunction
def RecalculateGameOneAchievement(game, statisticName, achievementName):
	logging.info("RecalculateGameOneAchievement('" + str(game.date) + "', '" + statisticName + "', '" + achievementName + "').")
	stats = game.stats.order("-" + statisticName)
	if stats.count() > 0:
		achievement = Achievement(
			achievementType = GetAchievementType(achievementName, "Gold"),
			game = game,
			gamer = stats[0].gamer)
		achievement.put()
		logging.info("Add gold achievement '" + achievementName + "'.")
	if stats.count() > 1:
		achievement = Achievement(
			achievementType = GetAchievementType(achievementName, "Silver"),
			game = game,
			gamer = stats[1].gamer)
		achievement.put()
		logging.info("Add silver achievement '" + achievementName + "'.")
	if stats.count() > 2:
		achievement = Achievement(
			achievementType = GetAchievementType(achievementName, "Bronze"),
			game = game,
			gamer = stats[2].gamer)
		achievement.put()
		logging.info("Add bronze achievement '" + achievementName + "'.")

###################################################
@loggingWrapper.CallFunction
def RecalculateAchievements():
	logging.info("RecalculateAchievements().")
	
	# Recalculate ordinary achievements
	allGames = Game.all()
	for currentGame in allGames:
		if not currentGame.wasCalculated:
			RecalculateGameOneAchievement(currentGame, 'rating', 'Воин')
			RecalculateGameOneAchievement(currentGame, 'accuracy', 'Снайпер')
			RecalculateGameOneAchievement(currentGame, 'countOfDeaths', 'Камикадзе')
			RecalculateGameOneAchievement(currentGame, 'used', 'Тра-та-та')
			
			currentGame.wasCalculated = True
			currentGame.put()

	# # Recalculate legendary achievements
	# allGamers = Gamer.all()
	# for currentGamer in allGamers:
	# 	achievementsTypes = [currentAchievement.achievementType for currentAchievement in currentGamer.achievements]

###################################################
@loggingWrapper.CallFunction
def GenerateAchievementsTypes():
	logging.info("Initially creating of achievement types.")
	# Ordinary
	AchievementType(name = "Воин", level = "Золото").put()
	AchievementType(name = "Воин", level = "Серебро").put()
	AchievementType(name = "Воин", level = "Бронза").put()

	AchievementType(name = "Снайпер", level = "Золото").put()
	AchievementType(name = "Снайпер", level = "Серебро").put()
	AchievementType(name = "Снайпер", level = "Бронза").put()

	AchievementType(name = "Камикадзе", level = "Золото").put()
	AchievementType(name = "Камикадзе", level = "Серебро").put()
	AchievementType(name = "Камикадзе", level = "Бронза").put()

	AchievementType(name = "Тра-та-та", level = "Золото").put()
	AchievementType(name = "Тра-та-та", level = "Серебро").put()
	AchievementType(name = "Тра-та-та", level = "Бронза").put()

	# # Legendary
	# AchievementType(name = "Герой", level = "Gold").put()
	# AchievementType(name = "Герой", level = "Silver").put()
	# AchievementType(name = "Герой", level = "Bronze").put()

	# AchievementType(name = "Коллекционер", level = "Gold").put()
	# AchievementType(name = "Коллекционер", level = "Silver").put()
	# AchievementType(name = "Коллекционер", level = "Bronze").put()

######################################################################################################