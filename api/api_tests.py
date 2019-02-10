from api.TextProcessorImpl import TextProcessor
import time


def test_text_processor_simple():
    text_processor = TextProcessor()
    sample_text = "The quick brown fo\'x jumped over the lazy dog!"
    test_processor(sample_text, text_processor)


def test_text_processor_medium():
    text_processor = TextProcessor()
    sample_text = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. " \
                  "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, " \
                  "when an unknown printer took a galley of type and scrambled it to make a type " \
                  "specimen book. It has survived not only five centuries, but also the leap into" \
                  " electronic typesetting, remaining essentially unchanged. It was popularised in " \
                  "the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, " \
                  "and more recently with desktop publishing software like Aldus PageMaker including " \
                  "versions of Lorem Ipsum."
    test_processor(sample_text, text_processor)


def test_text_processor_large():
    text_processor = TextProcessor()
    sample_text = open('test_text/Latin-Lipsum.txt').read()
    test_processor(sample_text, text_processor)


def test_processor(sample_text, text_processor):
    t0 = time.time()
    processed_text = text_processor.process_text(sample_text)
    t1 = time.time()
    print("TIME: " + str(t1 - t0), processed_text[:10])


test_text_processor_simple()
test_text_processor_medium()
test_text_processor_large()
