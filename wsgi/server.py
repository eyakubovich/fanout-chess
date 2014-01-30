import os
import uuid
import bottle
import requests
import json

import time
from base64 import b64decode
import jwt

import redis

FO_REALM_ID = '83b2cca6'
FO_REALM_KEY = os.environ['FO_REALM_KEY']
STATIC_ROOT = './static'

class FanoutClient:
	def __init__(self, realm, key):
		self.realm = realm
		self.key = b64decode(key)
		claim = dict(iss=realm, exp=int(time.time()) + 7*24*3600)
		self.token = jwt.encode(claim, self.key).decode()

	def publish(self, channel, msg):
		url = 'https://api.fanout.io/realm/{}/publish/{}/'.format(self.realm, channel)
		hdrs = {
			'Authorization': 'Bearer ' + self.token,
			'Content-Type': 'application/json'
		}

		data = {
			'items': [
				{ 'fpp': msg }
			]
		}
		data = json.dumps(data)

		requests.post(url, headers=hdrs, data=data).raise_for_status()

class Game:
	def __init__(self, data=None):
		if data:
			vars(self).update(json.loads(data.decode()))
		else:
			self.board = ''
			self.white_turn = True
			self.joinable = True

	def move(self, pos, is_white):
		if is_white != self.white_turn:
			raise RuntimeError('wrong turn')
		self.board = pos
		self.white_turn = not self.white_turn

	def join(self):
		if not self.joinable:
			raise RuntimeError('game already in progress')
		self.joinable = False

	def __str__(self):
		return json.dumps(vars(self))

class GamesCollection:
	def __init__(self):
		host = os.environ.get('OPENSHIFT_REDIS_HOST', 'localhost')
		port = os.environ.get('OPENSHIFT_REDIS_PORT', 6379)
		passwd = os.environ.get('REDIS_PASSWORD')
		
		self.r = redis.StrictRedis(host=host, port=int(port), password=passwd)

	def get(self, gameid):
		game = self.r.get(gameid)
		return Game(game) if game else None

	def set(self, gameid, game):
		self.r.set(gameid, str(game))

	def items(self):
		for gameid in self.r.keys():
			yield gameid, self.get(gameid)

@bottle.get('/')
@bottle.view('index')
def index():
	return dict(games=games)

@bottle.post('/games')
def new_game():
	game_id = uuid.uuid1().hex
	games.set(game_id, Game())
	bottle.redirect('/games/{}/?side=white'.format(game_id))

@bottle.post('/games/<game_id>/join')
def join_game(game_id):
	game = games.get(game_id) or bottle.abort(404)
	game.join()
	games.set(game_id, game)
	bottle.redirect('/games/{}/?side=black'.format(game_id))
	
@bottle.post('/games/<game_id>/move')
def move(game_id):
	forms = bottle.request.forms
	game = games.get(game_id) or bottle.abort(404)
	pos = forms.get('pos') or bottle.abort(400, 'pos field missing')
	mv = forms.get('move') or bottle.abort(400, 'move field missing')
	side = forms.get('side') or bottle.abort(400, 'side filed missing')
	is_white = (side == 'w')

	game.move(pos, is_white)
	games.set(game_id, game)

	fanout.publish(game_id, dict(move=mv, side=side))

@bottle.get('/games/<game_id>/')
@bottle.view('game')
def get_game(game_id):
	side = bottle.request.query.get('side', '')
	game = games.get(game_id) or bottle.abort(404)
	return dict(game_id=game_id, game=game, side=side)

@bottle.get('/static/<path:path>')
def statics(path):
	return bottle.static_file(path, root=STATIC_ROOT)

games = GamesCollection()

fanout = FanoutClient(FO_REALM_ID, FO_REALM_KEY)

# This must be added in order to do correct path lookups for the views
try:
	bottle.TEMPLATE_PATH.append(os.path.join(os.environ['OPENSHIFT_HOMEDIR'], 'runtime/repo/wsgi/views/')) 
except KeyError:
	pass

application=bottle.default_app()

if __name__ == '__main__':
	application.run()
