import datetime, time
import sys
import logging

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
def GetAchievementType(name, level):
	achievementType = AchievementType.all().filter('name = ', name).filter('level = ', level)[0]
	logging.info("Find achievementType = " + achievementType.name + "'")
	return achievementType

###################################################
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
def RecalculateAchievements():
	logging.info("RecalculateAchievements().")
	allGames = Game.all()
	for currentGame in allGames:
		if not currentGame.wasCalculated:
			RecalculateGameOneAchievement(currentGame, 'rating', 'Warrior')
			RecalculateGameOneAchievement(currentGame, 'accuracy', 'Sniper')
			RecalculateGameOneAchievement(currentGame, 'countOfDeaths', 'Kamikaze')
			RecalculateGameOneAchievement(currentGame, 'usedCartridge', 'Tra-ta-ta')
			
			currentGame.wasCalculated = True
			currentGame.put()

###################################################
def GenerateAchievementsTypes():
	logging.info("Initially creating of achievement types.")
	AchievementType(name = "Warrior", level = "Gold").put()
	AchievementType(name = "Warrior", level = "Silver").put()
	AchievementType(name = "Warrior", level = "Bronze").put()

	AchievementType(name = "Sniper", level = "Gold").put()
	AchievementType(name = "Sniper", level = "Silver").put()
	AchievementType(name = "Sniper", level = "Bronze").put()

	AchievementType(name = "Kamikaze", level = "Gold").put()
	AchievementType(name = "Kamikaze", level = "Silver").put()
	AchievementType(name = "Kamikaze", level = "Bronze").put()

	AchievementType(name = "Tra-ta-ta", level = "Gold").put()
	AchievementType(name = "Tra-ta-ta", level = "Silver").put()
	AchievementType(name = "Tra-ta-ta", level = "Bronze").put()

	# AchievementType(name = "Hero", level = "Gold").put()
	# AchievementType(name = "Hero", level = "Silver").put()
	# AchievementType(name = "Hero", level = "Bronze").put()

	# AchievementType(name = "Collector", level = "Gold").put()
	# AchievementType(name = "Collector", level = "Silver").put()
	# AchievementType(name = "Collector", level = "Bronze").put()

######################################################################################################
try:
	if not AchievementType.all().count() > 0:
		GenerateAchievementsTypes()
	RecalculateAchievements()
except:
	logging.error("Error in RecalculateAchievements: " + str(sys.exc_info()[1]))