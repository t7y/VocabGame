import pygame
import random
import csv
import pyttsx3  # Text-to-speech engine

# Initialize pygame and pyttsx3
pygame.init()
engine = pyttsx3.init()

# Screen dimensions and window setup
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spelling/Vocab Game")

# Font settings
MAIN_FONT = pygame.font.SysFont('Arial', 32)
SMALL_FONT = pygame.font.SysFont('Arial', 24)

# Load the soundwave icon image and scale it
try:
    soundwave_icon = pygame.image.load('soundwave.png')
    soundwave_icon = pygame.transform.scale(soundwave_icon, (50, 50))
except Exception as e:
    print("Error loading soundwave.png:", e)
    soundwave_icon = None

# Define the button rectangle for the soundwave icon
sound_button_rect = pygame.Rect(WIDTH - 100, 50, 50, 50)

def load_vocab(filename):
    """Load vocabulary list from a TSV file with columns 'word', 'meaning', and 'sentence' using tab as delimiter."""
    vocab = []
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            for row in reader:
                vocab.append({
                    "word": row["word"],
                    "meaning": row["meaning"],
                    "sentence": row["sentence"]
                })
    except FileNotFoundError:
        print(f"File {filename} not found.")
    return vocab

def draw_text(surface, text, pos, font, color=(0, 0, 0)):
    """Helper function to render text on the screen."""
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_text_wrap(surface, text, pos, font, color, max_width):
    """Render text with word wrap if it exceeds max_width."""
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] > max_width and current_line != "":
            lines.append(current_line)
            current_line = word + " "
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    y_offset = 0
    for line in lines:
        line_surface = font.render(line, True, color)
        surface.blit(line_surface, (pos[0], pos[1] + y_offset))
        y_offset += font.get_linesize()

def reset_word(vocab):
    """Selects a new random vocabulary entry from the given list and resets input state."""
    entry = random.choice(vocab)
    word = entry["word"]
    meaning = entry["meaning"]
    sentence = entry["sentence"]
    user_input = ""
    error = False
    error_index = None
    displayed = ["_" for _ in word]
    return entry, word, meaning, sentence, user_input, error, error_index, displayed

def pronounce_word(word):
    """Use pyttsx3 to pronounce the given word."""
    engine.say(word)
    engine.runAndWait()

