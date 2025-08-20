import logging

def filter_words_by_length(length: int) -> list[str]:
  filtered_words: list[str] = []
  with open('assets/words_alpha.txt', 'r') as f:
    for line in f:
      word = line.strip()
      if len(word) == length:
        filtered_words.append(word)
  
  if not filtered_words:
    logging.warning(f"No words of length {length} found in assets/words_alpha.txt")
  else:
    logging.info(f"Found {len(filtered_words)} words of length {length} in assets/words_alpha.txt")

  return filtered_words

def dump_words_into_file(words: list[str], file_path: str):
  try:
    with open(file_path, 'w') as f:
      f.writelines(f"{word}\n" for word in words)
  except IOError as e:
    logging.error(f"Error writing to file {file_path}: {e}")
    raise e
  logging.info(f"Words dumped into {file_path} successfully.")

def build_index(words: list[str]) -> list[dict]:
  index = [[list() for _ in range(len(words[0]))] for _ in range(26)]
  for i, word in enumerate(words):
    for j, char in enumerate(word):
      ascii_index = ord(char) - ord('a')
      index[ascii_index][j].append(i)

  logging.info(f"Built index for {len(words)} words.")

  return index

def get_word_score(word: str, index: list[dict]) -> int:
  score = 0
  for i, char in enumerate(word):
    ascii_index = ord(char) - ord('a')
    
    for j in range(len(word)):
      if j != i:
        score += len(index[ascii_index][j]) - 1
      else:
        score += 3 * (len(index[ascii_index][j]) - 1)
  
  return score

def score_words(words: list[str], index: list[dict]) -> list[tuple[str, int]]:
  scored_words = []
  for word in words:
    score = get_word_score(word, index)
    scored_words.append((word, score))

  return scored_words

def does_follow_pattern(word: str, initial_word: str, pattern: str) -> bool:
  if len(word) != len(initial_word) or len(pattern) != len(initial_word):
    return False
  
  word_without_green = ''
  initial_word_without_green = ''
  for i, c in enumerate(word):
    if pattern[i] == 'G':
      if c != initial_word[i]:
        return False
    else:
      word_without_green += c
      initial_word_without_green += initial_word[i]

  pattern_without_green = pattern.replace('G', '')

  yellow_char_counts = {}
  for i, c in enumerate(initial_word_without_green):
    if pattern_without_green[i] == 'Y':
      yellow_char_counts[c] = yellow_char_counts.get(c, 0) + 1

  word_char_counts = {}
  for c in word_without_green:
    word_char_counts[c] = word_char_counts.get(c, 0) + 1

  initial_word_char_counts = {}
  for c in initial_word_without_green:
    initial_word_char_counts[c] = initial_word_char_counts.get(c, 0) + 1
  
  for i, c in enumerate(initial_word_without_green):
    if pattern_without_green[i] == 'Y':
      if c == word_without_green[i]:
        return False

      if yellow_char_counts[c] > word_char_counts.get(c, 0):
        return False
      
      if yellow_char_counts[c] < word_char_counts.get(c, 0) and initial_word_char_counts[c] >= word_char_counts.get(c, 0):
        return False

  grey_chars = set([c for i, c in enumerate(initial_word_without_green) if pattern_without_green[i] == '-' and c not in yellow_char_counts])

  for c in word_without_green:
    if c in grey_chars or (c in yellow_char_counts and yellow_char_counts[c] == 0):
      return False
  
  return True

def filter_words_by_pattern(words: list[str], initial_word:str, pattern: str) -> list[str]:
  # pattern will look like "--GY-" where G is green, Y is yellow, and - is grey
  # Green means the letter is in the correct position
  # Yellow means the letter is in the word but not in the correct position
  # Grey means the letter is not in the word at all
  filtered_words = []
  
  for word in words:
    if does_follow_pattern(word, initial_word, pattern):
      filtered_words.append(word)

  logging.info(f"Filtered words by pattern '{pattern}' from {len(words)} to {len(filtered_words)} words.")
  
  return filtered_words

def load_invalid_words() -> set[str]:
  invalid_words = set()
  try:
    with open('assets/invalid_words.txt', 'r') as f:
      for line in f:
        invalid_words.add(line.strip())
  except FileNotFoundError:
    logging.warning("Invalid words file not found. Proceeding without it.")
  
  return invalid_words

def process_words(length: int):
  invalid_words = load_invalid_words()
  filtered_words = filter_words_by_length(length)
  dump_words_into_file(filtered_words, f"assets/processed/words_{length}.txt")

  initial_word = '#'
  choice = int(input("enter (1) to load history, (2) to continue without history: "))
  if choice == 1:
    with open("input.txt", "r") as f:
      lines = f.readlines()
      for i in range(0, len(lines), 2):
        initial_word = lines[i].strip()
        if initial_word == '#':
          break
        pattern = lines[i + 1].strip()
        filtered_words = filter_words_by_pattern(filtered_words, initial_word, pattern)

  while True:
    index = build_index(filtered_words)
    logging.info(f"Indexing complete for {len(filtered_words)} words.")
    scored_words = score_words(filtered_words, index)
    scored_words.sort(key=lambda x: x[1], reverse=True)

    pattern = 'i'
    top_index = 0
    while pattern == 'i':
      top_word = scored_words[top_index][0] if initial_word == '#' else initial_word
      if top_word in invalid_words:
        logging.info(f"Skipping invalid word: {top_word}")
        top_index += 1
        continue
      print(f"Guesed word: {top_word}")
      pattern = input("Enter the pattern (e.g., --GY-): ").strip()
      if pattern.lower() == 'i':
        invalid_words.add(top_word)
      if pattern.lower() == 'exit':
        break
      top_index += 1

    filtered_words = filter_words_by_pattern(filtered_words, top_word, pattern)
    if not filtered_words:
      logging.info("No words left after filtering. Exiting.")
      break
    
    initial_word = '#'
    logging.info(f"Scored words saved to assets/processed/scored_words_{length}.txt")

  return filtered_words, scored_words