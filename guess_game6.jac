"""A Number Guessing Game"""

import random;
import from byllm.llm { Model }

glob llm = Model(model_name="gemini-1.5-pro", api_key="AIzaSyCtigfkLBFwywDn1mUXXNG6icq9C9RukJU");

def give_hint(guess: int, correct_number: int) -> str by llm;

walker GuessGame {
    has guess: int;

    can start with `root entry;
    can process_guess with turn entry;
}

node turn {
    has correct_number: int = random.randint(1, 10);
}


 with entry:__main__ {
    root spawn GuessGame(3);
    root spawn GuessGame(4);
    root spawn GuessGame(5);
    root spawn GuessGame(6);
 }
