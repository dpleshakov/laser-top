from google.appengine.ext import db

class Command(db.Model):
	name = db.StringProperty(required = True)
	# gamers

class Gamer(db.Model):
	name = db.StringProperty(required = True)
	nick = db.StringProperty()
	command = db.ReferenceProperty(Command, collection_name = 'gamers')
	# stats
	# achievements

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

class Achievement(db.Model):
	achievementType = db.ReferenceProperty(AchievementType, collection_name = 'achievements', required = True)
	game = db.ReferenceProperty(Game, collection_name = 'achievements', required = True)
	gamer = db.ReferenceProperty(Gamer, collection_name = 'achievements', required = True)

class AchievementType(db.Model):
	name = db.StringProperty(required = True)
	level = db.StringProperty(required = True)
	image = db.LinkProperty(default = None)
	# achievements

class Game(db.Model):
	date = db.DateProperty(required = True)
	# stats
	# achievements

def GetAchievementType(name, level):
	return AchievementType.all().filter('name = ', name).filter('level = ', level).fetch(1)

def SetAchievements(game, gameStat, achievementName):
	

def RecalculateGameOneAchievement(game, statisticName, achievementName):
	 stats = game.stats.all().order(statisticName)
	 Achievement(
		achievementType = GetAchievementType(achievementName, "Gold"),
		game = game,
		gamer = stats[0].gamer).put()
	Achievement(
		achievementType = GetAchievementType(achievementName, "Silver"),
		game = game,
		gamer = stats[1].gamer).put()
	Achievement(
		achievementType = GetAchievementType(achievementName, "Bronze"),
		game = game,
		gamer = stats[2].gamer).put()

def RecalculateGameAchievements(game):
	

def RecalculateAchievement():
	allGames = Games.all()
	for currentGame in allGames:
		RecalculateGameOneAchievement(currentGame, 'rating', 'Warrior')
		RecalculateGameOneAchievement(currentGame, 'accuracy', 'Sniper')
		RecalculateGameOneAchievement(currentGame, 'countOfDeaths', 'Kamikaze')
		RecalculateGameOneAchievement(currentGame, 'usedCartridge', 'Tra-ta-ta')

def GenerateAchievementsTypes():
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
