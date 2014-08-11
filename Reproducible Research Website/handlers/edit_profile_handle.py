#=================================FUNCTION DESCRITION================================
# The code in this file handles the chefs signup process. It displays the signup form,
# gets the user's input, process them and if all necessary fields were complete and
# consistent with the requirements, it adds the inserted information to the
# corresponding database.
#====================================================================================


#=================INCLUDING THE NECESSARY LIBRARIES AND OTHER FILES==================
import webapp2
from utils import *
from google.appengine.api import images
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from dbs.databases import UserPass_User
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from google.appengine.api import memcache
#====================================================================================


#===================================THE MAIN CODE====================================
class EditProfileHandler(webapp2.RequestHandler):               
     
    #----------------------Display the Form Upon Loading the Page--------------------    
    def get(self):
        
        params_html = {}                                # The list of parametersthat will be passed to the html template
        temp = self.request.cookies.get('user_id')              # Check if the user has signed in
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                params_html['userid'] = userid
                d = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s' " %userid)
                l = d.get()
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
                    params_html['image_key'] = (l.key())
                
            else:
                self.redirect('/login')
        else:
            self.redirect('/login')
        
        params_html['admin_flag'] = admin_flag
        self.response.out.write(template.render('./html/edit_profile_user.html',params_html))            
    #--------------------------------------------------------------------------------             

    #-----------------------Get User's Input and Process Them------------------------
    def post(self):
        params_html = {}                                    # The list of parametersthat will be passed to the html template
        
        #-----------------------Check If the User has Signed In----------------------        
        temp = self.request.cookies.get('user_id')                  # Read the cookies that specify if a user has signed in
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                params_html['userid'] = userid
                d = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s' " %userid)
                l = d.get()
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
                    params_html['image_key'] = (l.key())                    
            else:
                self.redirect('/login')
        else:
            self.redirect('/login')
        params_html['admin_flag'] = admin_flag
        #----------------------------------------------------------------------------
        
        #-------------------------Get User's Inputs----------------------------------
        user_first_name = self.request.get('first_name')            # The first name of the user
        user_last_name = self.request.get('last_name')              # The last name of the user
        user_postal_address = self.request.get('postal_address')    # The postal address of the user        
        user_email = self.request.get('email')                      # The email of the user
        user_weblink = self.request.get('web_link_add')             # The link to the user's personal webpage
        biography = str(self.request.get('user_biography'))         # The user's biography
        isauthor = str(self.request.get('isauthor'))                # Check if the proposed author_ID is correct
        new_photo_added = self.request.get('newlyaddedphoto')       # Check if a new photo is added
        #----------------------------------------------------------------------------
        
        #-Assign HTML Template Parameters in Case we Have to Reload the Signup Page--
        params_html['first_name_value']= str(user_first_name)
        params_html['last_name_value']= str(user_last_name)
        params_html['postal_address_value'] = str(user_postal_address)
        params_html['web_link_value'] = str(user_weblink)        
        #params_html['email_value'] = str(user_email)        
        params_html['biography_value'] = str(biography)
        params_html['image_key'] = l.key()
        user_image = str(self.request.get('user_photo'))        
        user_image = db.Blob(user_image)
        #----------------------------------------------------------------------------
        
        #-----------------Check the Validity of Inserted Information-----------------
        first_name_flag = valid_name(user_first_name)               # Check if the first name is valid
        last_name_flag = valid_name(user_last_name)                 # Check if the last name is valid 
        #biography = valid_name(biography)                           # Check if the restaurant is valid
        postal_address_flag = valid_address(user_postal_address)    # Check if the postal address is valid   
        signup_success_flag = 1
        if user_email:
            if (valid_email(user_email)):
                params_html['email_value'] = str(user_email)
            else:
                signup_success_flag = 0
                params_html['error_email'] = "Email is invalid"
        #----------------------------------------------------------------------------
        
        
        #---------If Everything was Valid, Insert the Info into the Database---------
        if (signup_success_flag):                        
            
            name_updated = 0
            d = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s' " %userid)
            l = d.get()  
            if (l.firstname != str(user_first_name)):
                l.firstname = str(user_first_name)
                name_updated = 1
                
            if (l.lastname != str(user_last_name)):
                l.lastname = str(user_last_name)
                name_updated = 1
                
            l.address = str(user_postal_address)
            l.user_email = user_email    
            l.biography = str(biography)
            if user_weblink:
                l.webpage_link = user_weblink
            else:
                l.webpage_link = None
                
            if user_first_name or user_last_name or user_postal_address or user_email or biography:
                l.created_profile = 1
            
            if new_photo_added:
                l.photo = user_image
            
            
            l.put()
            
            show_profile_flag = 1
            if name_updated:
                author = str(user_first_name) + ' ' + str(user_last_name)
                authorID = str(author.replace(" ", ""))
                user = db.GqlQuery("SELECT * FROM Authors_DB WHERE author_id = '%s'" %authorID)
                user = user.get()
                if user:
                    params_html['ask_author_question'] = 1
                    params_html['author_ID'] = authorID
                    show_profile_flag = 0
                
                
                
            
            if isauthor:
                if (isauthor == 'yes'):
                    author = str(user_first_name) + ' ' + str(user_last_name)
                    authorID = str(author.replace(" ", ""))
                    user = db.GqlQuery("SELECT * FROM Authors_DB WHERE author_id = '%s'" %authorID)
                    user = user.get()
                    if user:
                        params_html['author_ID'] = authorID
                        l.author_id = authorID                        
                        l.put()
                        time.sleep(2)
                    
                    show_profile_flag = 1
            
            if show_profile_flag:                
                self.redirect('/_showprofile')                                       # Redirect the user to the profile page
            else:
                self.response.out.write(template.render('./html/edit_profile_user.html',params_html))
        #----------------------------------------------------------------------------    
            
        #-------Otherwise, Reload the Signup Page with Proper Error Messages---------
        else:
            self.response.out.write(template.render('./html/edit_profile_user.html',params_html))
        #----------------------------------------------------------------------------
        
    #--------------------------------------------------------------------------------
#====================================================================================