# -*- coding: utf-8 -*-

db.define_table('forsalesite',
                Field('name'),
                Field('date', 'datetime'),
                Field('title'),
                Field('content'),
                Field('image'),
                Field('category'),
                Field('price'),
                Field('available')
                )
