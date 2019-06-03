# Author: Howard Tai

# This script contains code for performing text-related processing tasks for
# preparation for input into a clustering model

import os
import pdb

from tqdm import tqdm

import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub

from text_preprocessing import preprocess_text


#----------------------------------------#
# GLOBAL VARIABLES
#----------------------------------------#
MOD_PATH = 'https://tfhub.dev/google/universal-sentence-encoder/2'
#----------------------------------------#


#------------------------------------------------------------------------------#
# Main text data cleaning function 
#------------------------------------------------------------------------------#
def clean_data(df, mode='990'):
    """
    Function for receiving a dataframe of extracted 990 fields and processing
    them in into a format that is compatible with embedding via the Universal
    Sentence Encoder. Several modes of processing are allowed: 
    
    - Normal 990 documents
    - Website-mined data
    
    Input(s):
    - df (pandas df)
    - mode (str): tag specifying type of processing to use
    """
    if mode not in ['990', 'website']:
        raise ModeNotValidException('Mode is not a valid selection')
    
    # Get valid text fields
    uniqueID = 'EIN'
    org_name = 'OrganizationName'
    if mode=='990':
        txt_cols = [
            'OrganizationName',
            'Desc',
            'ActivityOrMissionDesc',
            'MissionDesc'
        ]
    elif mode=='website':
        txt_cols = [
            'OrganizationName',
            'Desc',
            'ActivityOrMissionDesc',
            'MissionDesc',
            'WebSnippet'
        ]
    
    # Aggregate relevant text fields into single entities
    agg_indx = []
    agg_text = []
    agg_name = []
    for i, row in df.iterrows():
        tmp_text = []
        for f in txt_cols:
            tmp_text.append(row[f])
        
        # Preprocess and append
        agg_indx.append(row[uniqueID])
        agg_text.append(preprocess_text(' '.join(tmp_text)))
        agg_name.append(row[org_name])
    
    # Format results into dataframe
    clean_df = pd.DataFrame(
        {
            'EIN': agg_indx,
            'Name': agg_name,
            'Text': agg_text
        }
    )
    
    return clean_df
#------------------------------------------------------------------------------#


#------------------------------------------------------------------------------#
# Main text encoding function
#------------------------------------------------------------------------------#
def get_embed_fn(mod_path):
    """
    Helper function for getting embedding function
    """
    with tf.Graph().as_default():
        sentences = tf.placeholder(tf.string)
        embed = hub.Module(mod_path)
        embeddings = embed(sentences)
        session = tf.train.MonitoredSession()
        
    return lambda x: session.run(embeddings, {sentences: x})


def encode_text(df, text_tag='Text', name_tag='EIN'):
    """
    Function for encoding cleaned text using Tensorflow's Universal Sentence 
    Encoder
    """
    # Get embedding function
    embed_fn = get_embed_fn(MOD_PATH)
    
    # Get text encodings
    text_encodings = embed_fn(df[text_tag].values)
    
    # Format encoding outputs
    encoding_dict = {}
    for i, enc in enumerate(text_encodings):
        encoding_dict[df.iloc[i][name_tag]] = enc
    
    return encoding_dict
#------------------------------------------------------------------------------#