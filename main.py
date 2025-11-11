import random
import time
import os
from datetime import datetime

# --- CONFIGURATION ---

levels = {
    "Easy": {"ops": ["+", "-"], "range": (1, 20), "time": 6, "reward": 10, "penalty": 5},
    "Medium": {"ops": ["+", "-", "*"], "range": (5, 50), "time": 5, "reward": 15, "penalty": 10},
    "Hard": {"ops": ["+", "-", "*", "/"], "range": (10, 999), "time": 4, "reward": 20, "penalty": 15},
}

monsters = [
    {"name": "Addagon", "base_hp": 30},
    {"name": "Subtrax", "base_hp": 30},
    {"name": "Multiplex", "base_hp": 40},
    {"name": "Dividra", "base_hp": 50},
    {"name": "Mathemorph", "base_hp": 60},
]

# --- GLOBAL STATE ---

player = {"hp": 100, "score": 0, "level": None}
seen_monsters = set()


# --- HELPER FUNCTIONS ---

def clear_screen():
    """Clears the console for a clean turn-based display."""
    os.system('cls' if os.name == 'nt' else 'clear')


def choose_level():
    """Ask the player to choose a difficulty level."""
    print("📘 Choose your battle difficulty:")
    for i, lvl in enumerate(levels.keys(), start=1):
        print(f"{i}. {lvl}")

    while True:
        try:
            choice = int(input("\nEnter number: "))
            level_name = list(levels.keys())[choice - 1]
            print(f"\n⚔️ You chose {level_name} mode!\n")
            return level_name
        except (ValueError, IndexError):
            print("❌ Invalid choice. Try again.")


def generate_question(level):
    """Generate a random math question based on the selected level."""
    config = levels[level]
    op = random.choice(config["ops"])
    a, b = random.randint(*config["range"]), random.randint(*config["range"])

    # Avoid division by zero and round division answers
    if op == "/":
        b = random.randint(1, config["range"][1])
        correct = round(a / b, 2)
    else:
        correct = eval(f"{a} {op} {b}")

    return f"{a} {op} {b}", correct


def display_stats():
    """Display the player's current stats."""
    print("📊 CURRENT STATUS")
    print("-" * 30)
    print(f"❤️  HP: {player['hp']}")
    print(f"💯  Score: {player['score']}")
    print(f"🎯  Difficulty: {player['level']}")
    print("-" * 30)
    print()


def ask_question(monster, level):
    """Ask a math question, track timing, and apply rewards/damage."""
    config = levels[level]
    question, correct_answer = generate_question(level)

    clear_screen()
    display_stats()

    print("-" * 50)
    print(f"👾  A wild {monster['name']} appears!  (HP: {monster['hp']})")
    print("-" * 50)
    print(f"⏰  You have {config['time']} seconds to answer.")
    print(f"🧮  Question: {question}\n")

    start_time = datetime.now()

    try:
        # User input with time tracking
        answer = input("💬  Your answer: ")
        elapsed = (datetime.now() - start_time).total_seconds()

        # Validate numeric input
        try:
            answer = float(answer)
        except ValueError:
            print(f"\n⚠️ Invalid input! You take {config['penalty']} damage!")
            player["hp"] -= config["penalty"]
            time.sleep(1.5)
            return

        print()
        # Check time and correctness
        if elapsed > config["time"]:
            print(f"⏰ Too slow! You take {config['penalty']} damage!")
            player["hp"] -= config["penalty"]
        elif abs(answer - correct_answer) < 0.01:
            print(f"✅ Correct! You dealt {config['reward']} damage to {monster['name']}!")
            monster["hp"] -= config["reward"]
            player["score"] += config["reward"]
        else:
            print(f"❌ Wrong! The correct answer was {correct_answer}. You take {config['penalty']} damage!")
            player["hp"] -= config["penalty"]

        print()
        time.sleep(1.5)

    except KeyboardInterrupt:
        print("\n🚪 Exiting the battle...")
        exit()
    except Exception as e:
        print(f"\n⚠️ Unexpected error: {e}")
        time.sleep(1.5)


# --- MAIN GAME LOOP ---

def main():
    clear_screen()
    print("🎮 WELCOME TO MATH BATTLE!")
    print("Defeat monsters by solving math problems before time runs out!\n")

    level = choose_level()
    player["level"] = level

    # Main battle loop
    while player["hp"] > 0:
        monster = random.choice(monsters)
        seen_monsters.add(monster["name"])
        monster["hp"] = monster["base_hp"] + levels[level]["reward"]

        # Battle this monster until one side falls
        while monster["hp"] > 0 and player["hp"] > 0:
            ask_question(monster, level)

        if player["hp"] <= 0:
            clear_screen()
            print("💀 You were defeated...")
            break

        print(f"🎉 You defeated {monster['name']}!\n")
        time.sleep(1.5)

    # --- GAME OVER SUMMARY ---
    clear_screen()
    print("🏁 GAME OVER!")
    print(f"Final Score: {player['score']}")
    print(f"Monsters Encountered: {', '.join(seen_monsters)}")

    # --- Demonstrate map(), filter(), and lambda usage ---

    # 1️⃣ Use filter() to find which monsters were encountered
    encountered_monsters = list(filter(lambda m: m["name"] in seen_monsters, monsters))

    # 2️⃣ Use map() + lambda to get names of encountered monsters
    monster_names = list(map(lambda m: m["name"], encountered_monsters))

    # 3️⃣ Use another lambda in sum/map to calculate total monster HP encountered
    total_hp_encountered = sum(map(lambda m: m["base_hp"], encountered_monsters))

    print(f"\n👹 Monsters you fought: {', '.join(monster_names)}")
    print(f"💪 Total Base HP of encountered monsters: {total_hp_encountered}")

    # 4️⃣ Use filter() + lambda to show only strong monsters (base_hp > 40)
    strong_monsters = list(filter(lambda m: m["base_hp"] > 40, encountered_monsters))
    if strong_monsters:
        strong_names = ', '.join(map(lambda m: m['name'], strong_monsters))
        print(f"🔥 Tough Monsters (HP > 40): {strong_names}")

    # 5️⃣ Existing map() demo still valid
    print(f"\n🔢 Score doubled preview (map demo): {list(map(lambda x: x * 2, [player['score']]))}")
    print("\nThanks for playing MATH BATTLE! ⚔️")


# --- START THE GAME ---
if __name__ == "__main__":
    main()
