# -*- coding: utf-8 -*-
from datetime import datetime

def get_first_name():
	name = 'Nobody'
	if auth.user:
		name = auth.user.first_name
	return name

db.define_table('forsalesite',
                Field('name'),
                Field('user_id', db.auth_user),
                Field('date_posted', 'datetime'),
                Field('title'),
                Field('body', 'text'),
                Field('image', 'upload'),
                Field('category'),
                Field('price'),
                Field('available')
                )

db.forsalesite.name.default = get_first_name()
db.forsalesite.name.writable = False
db.forsalesite.date_posted.default = datetime.utcnow()
db.forsalesite.date_posted.writable = False
db.forsalesite.user_id.default = auth.user_id
db.forsalesite.user_id.writable = False
db.forsalesite.user_id.readable = False