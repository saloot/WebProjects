import webapp2
from google.appengine.ext.webapp import template
from google.appengine.api import images
from utils import *
from google.appengine.ext import db
#from dbs.databases import FoodList
#from dbs.databases import UserPass_Chef
from dbs.databases import *
from google.appengine.api import memcache
from datetime import datetime
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images

class NewPostHandler(webapp2.RequestHandler):
    
    def get(self):
        params_new_post = {}
        
        
        temp = self.request.cookies.get('user_id')
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                params_new_post['userid'] = userid
                user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
                user = user.get()
                params_new_post['login_first'] = 0
                
            else:
                params_new_post['login_first'] = 1
        else:
            params_new_post['login_first'] = 1
        
        params_new_post['isactive'] = ["active","0","0"]
        self.response.out.write(template.render('./html/new_post.html',params_new_post))
        
                        
        
        
        
        
        
        
    def post(self): 
        params_new_post = {}  
        paper_title = self.request.get('paper_title')
        
        success_flag = 1
        
        if not paper_title:
            params_new_post['error_title'] = "Title is necessary!"
            params_new_post['title_of_meal'] = ''
            success_flag = 0
        else:
            params_new_post['paper_title_value'] = unescape_html(paper_title)
            
        
            
        if not success_flag:            
            self.response.out.write(template.render('./html/new_post.html',params_new_post))
        else:
            temp = self.request.cookies.get('user_id')
            if not temp:                
                self.redirect('/login')        
                        
            self.redirect('/_import?q=%s' %escape_html2(paper_title))
            
            