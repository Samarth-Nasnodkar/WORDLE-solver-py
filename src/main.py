from processor.processor import process_words
import logging

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  
  WORD_LENGTH = 5  # Example word length
  process_words(WORD_LENGTH)
  logging.info(f"Processed words of length {WORD_LENGTH} and saved to assets/processed/words_{WORD_LENGTH}.txt")