import webapp2
#from madeathome_forms import form_login
from utils import *
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db


class ChangePasswordHandler(webapp2.RequestHandler):
    
    
    def get(self):
        temp = self.request.cookies.get('user_id')
        userid = ""
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:                
                user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
                user = user.get()
                if user:
                    admin_flag = user.isadmin
                    
                else:
                    self.redirect('/login')
            else:
                self.redirect('/login')
        else:
            self.redirect('/login')
            
        
        params=["","","","unchecked"]
        login_templ_params= {"error_username": params[0], "error_password":params[1],"username_value":params[2],"check_box_val":params[3],"userid":userid}
        login_templ_params['return_url'] = self.request.referer
        self.response.out.write(template.render('./html/change_password.html',login_templ_params))
            
            

    def post(self):
        temp = self.request.cookies.get('user_id')
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
                user = user.get()
                if user:
                    admin_flag = user.isadmin
                    
                else:
                    self.redirect('/login')
            else:
                self.redirect('/login')
        else:
            self.redirect('/login')
            
        params = ["","","","unchecked"]
        success_flag = 1
        
        user_password = self.request.get('current_password')
        

        h = user.user_pass        
        pass_check_flag = valid_hash_pw(userid.lower(), user_password, h)
        if not pass_check_flag:                    
            success_flag = 0
            params[0] = "The current password is not correct"
        else:
            
            new_password = self.request.get('new_password')
            password_flag = valid_pass(new_password)
            
            if not password_flag:
                success_flag = 0
                params[1] = "Inavlid password"            
            else:
                user_password_verify = self.request.get('verify')
                if new_password != user_password_verify:
                    success_flag = 0
                    params[2] = "Passwords should match!"
            
        if success_flag==1:
            
            hashed_val = make_hashed_cookie(userid)
            self.response.headers.add_header('Set-Cookie','user_id=%s' % str(hashed_val))
            user.user_pass = make_hashed_pw(userid.lower(),new_password)
            user.put()
            time.sleep(2)
            
            self.redirect('/_showprofile')
                
        else:                
            login_templ_params= {"error_current_password": params[0], "error_new_password":params[1],'error_password_verify':params[2],'userid':userid}
            
            self.response.out.write(template.render('./html/change_password.html',login_templ_params))
