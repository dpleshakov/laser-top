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

class Game(db.Model):
	date = db.DateProperty(required = True)
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

class AchievementType(db.Model):
	name = db.StringProperty(required = True)
	level = db.StringProperty(required = True)
	image = db.LinkProperty(default = None)
	# achievements
	
class Achievement(db.Model):
	achievementType = db.ReferenceProperty(AchievementType, collection_name = 'achievements', required = True)
	game = db.ReferenceProperty(Game, collection_name = 'achievements', required = True)
	gamer = db.ReferenceProperty(Gamer, collection_name = 'achievements', required = True)

# def GetAchievementType(name, level):
# 	return AchievementType.all().filter('name = ', name).filter('level = ', level).fetch(1)

# def SetAchievements(currentGame, statisticName, achievementName):
# 	gameStats = currentGame.stats.all().order(statisticName)

# 	Achievement(
# 		achievementType = GetAchievementType(achievementName, "Gold"),
# 		game = currentGame,
# 		gamer = gameStats[0].gamer).put()
# 	Achievement(
# 		achievementType = GetAchievementType(achievementName, "Silver"),
# 		game = currentGame,
# 		gamer = gameStats[1].gamer).put()
# 	Achievement(
# 		achievementType = GetAchievementType(achievementName, "Bronze"),
# 		game = currentGame,
# 		gamer = gameStats[2].gamer).put()

# def RecalculateAchievement():
# 	allGames = Games.all()
# 	for currentGame in allGames:
# 		allStats = currentGame.stats.all()

# 		SetAchievements(currentGame, 'rating', "Warrior")
# 		SetAchievements(currentGame, 'accuracy', "Sniper")
# 		SetAchievements(currentGame, 'countOfDeaths', "Kamikaze")
# 		SetAchievements(currentGame, 'usedCartridge', "Tra-ta-ta")
# 		SetAchievements(currentGame, 'accuracy', "Sniper")

# def GenerateAchievements():
# 	Achievement(name = "Warrior", level = "Gold").put()
# 	Achievement(name = "Warrior", level = "Silver").put()
# 	Achievement(name = "Warrior", level = "Bronze").put()

# 	Achievement(name = "Sniper", level = "Gold").put()
# 	Achievement(name = "Sniper", level = "Silver").put()
# 	Achievement(name = "Sniper", level = "Bronze").put()

# 	Achievement(name = "Kamikaze", level = "Gold").put()
# 	Achievement(name = "Kamikaze", level = "Silver").put()
# 	Achievement(name = "Kamikaze", level = "Bronze").put()

# 	Achievement(name = "Tra-ta-ta", level = "Gold").put()
# 	Achievement(name = "Tra-ta-ta", level = "Silver").put()
# 	Achievement(name = "Tra-ta-ta", level = "Bronze").put()

# 	Achievement(name = "Hero", level = "Gold").put()
# 	Achievement(name = "Hero", level = "Silver").put()
# 	Achievement(name = "Hero", level = "Bronze").put()

# 	Achievement(name = "Collector", level = "Gold").put()
# 	Achievement(name = "Collector", level = "Silver").put()
# 	Achievement(name = "Collector", level = "Bronze").put()
