#!/usr/bin/env python
# coding: utf-8

# ## Class Object to downlaod and parse IRS 990 forms

# In[1]:


import os, sys

import json
import pprint
import numpy as np
import pandas as pd
import urllib.request
from IPython.display import display, HTML
import xml.etree.cElementTree as et
from irsx.xmlrunner import XMLRunner
from collections import defaultdict
from pymongo import MongoClient


# In[2]:


# Global variables
cache = os.environ['IRSX_INDEX_DIRECTORY']
indexURL = 'https://s3.amazonaws.com/irs-form-990/index_%d.json'
pcklFile = cache + '/IRS990_%d.pkl' 


# # MongoDB
# 
# Keep all MongoDB configuration in one simple object

# In[3]:


class Mongo990():
    
    def __init__( self, uri=False, year=False, dump=False):
        
        self.uri = uri
        self.dbName = 'irs990'
        self.year = year
        
        self.db = None
        self.collection = None
        self.client = None
        
        # if we have all the info then connect
        if year and uri:
            self.connect()
            if dump:
                self.dump()
            
    def dump( self ):
        '''
        If we already have documents then drop them and start
        clean on empty collection
        '''
        
        self.verify()
        
        print( 'Drop database and start over with archive')
        self.collection.drop()
    
    def close( self ):
        '''
        Try to close and clean the connection to the db
        '''
        
        print( 'Close connection to [%s] [%s]' % (self.dbName, self.year) )
        try:
            self.client.close()
            print( 'Success on close for [%s]' % self.year )
        except:
            print( 'ERROR: Some problem during close command' )
        
    def reconnect( self ):
        
        self.close()
        self.connect()
        
    def connect( self, uri=False, year=False ):
        '''
        Primary method to connect to db
        '''
        
        if not self.uri:
            print( 'ERROR: Need URI for database.')
            return
        
        # host connection
        print( 'Connect to: [%s]' % self.uri )
        self.client = MongoClient( self.uri )

        print( 'List of databases in MongoDB: %s' % self.client.list_database_names() )

        # database
        print( 'Open db: [%s]' % self.dbName )
        self.db = self.client[ self.dbName ]
        
        # collection
        print( 'Collection: [%s]' % self.year )
        self.collection = self.db['%s' % self.year]
        
        self.verify()
        
    def server_info():
        print( self.client.server_info() )
    
    def verify( self ):
        
        try:
            total = self.collection.count_documents({})
        except Exception as e:
            #self.reconnect()
            print( 'ERROR: Some problem while trying to veirfy MongoDB\n%s' % e)
            total = 'unknown'
            
        print( '%s documents present' % total )
    
    def __del__( self ):
        '''
        Once we remove the object then we close the connection
        '''
        self.close()


# ## AWSparser
# This is a class dedicated to tracking the multiple fields that we
# have in all 990 forms. There is a configuration file that contains
# the list of all "flat-path" fields listed in the IRSx module. I got
# the list by calling the `list_variables` method on this object and
# saving the output to a file. Then I added the logic to read this
# file back and reject all lines starting with a # and setting
# to "use:True" the rest.

# In[4]:


class AWSparser():
    def __init__( self, config=False ):
    
        self.xml_runner = XMLRunner()
        self.variables = defaultdict(dict)
        self.variable_names = dict()
        self.validVariables = set()
        
        if config:
            # Read configuration file from disk
            #print( 'open config: %s' % config )
            with open(config) as fp:  
                for line in fp:
                    if line[0] == '#':
                        pass
                    else:
                        self.validVariables.add( line.strip() )

        # Prep definitions of variables from IRSx module
        for test in  self.xml_runner.standardizer.variables:
            each = self.xml_runner.standardizer.variables[test]
            self.variables[ each['db_table'] ][ each['db_name'] ] = test
            
        # Make list on final names of variables
        for x in self.variables:
            for y in self.variables[x]:
                self.variable_names[ self.variables[x][y] ] = { 
                    'table':x, 
                    'field':y, 
                    'use':  self.variables[x][y] in self.validVariables 
                }
            
    def list_variables( self, name=False ):
        '''
        Print list of valid variable names. just the final representation
        of them. Not the original object names on the form.
        '''
        if name and name in self.variable_names:
            return self.variable_names[ name ]
        
        return sorted(set(self.variable_names.keys()))