def main():
    # Set up modes: "practice" then "quiz"
    mode = "practice"
    total_words = 20

    # Load vocabulary for practice mode
    practice_vocab = load_vocab('vocab.tsv')
    if not practice_vocab:
        print("No vocabulary loaded. Exiting game.")
        pygame.quit()
        return

    # This list will hold all words that were practiced
    learned_words = []

    # For quiz mode we will use the learned_words list
    quiz_vocab = None

    clock = pygame.time.Clock()
    run = True
    score = 0
    words_completed = 0

    # Get the first word in practice mode
    current_entry, word, meaning, sentence, user_input, error, error_index, displayed = reset_word(practice_vocab)

    # Variables for quiz mode
    quiz_score = 0
    quiz_words_completed = 0
    quiz_word_correct = False  # Flag to indicate that the current quiz word was answered correctly

    while run:
        clock.tick(30)  # Run at 30 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Sound button: pronounce the current word when clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sound_button_rect.collidepoint(event.pos):
                    pronounce_word(word)

            if event.type == pygame.KEYDOWN:
                # In quiz mode, if the word is correctly typed, wait for Enter to move on
                if mode == "quiz" and quiz_word_correct:
                    if event.key == pygame.K_RETURN:
                        quiz_score += 1
                        quiz_words_completed += 1
                        # Remove current word from quiz_vocab to avoid duplicates
                        quiz_vocab.remove(current_entry)
                        quiz_word_correct = False
                        # If quiz is complete, show final message; otherwise, load next quiz word
                        if quiz_words_completed >= total_words or not quiz_vocab:
                            win.fill((255, 255, 255))
                            final_message = f"Congratulations! You passed the quiz with {quiz_score} correct words!"
                            draw_text_wrap(win, final_message, (50, HEIGHT // 2 - 50), MAIN_FONT, (0, 0, 0), WIDTH - 100)
                            pygame.display.update()
                            pygame.time.delay(4000)
                            run = False
                        else:
                            current_entry, word, meaning, sentence, user_input, error, error_index, displayed = reset_word(quiz_vocab)
                            pronounce_word(word)
                    continue  # Skip further key processing if waiting for Enter in quiz mode

                # Process backspace
                if event.key == pygame.K_BACKSPACE:
                    if len(user_input) > 0:
                        user_input = user_input[:-1]
                        if error and error_index == len(user_input):
                            error = False
                            error_index = None
                else:
                    char = event.unicode
                    if char.isalpha():
                        if not error:
                            if len(user_input) < len(word):
                                expected_char = word[len(user_input)]
                                if char.lower() == expected_char.lower():
                                    user_input += char
                                else:
                                    user_input += char
                                    error = True
                                    error_index = len(user_input) - 1

        # Update displayed letters based on user input
        for i in range(len(word)):
            if i < len(user_input):
                if error and i == error_index:
                    displayed[i] = user_input[i]
                elif user_input[i].lower() == word[i].lower():
                    displayed[i] = word[i]
                else:
                    displayed[i] = "_"
            else:
                displayed[i] = "_"

        # Clear screen
        win.fill((255, 255, 255))

        # Display UI based on mode
        if mode == "practice":
            # Practice mode UI: show word, meaning, and sample sentence
            score_text = f"Score: {score}"
            progress_text = f"Practice Word {words_completed + 1} of {total_words}"
            draw_text(win, score_text, (50, 10), SMALL_FONT)
            draw_text(win, progress_text, (WIDTH - 300, 10), SMALL_FONT)

            draw_text(win, word, (50, 50), MAIN_FONT)
            draw_text_wrap(win, meaning, (50, 100), SMALL_FONT, (0, 0, 0), WIDTH - 150)
            draw_text_wrap(win, "Example: " + sentence, (50, 150), SMALL_FONT, (0, 0, 0), WIDTH - 150)
        else:  # Quiz mode
            # When entering quiz mode, we use only words that were learned
            if quiz_vocab is None:
                quiz_vocab = learned_words.copy()
                # Optionally shuffle the quiz words:
                random.shuffle(quiz_vocab)
            quiz_header = "Quiz Mode: Listen and type the word"
            draw_text(win, quiz_header, (50, 10), SMALL_FONT)
            progress_text = f"Quiz Word {quiz_words_completed + 1} of {total_words}"
            draw_text(win, progress_text, (WIDTH - 300, 10), SMALL_FONT)
            # In quiz mode, only display the underlines (no hints) until answered correctly

        # Draw the sound button
        if soundwave_icon:
            win.blit(soundwave_icon, (sound_button_rect.x, sound_button_rect.y))
        else:
            pygame.draw.rect(win, (0, 0, 0), sound_button_rect, 2)
            draw_text(win, "Sound", (sound_button_rect.x + 5, sound_button_rect.y + 15), SMALL_FONT)

        # Draw spelling progress (underlines with user input)
        label = "Spelling: "
        draw_text(win, label, (50, 300), MAIN_FONT)
        x_offset = 50 + MAIN_FONT.size(label)[0]
        y_position = 300
        for i in range(len(word)):
            if i < len(user_input):
                if error and i == error_index:
                    letter = user_input[i]
                    letter_color = (255, 0, 0)
                elif user_input[i].lower() == word[i].lower():
                    letter = word[i]
                    letter_color = (0, 0, 0)
                else:
                    letter = "_"
                    letter_color = (0, 0, 0)
            else:
                letter = "_"
                letter_color = (0, 0, 0)
            draw_text(win, letter, (x_offset, y_position), MAIN_FONT, letter_color)
            x_offset += MAIN_FONT.size(letter)[0] + 10

        # In quiz mode, if the user types the word correctly, display the full word details and prompt for "Enter"
        if mode == "quiz" and not error and user_input.lower() == word.lower():
            quiz_word_correct = True
            # Display the full word details (after correct answer)
            draw_text(win, word, (50, 50), MAIN_FONT)
            draw_text_wrap(win, meaning, (50, 100), SMALL_FONT, (0, 0, 0), WIDTH - 150)
            draw_text_wrap(win, "Example: " + sentence, (50, 150), SMALL_FONT, (0, 0, 0), WIDTH - 150)
            next_prompt = "Press ENTER for next word"
            draw_text(win, next_prompt, (50, 400), SMALL_FONT)

        pygame.display.update()

        # Check if in practice mode the word is correctly spelled
        if mode == "practice" and not error and user_input.lower() == word.lower():
            # Pronounce the word automatically
            pronounce_word(word)
            pygame.time.delay(500)
            score += 1
            words_completed += 1
            # Add the learned word to the learned_words list
            learned_words.append(current_entry)
            # Remove the current word from practice_vocab to avoid duplicates
            practice_vocab.remove(current_entry)
            if words_completed >= total_words or not practice_vocab:
                mode = "quiz"
                # Set quiz_vocab to only the learned words
                quiz_vocab = learned_words.copy()
                random.shuffle(quiz_vocab)
                # Load the first quiz word
                current_entry, word, meaning, sentence, user_input, error, error_index, displayed = reset_word(quiz_vocab)
                pronounce_word(word)
            else:
                current_entry, word, meaning, sentence, user_input, error, error_index, displayed = reset_word(practice_vocab)
        # In quiz mode, moving to next word is handled by waiting for Enter (above)

    pygame.quit()

if __name__ == "__main__":
    main()