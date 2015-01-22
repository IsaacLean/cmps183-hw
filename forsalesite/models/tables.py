# -*- coding: utf-8 -*-

db.define_table('forsalesite',
                Field('name'),
                Field('date_posted', 'datetime'),
                Field('title'),
                Field('body'),
                Field('image'),
                Field('category'),
                Field('price'),
                Field('available')
                )