# # Filing
# 
# This class will process the information of the 990. It will download the
# information of an ID directly from AWS and will convert the nested structure
# into something that we can upload into MongoDB. We could keep one structure
# for each FORM that we download but it will consume too much memory. The
# correct model is to create a new object with new metadata and let the
# previous object go into a cleanup sequence in the interpreter. That will
# trigger the __del__ method and it will take care of the cleanup of the
# temporary XML file created by the IRSx module. We should only have one object
# active at any given time.

# In[5]:


class Filing(AWSparser):
    def __init__( self, config=False, mongo=False, **metadata ):
    
        AWSparser.__init__(self, config)
        
        self.activeRaw = None
        self.active = dict()
        self.filePath = None
        self.id = None
        self.ein = None
        self.dln = None
        self.url = None
        self.mongo= None
        self.index = None
        self.formType = None
        self.taxPeriod = None
        self.lastUpdated = None
        self.submittedOn = None
        self.organization = None
        self.metadata = dict()
        
        if metadata:
            self.setMetadata( metadata )
            self.get()
        
        if mongo:
            self.mongo = mongo
            
            
    def setMetadata( self, info ):
        '''
        Populate the metadata of this document
        '''
        
        self.metadata = info
        
        self.ein = info['EIN']
        self.dln = info['DLN']
        self.url = info['URL']
        self.id = info['ObjectId']
        self.formType = info['FormType']
        self.taxPeriod = info['TaxPeriod']
        self.lastUpdated = info['LastUpdated']
        self.submittedOn = info['SubmittedOn']
        self.organization = info['OrganizationName']
        
        self.index = "%s_%s" % ( info['EIN'], info['TaxPeriod'])
        
        # Example:
        #      EIN                 042662873
        #      TaxPeriod           201603
        #      DLN                 93493243000066
        #      FormType            990
        #      URL                 https://s3.amazonaws.com/irs-form-990/...
        #      OrganizationName    ELKS BUILDING CORP OF NORWOOD
        #      SubmittedOn         2017-01-04
        #      ObjectId            201612439349300006
        #      LastUpdated         2017-01-11T22:15:15
        
        
    def display( self ):
        '''
        Nice (native pandas) print of the DataFrame 990 data
        
        '''
        
        if not len(self.active):
            print( 'ERROR: Internal cache is empty!')
            return
        
        display( self.active )
        
    
    def __str__(self):
        '''
        Metadata representation of the object.
        '''
        
        text =  '''
        EIN         [%s]
        Name        [%s]
        TaxPeriod   [%s]
        DLN         [%s]
        FormType    [%s]
        SubmittedOn [%s]
        ObjectId    [%s]
        LastUpdated [%s]
        [%s]
        ''' % ( self.ein, self.organization, self.taxPeriod, self.dln, 
        self.formType, self.submittedOn, self.id, self.lastUpdated, self.url )
        
        return text
    
    def __del__(self):
        # Remove temp file if possible
        try:
            os.remove( self.filePath )
        except:
            pass
        
    def __repr__(self):
        return str(pprint.pprint(self.active))

    def __getitem__(self, item):
        if item in self.active:
            return self.active[item]
        else:
            return None
    
    def info( self ):
        return self.__str__()
    
    def _getRaw( self ):
        '''
        Download the actual 990 form from AWS using IRSx tools
        '''
        self.activeRaw = self.xml_runner.run_filing( self.id, verbose=False )
        
    def json( self ):
        '''
        Convert to JSON format. Needed for MongoDB uploads
        '''
        return json.dumps( self.active )
    
    def to_mongo( self, upsert=True ):
        '''
        Sent values of form to MongoDB
        '''
        if not self.mongo:
            print( 'ERROR: Missing MongoDB configuration. Skip.' )
        else:
            #self.mongo.verify()
            try:
                self.mongo.collection.update_one( {"_id" : self.index}, {"$set":self.active}, upsert=upsert )
            except Exception as e:
                print( 'ERROR: Problem during MongoDB insert. \n %s' % e )
        
        
    def get( self, **metadata ):
        '''
        Download the actual 990 form from AWS using IRSx tools
        '''
        
        if metadata:
            self.setMetadata( metadata )
        
        #print( 'Get Form: [%s]' % self.id )
        self._getRaw()
        
        # save path of temp file for cleanup later
        self.filePath = self.activeRaw.get_filepath()
        
        # convert to normalized dict
        self.parse()
        
        self.active.update(self.metadata)
    
    def list_schedules( self ): 
        '''
        Return a list of all valid segments on the active form.
        '''
        
        if self.activeRaw:
            return self.activeRaw.list_schedules()
        else:
            print( 'ERROR: No active form selected!' )
            return None
        
    def parse( self ):
        '''
        Convert active object to final flat format.
        '''
        
        if self.activeRaw:
            temp = dict()
            for sked in self.activeRaw.get_result():
                #print("Segment: %s" % sked['schedule_name'])  
                for x in sked['schedule_parts']:
                    for y in sked['schedule_parts'][x]:
                        
                        # verify if we set the value off
                        if x in self.variables and y in self.variables[x]                             and not self.variable_names[ self.variables[x][y] ]['use']:
                            continue
                            
                        # try to flatten the name
                        try:
                            # clean a bit
                            if not sked['schedule_parts'][x][y]: continue
                            if sked['schedule_parts'][x][y] == 'false': continue
                                
                            # one level only
                            temp[ self.variables[x][y] ] = sked['schedule_parts'][x][y]
                            
                        except:
                            if not y in ['object_id', 'ein']:
                                print( 'ERROR on %s.%s.%s' % (sked['schedule_parts'], x, y) )
                                
                                
            # replace original object
            self.active = temp
                    
        else:
            self.active = dict()
            print( 'ERROR: No active form selected!' )


