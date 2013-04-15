import model

def getGamerKey(gamerKey = None):
	return db.Key.from_path('Gamer', gamerKey)

