from abc import ABC, abstractmethod


class TextProcessorAbstract(ABC):
    """
    Helper Class to clean and process text
    """
    @abstractmethod
    def clean_text(self, text, remove_stopwords=True):
        """
        Cleans the text from english noise
        :param text: input text string
        :param remove_stopwords: boolean indicating if should remove stopwords
        :return: text: output text string
        """
        pass

    @abstractmethod
    def process_text(self, text, remove_stopwords=True):
        """
        Returns text in form of vector
        :param text: input text string
        :param remove_stopwords: boolean indicating if should remove stopwords
        :return: vector representing document text
        """
        pass