# # classy990forms
# 
# Superclass that we need to handle the year index provided by the AWS framework. We could
# allow the IRSx tool to download the index directly but it's just a black box that provides
# no viable way for discriminating between filings that we want to download or skip. We get
# the IRS index in JSON format directly from AWS and convert that into a native dictionary
# object. Then we save this dictionary into a Pickel file that we can access quickly from the
# executable on subsequent runs. Then we can send the object itself into an iterator that will
# return each "row" on the index as a Form object that automatically populates itself
# with AWS information. Once the iterator returns the next value you should be able to send the
# values of the Form to MongoDB or any other process. Then the next loop will give you a new object
# and the previous one will be deleted by the garbage collector. That process also cleans the
# temporary files created by the IRSx download.
# 

# In[6]:


class classy990forms(AWSparser):
    def __init__( self, year=False, config=False, mongo=False, debug=False ):
    
        AWSparser.__init__(self, config)
        
        self.index = 0
        self.debug = debug
        self.set_year = year
        self.sourceURL = False
        self.pkl_name = False
        self.df = pd.DataFrame()
        self.mongo = False
        self.mongoURI = None
        
        if year:
            self.year( year )
            
        if mongo:
            self.mongoURI = mongo
            self.mongodb()
            
        
        
        if config:
            self.config = config
        else:
            self.config = '/home/notebooks/config/validElements.conf'
            
            
    
    def mongodb( self ):
        '''
        If provided with a MongoDB URI then try to connect.
        This object could be sent to the Filing objects to
        allow self uploads to the the db.
        '''
        if not self.set_year:
            return
        
        print( 'Init MongoDB inside classy990forms object [%s] [%s]' % (self.mongoURI, self.set_year))
        self.mongo = Mongo990( uri=self.mongoURI, year=self.set_year )
        
        
    def year( self, year, reset_index=False ):
        self.set_year = year
        self.reset_index = reset_index
        
        # Name format from global variable
        self.sourceURL = indexURL % self.set_year
        # Name format from global variable
        self.pkl_name = pcklFile % self.set_year

        if self.debug: print( 'Working on year: %d' % self.set_year)
        if self.debug: print( 'index URL: %d' % self.set_year)
        
        self.load_index()
        
        if self.mongoURI:
            self.mongodb()
    
    def load_index( self, reset_index=False ):
        
        if not self.sourceURL or not self.pkl_name:
            print( 'ERROR: Neet to configure object.year(####) first.')
            return
        
        if self.debug: print( 'Prepare INDEX on year: %d' % self.set_year)
            
        # Maybe we want to reset the local cache
        if self.reset_index and os.path.isfile( self.pkl_name ):
            if self.debug: print( 'Remove previous cached INDEX: %d' % self.pkl_name)
            try:
                os.remove( self.pkl_name )
            except:
                self.print( 'ERROR: Cannot remove previous index: %s' % self.pkl_name )
                return
            
            self.reset_index = False
            
        # Verify if we already have the file
        if os.path.isfile( self.pkl_name ):
            # Read from disk
            if self.debug: 
                print( 'Found local copy: %s' % self.pkl_name)
                sys.stdout.write('LOADING...\r')
                sys.stdout.flush()
            self.df = pd.read_pickle( self.pkl_name )
        else:
            # Download from URL
            if self.debug:
                print( 'Download new index from: %s' % self.sourceURL)
                sys.stdout.write('DOWNLOADING...\r')
                sys.stdout.flush()
            self.df = pd.read_json( self.sourceURL )
            if self.debug:
                sys.stdout.write('PARSING DOWNLOADED FILE...\r')
                sys.stdout.flush()
            self.df = self.df[self.df.keys()[0]].apply(lambda x:pd.Series(x))
            # Save version to disk
            if self.debug:
                sys.stdout.write('SAVING COPY TO DISK...\r')
                sys.stdout.flush()
            self.df.to_pickle( self.pkl_name )
            if self.debug: print( 'New cached form: %s' % self.pkl_name)

        #if self.debug: print( self.df )
            
    
    def display( self ):
        '''
        Nice (native pandas) print of the DataFrame 990 data
        
        '''
        
        if not len(self.df):
            print( 'ERROR: Internal cache is empty!')
            return
        
        display( self.df )
    
    def __str__(self):
        '''
        String representation of the 990 form data
        To be called with the print on str methods:
            print(form)
        '''
        return str( self.df )
    
    def __repr__(self):
        '''
        Simple representation of the object.
            print( form.info() )
            form.info()
            or just "form" as the last line in notebook cell
        '''
        
        return 'IRS 990 form for year [%s]: %d documents' % (self.set_year, len(self.df) )

    def info( self ):
        return self.__repr__()
    
    def get( self, id=False, ein=False ):
        '''
        Download the actual 990 form from AWS using IRSx tools
        '''
        
        if id:
            variable = 'ObjectId'
            value = id
        elif ein:
            variable = 'EIN'
            value = ein
        else:
            print('ERROR: Only [ObjectId] or [EIN]')
            return None
        
        
        if self.debug: print( 'Downlaod %s:%s' % (variable,value) )
            
        # The identification of the row changes from iloc to loc
        return Filing(config=self.config, mongo=self.mongo,
                      **self.df.loc[self.df[variable] == value].to_dict('records')[0] )
    
    # Need iterator
    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            result =  Filing(config=self.config, mongo=self.mongo,
                             **self.df.iloc[self.index].to_dict() )
            return result
        except IndexError:
            raise StopIteration
        except Exception as e:
            print( 'ERROR: Problem on creating new Filing object' )
            print( '       Skipping this instance and continue with next' )
            print( '       %s' % e )
        self.index += 1
        return None


# In[7]:


if __name__ == '__main__':
    get_ipython().system('jupyter nbconvert --to script *.ipynb')


# In[ ]:




