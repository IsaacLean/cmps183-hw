# -*- coding: utf-8 -*-
from datetime import datetime

def get_first_name():
	name = 'Nobody'
	if auth.user:
		name = auth.user.first_name
	return name

CATEGORY = ['For Sale', 'Wanted', 'Misc']

db.define_table('forsalesite',
                Field('user_id', db.auth_user),
                Field('name'),
                Field('email'),
                Field('date_posted', 'datetime'),
                Field('title'),
                Field('body', 'text'),
                Field('image', 'upload'),
                Field('category'),
                Field('price', 'double'),
                Field('available', 'boolean')
                )

db.forsalesite.name.default = get_first_name()
db.forsalesite.name.writable = False
db.forsalesite.date_posted.default = datetime.utcnow()
db.forsalesite.date_posted.writable = False
db.forsalesite.user_id.default = auth.user_id
db.forsalesite.user_id.writable = False
db.forsalesite.user_id.readable = False
db.forsalesite.email.requires = IS_EMAIL()
db.forsalesite.email.required = True
db.forsalesite.category.requires = IS_IN_SET(CATEGORY)
db.forsalesite.category.required = True
db.forsalesite.price.requires = IS_FLOAT_IN_RANGE(0, 100000.0, error_message='The price should be in the range 0..100000') 