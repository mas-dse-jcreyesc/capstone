from TextProcessorAbstract import TextProcessorAbstract


class TextProcessor(TextProcessorAbstract):
    """
    Helper Class to clean and process text
    """
    def clean_text(self, text):
        """
        Cleans the text from english noise
        :param text: input text string
        :return: text: output text string
        """
        pass

    def process_text(self, text):
        """
        Returns text in form of vector
        :param text: input text string
        :return: vector representing document text
        """
        pass