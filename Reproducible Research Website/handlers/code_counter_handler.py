import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
import time
from dbs.databases import *

class CodeCounterHandler (webapp2.RequestHandler):
  def get(self):
    paper_key =self.request.get('k')    
    pp = db.get(paper_key)
    
    #pp = db.GqlQuery("SELECT * FROM Paper_Clicks_DB WHERE paperkey = '%s'" %paper_key)
    #pp = pp.get()
    if pp:
      pp.no_code_downloads = pp.no_code_downloads + 1
      pp.put()
      self.redirect(str(pp.code_link))
    else:
      self.redirect('/404')
    