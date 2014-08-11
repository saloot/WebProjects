import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
import time
from dbs.databases import *

class DataCounterHandler (webapp2.RequestHandler):
  def get(self):
    paper_key =self.request.get('k')
    success_flag = 1
    try:
      pp = db.get(paper_key)
          
    except:
      success_flag = 0
    if success_flag:
      pp.no_data_downloads = pp.no_data_downloads + 1
      pp.put()
      self.redirect(str(pp.data_link))
    else:
      self.redirect('/404')
    