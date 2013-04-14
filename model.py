from google.appengine.ext import db

class Command(db.Model):
	name = db.StringProperty()

class Gamer(db.Model):
	name = db.StringProperty()
	nick = db.StringProperty()
	command = db.ReferenceProperty(Command)

class Statistic(db.Model):
	date = db.DateProperty()
	color = db.StringProperty()
	countOfDeaths = db.IntegerProperty()
	countOfInjuries = db.IntegerProperty()
	usedCartridge = db.IntegerProperty()
	damage = db.IntegerProperty()
	rating = db.IntegerProperty()
	accuracy = db.IntegerProperty()
	gamer = db.ReferenceProperty(Gamer)