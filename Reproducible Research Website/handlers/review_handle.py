import webapp2
from utils import *
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db
from dbs.databases import *

class ReviewHandler(webapp2.RequestHandler):        
    def get(self):
        params = {}
        u = self.request.get('u')
        #b = Orders_DB(rating = 0)
        #b.put()
        #u = make_hashed_cookie('%s' %str(b.key()))
        #943057e9a46648a8d68817518c8196e98575f961bea6309aa77aabba9f725e4b|ahBkZXZ-bWFkZWF0bXlob21lchYLEglPcmRlcnNfREIYgICAgICAgAsM
        order_id = valid_hash_cookie(u)
        #self.response.out.write(order_id)
        
        #----------------------Check If a User Has Signed In-------------------------
        temp = self.request.cookies.get('user_id')
        if temp:
            userid = valid_hash_cookie(temp)
            if userid:
                params['userid'] = userid
                user = db.GqlQuery("SELECT * FROM UserPass_User WHERE user_id = '%s'" %userid)
                user = user.get()
                params['chef_flag'] = user.ischef
        #----------------------------------------------------------------------------
        
        if order_id:
            l = db.get(order_id)            
            params['submitted'] = 0
            if l:
                if l.reviewed:
                    
                    r = db.GqlQuery("SELECT * FROM Reviews_DB WHERE order_id = '%s'" %order_id)
                    r = r.get()
                    
                    params['comments_value'] = unescape_html(r.comments)
                    rating_str = ""
                    for i in range(r.rating_param1):
                        rating_str = rating_str + "<span>&#9733</span>"
                    for i in range(5-r.rating_param1):
                        rating_str = rating_str + "<span>&#9734</span>"
                    params['rating_param1'] = rating_str
                    
                    rating_str = ""
                    for i in range(r.rating_param2):
                        rating_str = rating_str + "<span>&#9733</span>"
                    for i in range(5-r.rating_param2):
                        rating_str = rating_str + "<span>&#9734</span>"
                    params['rating_param2'] = rating_str
                    
                    rating_str = ""
                    for i in range(r.rating_param3):
                        rating_str = rating_str + "<span>&#9733</span>"
                    for i in range(5-r.rating_param3):
                        rating_str = rating_str + "<span>&#9734</span>"
                    params['rating_param3'] = rating_str
                    
                    params['title_value'] = unescape_html(r.title)
                    params['submitted'] = 1
                    self.response.out.write(template.render('./html/review_form.html',params))
                    
                else:
                    self.response.out.write(template.render('./html/review_form.html',params))
            else:
                self.response.out.write('Invalid review link!')
        else:
            self.response.out.write('Invalid review link!')

    def post(self): 
        params = {}
        rate_quality = self.request.get('rating_quality')
        rate_quantity = self.request.get('rating_quantity')
        rate_delivery = self.request.get('rating_delivery')
        
        comments = escape_html(self.request.get('comments'))
        review_title = escape_html(self.request.get('review_title'))
        success_flag = 1
        params['comments_value'] = comments
        params['submitted'] = 0
        params['review_title'] = unescape_html(review_title)
        
        if not (rate_quality and rate_quantity and rate_delivery):
            params['error_rating'] = 'Rating is mandatory!'
            success_flag = 0
        if not review_title:
            review_title = ""
        
        if not comments: 
            comments = ""
            
        if success_flag:
            u = self.request.get('u')        
            order_id = valid_hash_cookie(u)
            ordr = db.get(order_id)
            user_reviewd = ordr.user_id
            if not user_reviewd:
                user_reviewd = "Anonymous"
            ordr.reviewed = 1
            ordr.rating_param1 = int(rate_quality)
            ordr.rating_param2 = int(rate_quantity)
            ordr.rating_param3 = int(rate_delivery)
            rate = int(round((int(rate_quality)+int(rate_quantity))/2))
            ordr.rating = rate 
            ordr.comments = comments
            chef = ordr.chef_id
            ordr.put()
            
            user = db.GqlQuery("SELECT * FROM UserPass_Chef WHERE user_id = '%s'" %chef)
            user = user.get()
            if user:
                #self.response.out.write(rate)
                current_rating = user.user_rating * user.no_reviews
                user.no_reviews = user.no_reviews + 1
                new_rating = current_rating + int(rate)
                new_rating = new_rating / user.no_reviews
                user.user_rating = new_rating
                user.put()
                
                r = Reviews_DB(title=review_title,chef_id = chef,user_id = user_reviewd,comments = comments, order_id = order_id, rating = int(rate),rating_param1 = int(rate_quality),rating_param2 = int(rate_quantity),rating_param3 = int(rate_delivery))
                r.put()            
            else:
                self.response.out.write('No such chef! Wth?!')
                
            #self.response.out.write('Thank you for your time. Your comments will be UPDATED!')
            rating_str = ""
            for i in range(int(rate_quality)):
                rating_str = rating_str + "<span>&#9733</span>"
            for i in range(5-int(rate_quality)):
                rating_str = rating_str + "<span>&#9734</span>"
            params['rating_param1'] = rating_str
                    
            rating_str = ""
            for i in range(int(rate_quantity)):
                rating_str = rating_str + "<span>&#9733</span>"
            for i in range(5-int(rate_quantity)):
                rating_str = rating_str + "<span>&#9734</span>"
            params['rating_param2'] = rating_str
                    
            rating_str = ""
            for i in range(int(rate_delivery)):
                rating_str = rating_str + "<span>&#9733</span>"
            for i in range(5-int(rate_delivery)):
                rating_str = rating_str + "<span>&#9734</span>"
            params['rating_param3'] = rating_str
            
            params['title_value'] = review_title
            params['rating'] = rating_str
            params['submitted'] = 1
            self.response.out.write(template.render('./html/review_form.html',params))
        else:
            self.response.out.write(template.render('./html/review_form.html',params))
            