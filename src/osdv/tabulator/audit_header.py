#!/usr/bin/env python
# Python 2.6.2
# Name: audit_header.py
# Author: Mike Anderson
# Created: Sep 2, 2009
# Purpose: To define behaviors and attributes of an audit header class.

from uuid import uuid1
from datetime import datetime

# A data structure and API for audit headers
class AuditHeader(object):    
    def __init__ (self):
        # Put a new GUID into file_id, put a UTC timestamp in
        #  create_date. The other variables are specified by the caller.
        self.file_id = ''
        self.create_date = ''
        self.type = ''
        self.operator = ''
        self.hardware = ''
        self.software = ''
        self.provenance = ''

    # Set the last five data members, generate the first two
    def set_fields (self, type, operator, hardware, software, provenance):
        self.file_id = uuid1().hex.upper()
        self.create_date = datetime.utcnow()
        self.type = type
        self.operator = operator
        self.hardware = hardware
        self.software = software
        self.provenance = provenance
    
    # Loads and deserializes the file_id, type, and provenance of a
    #  ballot header pulled from a given file stream
    def load_from_file(self, stream):
        stream.readline()  # Ignore the title part of the header
        
        temp = stream.readline()
        self.file_id = temp[temp.rfind(' ') + 1:].strip()
               
        stream.readline()
        temp = stream.readline()
        self.type = temp[temp.rfind(' ') + 1:].strip()
        stream.readline()
        stream.readline()
        stream.readline()
                
        temp = stream.readline()        
        prov2_str = temp[temp.find(':') + 2:].strip()
        self.provenance = prov2_str.replace(',','').split()

    # Convert audit header data into an xml formatted string
    def serialize_xml(self):
        return '<audit-header>\n' + \
            '  <file_id>' + self.file_id + '</file_id>\n' + \
            '  <create_date>' + self.stringify_date(self.create_date) + '</create_date>\n' + \
            '  <type>' + self.type + '</type>\n' + \
            '  <operator>' + self.operator + '</operator>\n' + \
            '  <hardware>' + self.hardware + '</hardware>\n' + \
            '  <software>' + self.software + '</software>\n' + \
            '  <provenance>' + self.stringify_list(self.provenance) + '</provenance>\n' + \
            '</audit-header>\n\n\n'

    # Convert audit header data into a yaml formatted string
    def serialize_yaml(self):
        return 'Audit-header:\n' + \
            '  file_id: ' + self.file_id + '\n' + \
            '  create_date: ' + self.stringify_date(self.create_date) + '\n' + \
            '  type: ' + self.type + '\n' + \
            '  operator: ' + self.operator + '\n' + \
            '  hardware: ' + self.hardware + '\n' + \
            '  software: ' + self.software + '\n' + \
            '  provenance: ' + self.stringify_list(self.provenance) + '\n\n\n'

    # Convert a date object to a specific string format
    def stringify_date(self, date):
        # Convert the month number to a string
        if date.month == 1:
            mstr = 'JAN'
        elif date.month == 2:
            mstr = 'FEB'
        elif date.month == 3:
            mstr = 'MAR'
        elif date.month == 4:
            mstr = 'APR'
        elif date.month == 5:
            mstr = 'MAY'
        elif date.month == 6:
            mstr = 'JUN'
        elif date.month == 7:
            mstr = 'JUL'
        elif date.month == 8:
            mstr = 'AUG'
        elif date.month == 9:
            mstr = 'SEP'
        elif date.month == 10:
            mstr = 'OCT'
        elif date.month == 11:
            mstr = 'NOV'
        elif date.month == 12:
            mstr = 'DEC'
        
        # Eliminate the microseconds part of the timestamp
        time = str(date.time())
        time = time[:time.index('.')]
        
        return str(date.day) + '-' + mstr + '-' + str(date.year) + ' ' + time

    # Convert a list into a specific string format
    def stringify_list(self, list_):
        result = ''
        for i in range(len(list_)):
            result += list_[i]
            if list_[i] != list_[len(list_) - 1]:
                result += ', '
        return result
