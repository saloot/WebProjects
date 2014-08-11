import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
import time
from dbs.databases import *

class ImageHandler (webapp2.RequestHandler):
  def get(self):
    user_key=self.request.get('k')    
    user = db.get(user_key)
    if user:
      if user.photo:        
        self.response.headers['Content-Type'] = "image/png"
        self.response.out.write(user.photo)
    else:
      self.error(404)
    