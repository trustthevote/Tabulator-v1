"""
Developed with Python 2.6.2
Name: audit_header.py
Author: Mike Anderson
Created: Sep 2, 2009
Purpose: To define behaviors and attributes of an audit header class.
"""

from uuid import uuid1
from datetime import datetime

class AuditHeader(object):

    """
    A data structure and API for voting machine audit headers
    """

    def __init__ (self):
        self.file_id = ''
        self.create_date = ''
        self.type = ''
        self.operator = ''
        self.hardware = ''
        self.software = ''
        self.provenance = ''

    def set_fields (self, type, operator, hardware, software, provenance):
        """
        Initialize the data members of an audit header object
        """
        
        #Generate the first two data members, set the last five
        self.file_id = uuid1().hex.upper()
        self.create_date = datetime.utcnow()
        self.type = type
        self.operator = operator
        self.hardware = hardware
        self.software = software
        self.provenance = provenance
    
    def load_from_file(self, stream):
        """
        Loads and deserializes the file_id, type, and provenance of a
         ballot header pulled from a given file stream
        """
        
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

    def serialize_xml(self):
        """
        Convert audit header data into an xml formatted string
        """
        
        return '\n'.join(['<audit-header>',
         '  <file_id>%s</file_id>' % self.file_id,
         '  <create_date>%s</create_date>' % self.stringify_date(self.create_date),
         '  <type>%s</type>' % self.type,
         '  <operator>%s</operator>' % self.operator,
         '  <hardware>%s</hardware>' % self.hardware,
         '  <software>%s</software>' % self.software,
         '  <provenance>%s</provenance>' % ', '.join(self.provenance),
         '</audit-header>\n\n\n'])

    def serialize_yaml(self):
        """
        Convert audit header data into a yaml formatted string
        """

        return '\n'.join(['Audit-header:',
         '  file_id: %s' % self.file_id,
         '  create_date: %s' % self.stringify_date(self.create_date),
         '  type: %s' % self.type,
         '  operator: %s' % self.operator,
         '  hardware: %s' % self.hardware,
         '  software: %s' % self.software,
         '  provenance: %s\n\n\n' % ', '.join(self.provenance)])

    def stringify_date(self, date):
        """
        Convert a date object to a specific string format
        """

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
        
        return '%d-%s-%d %s' % (date.day, mstr, date.year, time)
