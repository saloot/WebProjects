#=================================FUNCTION DESCRITION================================
# This code is responsible for displaying the chefs' profiles, namely, all the food
# they offer, their favourite recipes, their rating, etc.
#====================================================================================


#=================INCLUDING THE NECESSARY LIBRARIES AND OTHER FILES==================
import webapp2
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from dbs.databases import *
from utils import *
import time
#====================================================================================


#===================================THE MAIN CODE====================================
class AuthorProfileHandler(webapp2.RequestHandler):
    
    #---------------------Display the HTML Template Upon Loading---------------------    
    def get(self):
        
        params_html = {}                         # The list of parametersthat will be passed to the html template
        
        #----------------------Check If a User Has Signed In-------------------------
        admin_flag = 0
        temp = self.request.cookies.get('user_id')
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                params_html['userid'] = userid
                user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
                user = user.get()
                if user:
                    admin_flag = user.isadmin
        
        params_html['admin_flag'] = admin_flag
        #----------------------------------------------------------------------------
        
        #----------------------Get the Author ID From the URL------------------------
        authorID = self.request.get('a')
        author = db.GqlQuery("SELECT * FROM Authors_DB WHERE author_id = '%s'" %authorID)
        author = author.get()
        if not author:
            self.redirect('/404?u=author')
        #----------------------------------------------------------------------------    
        
        #--------------------------If the Chef ID Is Correct-------------------------
        else:            

            #------------------------Assign HTML Parameters--------------------------
            params_html['author_name'] = author.firstname + ' ' + author.lastname
            params_html['author_firstname'] = author.firstname
            params_html['author_email'] = author.email_add
            params_html['papers_list'] = zip(author.paper_titles,author.paper_dates,author.paper_keys,author.other_authors)
            #------------------------------------------------------------------------
            
            #----------Check if Extra Details are Availbale for the Author----------
            user = db.GqlQuery("SELECT * FROM UserPass_User WHERE author_id = '%s'" %authorID)
            user = user.get()
            if user:
                if user.biography:
                    params_html['author_biography'] = user.biography
                if user.photo:
                    params_html['image_key'] = str(user.key())
                if user.webpage_link:
                    params_html['author_webpage'] = user.webpage_link
                if user.user_email:
                    params_html['author_email'] = user.user_email
            #------------------------------------------------------------------------
            
            #----------------------Display the Final HTML File-----------------------
            self.response.out.write(template.render('./html/display_profile.html',params_html))
            #------------------------------------------------------------------------
            
        #----------------------------------------------------------------------------        
            
        
    #--------------------------------------------------------------------------------

#====================================================================================