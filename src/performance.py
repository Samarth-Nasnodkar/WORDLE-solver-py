from processor.processor import *
import logging

WORD_LENGTH = 5

def get_pattern(correct_word, word):
  pattern = ['-' for _ in range(len(correct_word))]

  correct_word_chars = {}
  word_chars = {}

  for c in correct_word:
    correct_word_chars[c] = correct_word_chars.get(c, 0) + 1

  for c in word:
    word_chars[c] = word_chars.get(c, 0) + 1

  for i, c in enumerate(correct_word):
    if c == word[i]:
      pattern[i] = 'G'
      correct_word_chars[c] -= 1
      word_chars[c] -= 1
      if correct_word_chars[c] == 0:
        del correct_word_chars[c]
      if word_chars[c] == 0:
        del word_chars[c]

  for i, c in enumerate(word):
    if pattern[i] == 'G':
      continue

    if c in correct_word_chars:
      if pattern[i] == '-':
        pattern[i] = 'Y'
        correct_word_chars[c] -= 1
        word_chars[c] -= 1

  return ''.join(pattern)

if __name__ == "__main__":

  logging.basicConfig(level=logging.ERROR)

  words = filter_words_by_length(WORD_LENGTH)
  word_attempts_map = {}
  for word in words:
    filtered_words = words[:]
    correct_word = word

    for start_word in ['saree']:
      success = False
      total_attempts = 7
      top_word = None
      for attempt in range(6):
        try:
          if top_word is None:
            top_word = start_word
          else:
            index = build_index(filtered_words)
            scored_words = score_words(filtered_words, index)
            top_word = scored_words[0][0]
          pattern = get_pattern(correct_word, top_word)
          if pattern == "GGGGG":
            total_attempts = attempt + 1
            success = True
            logging.info(f"Found correct word '{correct_word}' in {attempt + 1} attempts.")
            break
          else:
            filtered_words = filter_words_by_pattern(filtered_words, top_word, pattern)
        except Exception as e:
          logging.error(f"Error occurred: {e}")
          continue

      word_attempts_map[start_word] = word_attempts_map.get(start_word, 0) + total_attempts

  with open("assets/performance/attempts.txt", "w") as f:
    sorted_attempts = sorted(word_attempts_map.items(), key=lambda x: x[1])
    for word, attempts in sorted_attempts:
      f.write(f"{word}: {attempts}\n")

  # Not ready yet!
  logging.info("Performance data saved to assets/performance/attempts.txt")
