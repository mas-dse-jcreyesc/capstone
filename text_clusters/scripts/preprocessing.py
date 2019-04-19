# Author: Howard Tai

import re

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


#----------------------------------------#
# GLOBAL VARIABLES
#----------------------------------------#
SW = set(stopwords.words('english'))
LEMMA = WordNetLemmatizer()
#----------------------------------------#


#------------------------------------------------------------------------------#
# Text preprocessing function
#------------------------------------------------------------------------------#
def preprocess_text(text):
    """
    Helper function for preprocessing a given input text. Preprocessing includes
    removal of numbers, punctuation marks, stopwords, uncasing, normalizing
    spacing, and also lemmatization.
    """
    # Remove punctuations and numbers and lowercase
    new_text = re.sub('[^a-zA-Z ]', '', text).lower()
    new_text = re.sub(r'http.+org',' ',new_text)

    # Normalize spacing, remove stopwords, and lemmatize
    new_text = ' '.join(
        [LEMMA.lemmatize(s) for s in new_text.split() if s not in SW]
    )

    return new_text
#------------------------------------------------------------------------------#


#------------------------------------------------------------------------------#
# Main function
#------------------------------------------------------------------------------#
def main():
    """
    Tests for preprocess_text function
    """
    tmp = """
    This is a piece of sample text! Here are some numbers: 5567531246. The
    purpose of this text is to test out the ##awesome## preprocessing function!
    :) Let's see how it works...
    """

    print(tmp)

    print(preprocess_text(tmp))

    return None
#------------------------------------------------------------------------------#


if __name__=='__main__':
    main()
