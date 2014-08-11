from google.appengine.ext import db

class Papers_DB(db.Model):
    title = db.StringProperty(required = True)
    publication_date = db.StringProperty(required = False)
    publication_year = db.IntegerProperty(required = True)
    created_date = db.DateTimeProperty(auto_now_add = True)
    publication_venue = db.TextProperty(required = False)
    publisher = db.TextProperty(required = False)
    keywords = db.ListProperty(unicode)
    whoadded_id = db.StringProperty(required = False)
    publication_type = db.StringProperty(required = False)
    authors = db.ListProperty(unicode)
    authors_str = db.StringProperty(required = True)
    google_scholar_link = db.LinkProperty(required = False)
    abstract = db.TextProperty(required = False)
    publication_status = db.StringProperty(required = False)   #accepted/pending?
    web_link = db.LinkProperty(required = False)
    pdf_link = db.LinkProperty(required = False)
    data_link = db.LinkProperty(required = False)
    code_link = db.LinkProperty(required = False)
    demo_link = db.LinkProperty(required = False)
    biblio_str = db.StringProperty(required = False)
    email_authors = db.ListProperty(str)
    rating = db.IntegerProperty(required = False)
    rating_param1 = db.IntegerProperty(required = False)
    rating_param2 = db.IntegerProperty(required = False)
    rating_param3 = db.IntegerProperty(required = False)
    comments = db.TextProperty(required = False)
    reviewed = db.IntegerProperty(required = False, default = 0)    
    no_views = db.IntegerProperty(required = True, default = 0)
    no_pdf_downloads = db.IntegerProperty(required = True, default = 0)
    no_code_downloads = db.IntegerProperty(required = True, default = 0)
    no_demo_downloads = db.IntegerProperty(required = True, default = 0)
    no_data_downloads = db.IntegerProperty(required = True, default = 0)
    
class Reviews_DB(db.Model):
    chef_id = db.StringProperty(required = True)
    user_id = db.StringProperty(required = False)
    comments = db.TextProperty(required = False)
    order_id = db.StringProperty(required = False)
    rating = db.IntegerProperty(required = False)
    rating_param1 = db.IntegerProperty(required = False)
    rating_param2 = db.IntegerProperty(required = False)
    rating_param3 = db.IntegerProperty(required = False)
    title = db.StringProperty(required = False)
    
class Messages_DB(db.Model):
    sender_id = db.StringProperty(required = True)
    recepient_id = db.StringProperty(required = True)
    message_body = db.TextProperty(required = True)
    created_date = db.DateTimeProperty(auto_now_add = True)
    message_title = db.StringProperty(required = True)
    message_parent = db.StringProperty(required = False)
    read_status = db.IntegerProperty(required = True, default = 0)    
    new_conversation = db.IntegerProperty(required = True, default = 1)

class Authors_DB(db.Model):
    author_id = db.StringProperty(required = True)    
    firstname = db.StringProperty(required = True)
    lastname = db.StringProperty(required = True)
    email_add = db.StringProperty(required = False)
    paper_keys = db.ListProperty(str)
    paper_titles = db.ListProperty(unicode)
    other_authors = db.ListProperty(unicode)
    paper_dates = db.ListProperty(str)
    
class UserPass_User(db.Model):
    user_id = db.StringProperty(required = True)
    user_pass = db.StringProperty(required = True)
    firstname = db.StringProperty(required = False)
    lastname = db.StringProperty(required = False)
    address = db.TextProperty(required = False)
    created_date = db.DateTimeProperty(auto_now_add = True)
    user_email = db.StringProperty(required = False)
    isadmin = db.IntegerProperty(required = True, default = 0)
    isLCAV = db.IntegerProperty(required = True, default = 0)
    biography = db.TextProperty(required = False)
    webpage_link = db.LinkProperty(required = False)
    author_id = db.StringProperty(required = False)
    created_profile = db.IntegerProperty(required = True, default = 0)
    photo = db.BlobProperty(required = False)


class Paper_Clicks_DB(db.Model):
    paperkey = db.StringProperty(required = True)
    no_views = db.IntegerProperty(required = True, default = 0)
    no_pdf_downloads = db.IntegerProperty(required = True, default = 0)
    no_code_downloads = db.IntegerProperty(required = True, default = 0)
    no_demo_downloads = db.IntegerProperty(required = True, default = 0)
    no_data_downloads = db.IntegerProperty(required = True, default = 0)