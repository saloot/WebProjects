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
class ChefShowReview(webapp2.RequestHandler):
    
    #---------------------Display the HTML Template Upon Loading---------------------    
    def get(self):        
        
        params_review = {}                         # The list of parametersthat will be passed to the html template
        
        #----------------------Check If a User Has Signed In-------------------------
        temp = self.request.cookies.get('user_id')
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                params_review['userid'] = userid
                user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
                user = user.get()
                params_review['chef_flag'] = user.ischef
        #----------------------------------------------------------------------------
        
        #-----------------------Get the Chef ID From the URL-------------------------
        u = self.request.get('u')
        s = self.request.get('s')
        
        chef = db.GqlQuery("SELECT * FROM UserPass_Chef WHERE user_id = '%s'" %u)
        chef = chef.get()
        if not chef:
            self.redirect('/404?u=chef')
        #----------------------------------------------------------------------------    
        
        #--------------------------If the Chef ID Is Correct-------------------------
        else:            

            #------------------------Chef's Complete Name----------------------------
            params_review['chef_name'] = chef.user_firstname + ' ' + chef.user_lastname
            #------------------------------------------------------------------------
            
            #-----------------------Extract Chef's Rating----------------------------
            rating_str = ""             
            for i in range(int(chef.user_rating)):
                rating_str = rating_str + "<span>&#9733</span>"
            for i in range(5-int(chef.user_rating)):
                rating_str = rating_str + "<span>&#9734</span>"
            #------------------------------------------------------------------------ 
                                        
            #-------------------Find the Meals Offerd by the Chef--------------------
            no_1stars = 0
            no_2stars = 0
            no_3stars = 0
            no_4stars = 0
            no_5stars = 0
            
            review_list = []                             # The list of meals offered by the chef
            reviews = db.GqlQuery("SELECT * FROM Reviews_DB WHERE chef_id = '%s'" %u)
            if reviews:                
                for review in reviews:                    
                    if review.rating == 1:
                        no_1stars = no_1stars + 1    
                    elif review.rating == 2:
                        no_2stars = no_2stars + 1
                    elif review.rating == 3:
                        no_3stars = no_3stars + 1
                    elif review.rating == 4:
                        no_4stars = no_4stars + 1
                    else:
                        no_5stars = no_5stars + 1
                        
                    if review.comments:
                        review_specifications = []                                        
                        review_specifications.append(unescape_html(review.comments))
                        review_str = ""             
                        for i in range(int(review.rating)):
                            review_str = review_str + "<span>&#9733</span>"
                        for i in range(5-int(review.rating)):
                            review_str = review_str + "<span>&#9734</span>"
                            
                        review_specifications.append(review_str)
                        review_specifications.append(unescape_html(review.title))
                        if s:
                            if review.rating == int(s):
                                review_list.append(review_specifications)
                        else:
                            review_list.append(review_specifications)
            #------------------------------------------------------------------------
            
            #-------------------Assign the HTML Template Parameters------------------
            summ = no_1stars + no_2stars + no_3stars + no_4stars + no_5stars
            
            if summ == 0:
                summ = 0.0001;
                
            params_review['star1_percent'] = no_1stars
            params_review['star2_percent'] = no_2stars
            params_review['star3_percent'] = no_3stars
            params_review['star4_percent'] = no_4stars
            params_review['star5_percent'] = no_5stars
            params_review['no_reviews'] = summ
            params_review['review_list'] = review_list 
            params_review['chef_rating'] = rating_str               
            params_review['no_reviews'] = chef.no_reviews
            params_review['chef_id'] = chef.user_id
            #------------------------------------------------------------------------
            
            #----------------------Display the Final HTML File-----------------------
            self.response.out.write(template.render('./html/display_reviews.html',params_review))
            #------------------------------------------------------------------------
            
        #----------------------------------------------------------------------------        
            
        
    #--------------------------------------------------------------------------------

#====================================================================================bb