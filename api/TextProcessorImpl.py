from api.TextProcessorAbstract import TextProcessorAbstract
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string


class TextProcessor(TextProcessorAbstract):
    """
    Helper Class to clean and process text
    """
    __stopwords__ = set(stopwords.words('english'))
    __translator__ = str.maketrans('', '', string.punctuation)

    def clean_text(self, text, remove_stopwords=True):
        """
        Cleans the text from english noise
        :param text: input text string
         :param remove_stopwords: boolean indicating if should remove stopwords
        :return: text: output list of text tokens
        """
        # remove white space and punctuation
        clean_text = text.strip().lower().translate(self.__translator__)
        # tokenize the text
        tokenized_text = word_tokenize(clean_text)
        # remove stop words
        if remove_stopwords:
            return [w for w in tokenized_text if not w in self.__stopwords__]
        return tokenized_text

    def process_text(self, text, remove_stopwords=True):
        """
        Returns text in form of vector
        :param text: input text string
         :param remove_stopwords: boolean indicating if should remove stopwords
        :return: vector representing document text
        """
        return self.clean_text(text, remove_stopwords)
