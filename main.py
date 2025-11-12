import random
import time
import os
import math
from datetime import datetime

# --- CONFIGURATION ---

levels = {
    "Easy": {"ops": ["+", "-"], "range": (1, 20), "time": 8, "reward": 10, "penalty": 10},
    "Medium": {"ops": ["*"], "range": (2, 12), "time": 10, "reward": 15, "penalty": 15},
    "Hard": {"ops": ["/"], "range": (2, 12), "time": 15, "reward": 20, "penalty": 25},
}

monsters = [
    {"name": "Addagon", "base_hp": 30},
    {"name": "Subtrax", "base_hp": 30},
    {"name": "Multiplex", "base_hp": 40},
    {"name": "Dividra", "base_hp": 50},
    {"name": "Mathemorph", "base_hp": 60},
]

# --- GLOBAL STATE ---

player = {"hp": 100, "score": 0, "level": None, "name": ""}
seen_monsters = set()
defeated_monsters = []


# --- HELPER FUNCTIONS ---

def clear_screen():
    """Clears the console for a clean turn-based display."""
    print("\n" * 50)


def hp_bar(current_hp, max_hp, bar_length=20):
    """Return a visual HP bar string."""
    current_hp = max(0, current_hp)
    filled_length = int(bar_length * current_hp // max_hp)
    bar = "#" * filled_length + "-" * (bar_length - filled_length)
    percent = int((current_hp / max_hp) * 100)
    return f"[{bar}] ({percent}%)"


def choose_level():
    """Ask the player to choose a difficulty level."""
    print("Choose your battle difficulty:")
    for i, lvl in enumerate(levels.keys(), start=1):
        print(f"{i}. {lvl}")

    while True:
        try:
            choice = int(input("\nEnter number: "))
            level_name = list(levels.keys())[choice - 1]
            print(f"\n⚔️ You chose {level_name} mode!\n")
            return level_name
        except (ValueError, IndexError):
            print("Invalid choice. Try again.")


def generate_question(level):
    """Generate a random math question based on the selected level."""
    config = levels[level]
    op = random.choice(config["ops"])

    if op == "/":
        # Ensure division results in an integer answer
        divisor = random.randint(config["range"][0], config["range"][1])
        quotient = random.randint(config["range"][0], config["range"][1])
        dividend = divisor * quotient
        question = f"{dividend} / {divisor}"
        correct = quotient
    else:
        a, b = random.randint(*config["range"]), random.randint(*config["range"])
        correct = eval(f"{a} {op} {b}")
        question = f"{a} {op} {b}"

    return question, correct


def display_stats(monster=None, monster_max_hp=None):
    """Display the player's and monster's current stats with HP bars."""
    print("📊 CURRENT STATUS")
    print("-" * 30)
    if player['name']:
        display_name = player['name'][:10]
        print(f"Warrior: {display_name}")
    print(f"❤️ HP: {hp_bar(player['hp'], 100)}")
    print(f"💯 Score: {player['score']}")
    print(f"🎯 Difficulty: {player['level']}")
    print("-" * 30)

    if monster:
        print(f"\n👾 {monster['name']} HP: {hp_bar(monster['hp'], monster_max_hp)}")
        print("-" * 30)
    print()


def ask_question(monster, level, monster_max_hp):
    """Ask a math question, track timing, and apply rewards/damage."""
    config = levels[level]
    question, correct_answer = generate_question(level)

    clear_screen()
    display_stats(monster, monster_max_hp)

    print(f"⏰ You have {config['time']} seconds to answer.")
    print(f"🧮 Question: {question}\n")

    start_time = datetime.now()

    try:
        raw_input_val = input("💬 Your answer: ").strip()

        # Allow player to exit anytime
        if raw_input_val.lower() in ["exit", "quit"]:
            print("\nExiting the battle...")
            exit()

        # Clean and parse answer
        try:
            answer = float(raw_input_val.replace(",", ""))
        except ValueError:
            print(f"\nInvalid input! You take {config['penalty']} damage!")
            player["hp"] -= config["penalty"]
            time.sleep(1.5)
            return

        print()
        elapsed = (datetime.now() - start_time).total_seconds()

        if elapsed > config["time"]:
            print(f"⏰ Too slow! You take {config['penalty']} damage!")
            player["hp"] -= config["penalty"]
        elif math.isclose(answer, correct_answer, rel_tol=1e-9, abs_tol=1e-9) or round(answer, 2) == round(correct_answer, 2):
            print(f"✅ Correct! You dealt {config['reward']} damage to {monster['name']}!")
            monster["hp"] -= config["reward"]
            player["score"] += config["reward"]
        else:
            print(f"❌ Wrong! The correct answer was {correct_answer}. You take {config['penalty']} damage!")
            player["hp"] -= config["penalty"]

        time.sleep(1.5)

    except KeyboardInterrupt:
        print("\nExiting the battle...")
        exit()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        time.sleep(1.5)


# --- MAIN GAME LOOP ---

def main():
    clear_screen()
    print("🎮 WELCOME TO MATH BATTLE!")
    print("Defeat monsters by solving math problems before time runs out!\n")

    player_input = input("Enter your warrior name: ").strip()
    if player_input:
        player["name"] = player_input[:15]
        print(f"\nWelcome, {player['name']}!\n")
    else:
        player["name"] = "Warrior"
        print("\nWelcome, Warrior!\n")

    level = choose_level()
    player["level"] = level

    while player["hp"] > 0:
        monster = random.choice(monsters).copy()
        seen_monsters.add(monster["name"])
        monster["hp"] = monster["base_hp"] + levels[level]["reward"]
        monster_max_hp = monster["hp"]

        while monster["hp"] > 0 and player["hp"] > 0:
            ask_question(monster, level, monster_max_hp)

        if player["hp"] <= 0:
            clear_screen()
            break

        print(f"🏆 You defeated {monster['name']}!\n")
        defeated_monsters.append(monster["name"])
        time.sleep(1.5)

    # --- GAME OVER SUMMARY ---
    clear_screen()
    print("🏁 GAME OVER!")

    print(f"Warrior: {player['name']}")
    print(f"Final Score: {player['score']}")
    print(f"Monsters Encountered: {', '.join(seen_monsters) if seen_monsters else 'None'}")
    print(f"Monsters Defeated: {', '.join(defeated_monsters) if defeated_monsters else 'None'}")

    encountered_monsters = list(filter(lambda m: m["name"] in seen_monsters, monsters))
    monster_names = list(map(lambda m: m["name"], encountered_monsters))
    total_hp_encountered = sum(map(lambda m: m["base_hp"], encountered_monsters))

    print(f"\nTotal Base HP of encountered monsters: {total_hp_encountered}")

    strong_monsters = [m for m in encountered_monsters if m["base_hp"] > 40]
    if strong_monsters:
        strong_names = ', '.join(m['name'] for m in strong_monsters)
        print(f"Tough Monsters (HP > 40): {strong_names}")

    print("\n✨ Thanks for playing MATH BATTLE!")


# --- START THE GAME ---
if __name__ == "__main__":
    main()
