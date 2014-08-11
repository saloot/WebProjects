#=================================FUNCTION DESCRITION================================
# The code in this file handles the chefs signup process. It displays the signup form,
# gets the user's input, process them and if all necessary fields were complete and
# consistent with the requirements, it adds the inserted information to the
# corresponding database.
#====================================================================================


#=================INCLUDING THE NECESSARY LIBRARIES AND OTHER FILES==================
import webapp2
from utils import *
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from dbs.databases import UserPass_User 
#====================================================================================


#===================================THE MAIN CODE====================================
class DisplayProfileHandler(webapp2.RequestHandler):               
     
    #----------------------Display the Form Upon Loading the Page--------------------    
    def get(self):
        
        params_html = {}                                # The list of parametersthat will be passed to the html template
        admin_flag = 0
        temp = self.request.cookies.get('user_id')              # Check if the user has signed in
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                params_html['userid'] = userid
                d = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s' " %userid)
                l = d.get()
                if l:
                    admin_flag = l.isadmin
                params_html['profile_edited'] = l.created_profile
                if l.firstname:
                    params_html['first_name_value']= (l.firstname)
                if l.lastname:
                    params_html['last_name_value']= (l.lastname)
                if l.address:
                    params_html['address_value'] = (l.address)
                if l.user_email:
                    params_html['email_value'] = (l.user_email)
                if l.webpage_link:
                    params_html['web_link_value'] = (l.webpage_link)
                if l.biography:
                    params_html['biography_value'] = (l.biography)
                if l.photo:
                    params_html['image_key'] = str(l.key())                
                if l.author_id:
                    params_html['author_id'] = str(l.author_id)
            else:
                self.redirect('/login')
        else:
            self.redirect('/login')
        
        params_html['admin_flag'] = admin_flag
        self.response.out.write(template.render('./html/display_profile_user.html',params_html))            
    #--------------------------------------------------------------------------------             