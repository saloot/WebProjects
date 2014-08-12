import webapp2
from utils import *
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.api import mail

class ForgotPasswordHandler(webapp2.RequestHandler):
    
    
    def get(self):
        
        params=["","","","unchecked"]
        login_templ_params= {"error_username": params[0], "error_password":params[1],"username_value":params[2],"check_box_val":params[3]}
        login_templ_params['return_url'] = self.request.referer
        self.response.out.write(template.render('./html/forgot_password.html',login_templ_params))
            
            

    def post(self):
        params_html = {}
        success_flag = 1
        userid = self.request.get('user_name')
        if userid:
            user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
            user = user.get()
            if not user:
                success_flag = 0
                params_html['error_user'] = 'Invalid username'
                params_html['user_name_value'] = userid
            
        else:
            success_flag = 0
            params_html['error_user'] = 'Username is necessary'
            
        
        params_html['success_flag'] = success_flag
        if success_flag:            
            user_email_add  = user.user_id        
            u = make_hashed_cookie('%s' %user_email_add )
            
            #==============SEND THE REVIEW EMAIL TO THE USER=============
            str0 = '<html> <head><style> td{text-align:center;}</style></head> <body>'
            email_body = '<table cellpadding="0" cellspacing="0" border="0" align="center"> '
            email_body = email_body + '<td width="600" valign="top"><h3><span style="color:#888888">It seems that you have forgotten your password.</span></h3><h4><span style="color:#888888">Please click <a href="%s/_resetpassword?u=%s">here</a> to reset your password</span></h4></tr></tbody></table>'%(home_site,u)
            str3 = '</body></html>'
            msg_content = str0 + email_body  + str3
            message = mail.EmailMessage(sender="Amir Hesam Salavati <saloot@gmail.com>",
            subject="Reset password instructions")
            message.to = "%s" %str(user_email_add)
            message.html = """%s""" %msg_content
                        
   
            message.send()
            #==================================================================
        
                
                                    
        self.response.out.write(template.render('./html/forgot_password.html',params_html))
