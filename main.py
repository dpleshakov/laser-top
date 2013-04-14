import webapp2
from google.appengine.ext import db
import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

###################################################
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

###################################################
class MainPage(webapp2.RequestHandler):
	
	def get(self):
		gamers = db.GqlQuery("SELECT * FROM Gamer")
		commands = db.GqlQuery("SELECT * FROM Command")
		statistics = db.GqlQuery("SELECT * FROM Statistic")

		template_values = {
			'gamers': gamers,
			'commands': commands,
			'statistics': statistics,
		}

		template = JINJA_ENVIRONMENT.get_template('index.html')
		self.response.write(template.render(template_values))

class NewPage(webapp2.RequestHandler):
	
	def get(self):
		command = Command(name = "Norfolk")
		command.put()

		gamer = Gamer(name = "Dmitry Pleshakov", nick = "Fearing", command = command)
		gamer.put()
		
		stat = Statistic(rating = 140, gamer = gamer)
		stat.put()

		self.response.headers['Content-Type'] = 'text/plain'
		self.response.write('Added!')

app = webapp2.WSGIApplication(
	[('/', MainPage),
	('/new', NewPage)],
	debug = True)