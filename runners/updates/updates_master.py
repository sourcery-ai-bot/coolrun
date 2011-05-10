#! /usr/bin/python -tt
########################################################################
# Copyright (c) 2011 by Vinny Murphy
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
########################################################################

import csv
import dateutil.parser as dparser
import os
import re
import sys

top_dir = os.path.abspath(os.path.join(\
        os.path.dirname(os.path.dirname(__file__)), '..', '..', '..'))
sys.path.insert(0, top_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'coolrun.settings'

from coolrun.runners.models import City, Address
from coolrun.runners.models import Club, Runner
from django.db import IntegrityError
from datetime import date
from pprint import pprint

THIS_DIR = os.path.dirname(__file__)

# grab the csv file and put it into the database.
update = os.path.join(THIS_DIR, 'latest.csv')
dr = csv.DictReader(open(update))

# The csv files fields are:
# id,firstname,MI,lastname,suffix,street_#,street,city,state,zip,
# mobilephone,homephone,dob,email,Member Since,Type,gender,Comp?,
# Exp,eNewsletter,mailit,Age
for row in dr:
    '''TODO: do a try block here because not all cities are in the zip
    file'''
    city_obj, city_created = City.objects.get_or_create(zipcode=row['zip'])
    addr_obj, addr_created = Address.objects.get_or_create(
        number=row['street_#'],
        street=row['street'],
        city=city_obj)
    if row['dob']:
        if re.match(r'\d+/\d+/\d+', row['dob']):
            dob = dparser.parse(row['dob'])
            if dob.year > date.today().year:
                '''most likely they are not more than 100 years old'''
                dob = dob.replace(year=dob.year - 100)
    try:
        runner_obj, runner_created = Runner.objects.get_or_create(
            first_name=row['firstname'],
            gender=row['gender'].upper(),
            phone=row['homephone'],
            mobile=row['mobilephone'],
            sur_name=row['lastname'],
            address=addr_obj,
            email=row['email'],
            dob=dob)
    except IntegrityError, e:
        '''it barfed for some reason. :-('''
        print 'wtf',
        print row['firstname'], row['lastname'], row['dob']
        
    if runner_created:
        print 'created %s %s' % (row['firstname'], row['lastname'])
