import webapp2
from utils import *
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db
from dbs.databases import *


class ResetPassHandler(webapp2.RequestHandler):        
    def get(self):
        u = self.request.get('u')        
        user_id = valid_hash_cookie(u)
        if user_id:
            params=["","","","unchecked"]
            login_templ_params= {"success_flag":0,"error_username": params[0], "error_password":params[1],"username_value":params[2],"check_box_val":params[3]}
            self.response.out.write(template.render('./html/reset_password.html',login_templ_params))
        else:
            self.response.out.write('Inavlid username!')
            
            

    def post(self):
        u = self.request.get('u')        
        user_id = valid_hash_cookie(u)
        params_html = {}
        
        #----------------------Check If a User Has Signed In-------------------------        
        if user_id:                        
            user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %user_id)
            user = user.get()
            if not user:                
                self.response.out.write('Inavlid username!')
        else:
            self.response.out.write('Inavlid username!')
        #----------------------------------------------------------------------------
        
        
        password_flag = valid_pass(self.request.get('new_password'))
        
        
        success_flag = 1
        
        if not password_flag:
            success_flag = 0
            params_html['error_new_password'] = "Inavlid password"            
        else:
            user_password = self.request.get('new_password')
            repeated_password = self.request.get('verify')
            
            if (repeated_password != user_password):
                success_flag = 0
                params_html['error_password_verify'] = 'The passwords should match!'
        
        params_html['success_flag'] = success_flag       
        if success_flag==1:
            user.user_pass = make_hashed_pw(user_id.lower(),user_password)
            user.put()
            
            
        self.response.out.write(template.render('./html/reset_password.html',params_html))
