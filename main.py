import random
from datetime import datetime
import threading
import time
import sys

# -------------------------------
# 🧠 Data Structures
# -------------------------------

# Player stats (Dict)
player = {"name": "Hero", "hp": 100, "score": 0, "defeated": 0}

# Monster pools by difficulty (List of Dicts)
monsters = {
    "easy": [
        {"name": "Addagon", "hp": 25, "type": "Addition"},
        {"name": "Subtrax", "hp": 25, "type": "Subtraction"},
    ],
    "medium": [
        {"name": "Multiplex", "hp": 35, "type": "Multiplication"},
        {"name": "Calcumancer", "hp": 30, "type": "Addition"},
    ],
    "hard": [
        {"name": "Dividra", "hp": 50, "type": "Division"},
        {"name": "Mathemorph", "hp": 45, "type": "All"},
    ]
}

# Mode settings (Dict with Tuples for ranges)
modes = {
    "easy": {"ops": ["+", "-"], "time": 6, "range": (1, 20), "reward": 10, "penalty": 5},
    "medium": {"ops": ["+", "-", "*"], "time": 5, "range": (5, 50), "reward": 15, "penalty": 10},
    "hard": {"ops": ["+", "-", "*", "/"], "time": 4, "range": (10, 99), "reward": 20, "penalty": 15}
}

# Game tracking
encountered = set()  # Set for unique monsters
high_scores = []  # List with Tuples
questions = []  # List of questions asked
current_monster = None
correct_answer = None
start_time = None
mode = "easy"
level = 1

# Timer control
timer_running = False
user_input = None


# -------------------------------
# 🎮 Game Functions
# -------------------------------

def select_mode():
    """Select difficulty mode with while loop."""
    global mode
    print("\n🎯 SELECT MODE:")
    print("1. EASY (+ −) | 1-20 | 6s")
    print("2. MEDIUM (+ − ×) | 5-50 | 5s")
    print("3. HARD (+ − × ÷) | 10-99 | 4s")

    # While loop for validation
    while True:
        choice = input("\nChoice (1-3): ").strip()
        if choice == "1":
            mode = "easy"
            break
        elif choice == "2":
            mode = "medium"
            break
        elif choice == "3":
            mode = "hard"
            break
        else:
            print("❌ Enter 1, 2, or 3")


def start_game():
    """Initialize game."""
    global player, encountered, questions, level

    # String manipulation
    name = input("\n🦸 Hero name: ").strip().capitalize()
    player["name"] = name if name else "Hero"

    select_mode()

    # Reset state
    player["hp"], player["score"], player["defeated"] = 100, 0, 0
    encountered.clear()
    questions.clear()
    level = 1

    print(f"\n⚔️ {player['name']} enters {mode.upper()} mode!\n")
    spawn_monster()


def spawn_monster():
    """Spawn random monster."""
    global current_monster, level

    # Random selection from list
    template = random.choice(monsters[mode])
    current_monster = template.copy()
    current_monster["hp"] = template["hp"] + (level * 10)

    # Add to set
    encountered.add(current_monster["name"])

    # Level up every 3 monsters
    if player["defeated"] > 0 and player["defeated"] % 3 == 0:
        level += 1
        print(f"⚡ LEVEL {level}! ⚡")

    print(f"🚨 {current_monster['name']} appears!")
    ask_question()


def ask_question():
    """Generate and ask math question."""
    global correct_answer, start_time

    config = modes[mode]
    min_num, max_num = config["range"]

    # Determine operation
    if current_monster["type"] == "All":
        op = random.choice(config["ops"])
    elif current_monster["type"] == "Addition" and "+" in config["ops"]:
        op = "+"
    elif current_monster["type"] == "Subtraction" and "-" in config["ops"]:
        op = "-"
    elif current_monster["type"] == "Multiplication" and "*" in config["ops"]:
        op = "*"
    elif current_monster["type"] == "Division" and "/" in config["ops"]:
        op = "/"
    else:
        op = random.choice(config["ops"])

    # Generate numbers
    a = random.randint(min_num, max_num)
    b = random.randint(min_num, max_num)

    # Adjust for operation type
    if op == "-" and a < b:
        a, b = b, a
    elif op == "*":
        a, b = random.randint(2, 12), random.randint(2, 12)
    elif op == "/":
        b = random.randint(2, 12)
        a = b * random.randint(2, 12)  # Whole numbers

    # Calculate answer
    try:
        correct_answer = round(eval(f"{a} {op} {b}"), 2)
    except:
        correct_answer = 0

    # Display and record
    question = f"{a} {op} {b} = ?"
    questions.append(question)

    print(f"\n❤️ HP: {player['hp']} | ⭐ Score: {player['score']} | 💀 Defeated: {player['defeated']}")
    print(f"🎯 {current_monster['name']} HP: {current_monster['hp']}")
    print(f"❓ {question}")

    start_time = datetime.now()
    get_answer_with_timer()


def display_timer(time_limit):
    """Display live countdown timer in separate thread."""
    global timer_running
    start = datetime.now()
    last_second = time_limit

    while timer_running:
        elapsed = (datetime.now() - start).total_seconds()
        remaining = max(0, time_limit - elapsed)
        current_second = int(remaining)

        # Only update display when second changes
        if current_second != last_second:
            # Clear the timer line and rewrite it
            sys.stdout.write(f"\r⏰ Time left: {current_second}s  ")
            sys.stdout.flush()
            last_second = current_second

        if remaining <= 0:
            break

        time.sleep(0.1)


def get_answer_with_timer():
    """Get answer with live timer."""
    global timer_running, user_input

    config = modes[mode]
    time_limit = config["time"]

    # Display initial timer
    print(f"⏰ Time left: {int(time_limit)}s")

    # Start timer in separate thread
    timer_running = True
    timer_thread = threading.Thread(target=display_timer, args=(time_limit,), daemon=True)
    timer_thread.start()

    try:
        # Get user input on separate line
        user_input = input("Your answer: ")
        timer_running = False  # Stop timer
        print()  # New line after answer

        elapsed = (datetime.now() - start_time).total_seconds()
        answer = float(user_input)

        # Conditional statements
        if elapsed > time_limit:
            print(f"⏰ TOO SLOW! -{config['penalty']} HP")
            player["hp"] -= config["penalty"]
        elif abs(answer - correct_answer) < 0.01:
            damage = config["reward"] + level * 2
            print(f"✅ CORRECT! {damage} damage dealt!")
            current_monster["hp"] -= damage
            player["score"] += config["reward"]
        else:
            print(f"❌ WRONG! Answer: {correct_answer}. -{config['penalty']} HP")
            player["hp"] -= config["penalty"]

        check_state()

    except ValueError:
        timer_running = False
        print("\n⚠️ Invalid input!")
        ask_question()
    except KeyboardInterrupt:
        timer_running = False
        print("\n\n🚪 Exiting...")
        save_score()
        end_game()
    except Exception as e:
        timer_running = False
        print(f"\n⚠️ Error: {e}")
        ask_question()


def check_state():
    """Check win/loss conditions."""
    # If-elif-else statements
    if player["hp"] <= 0:
        print(f"💀 {player['name']} defeated!")
        save_score()
        end_game()
    elif current_monster["hp"] <= 0:
        player["defeated"] += 1
        player["hp"] = min(100, player["hp"] + 15)
        player["score"] += 20 + level * 5
        print(f"🎉 {current_monster['name']} defeated! +15 HP!")
        spawn_monster()
    else:
        ask_question()


def end_game():
    """Display final stats and high scores."""
    print("\n" + "=" * 50)
    print("🎮 GAME OVER")
    print("=" * 50)
    print(f"\n📊 {player['name']}'s Stats:")
    print(f"🏆 Score: {player['score']}")
    print(f"💀 Monsters: {player['defeated']}")
    print(f"❓ Questions: {len(questions)}")
    print(f"⚔️ Level: {level}")

    # Show unique monsters (Set)
    if encountered:
        print(f"\n👾 Fought: {', '.join(sorted(encountered))}")

    # Show sample questions (List slicing)
    if questions:
        print(f"\n📝 First 3 questions:")
        for i, q in enumerate(questions[:3], 1):
            print(f"   {i}. {q}")

    show_high_scores()

    # Play again loop
    if input("\n🎮 Play again? (y/n): ").lower() == 'y':
        start_game()
    else:
        print("👋 Thanks for playing!\n")


def save_score():
    """Save score using Tuple."""
    # Tuple: (name, score, time)
    entry = (player["name"], player["score"], datetime.now().strftime("%H:%M"))
    high_scores.append(entry)

    # Filter with lambda
    good = list(filter(lambda x: x[1] >= 50, high_scores))
    print(f"\n💾 Saved! Scores ≥50: {len(good)}")


def show_high_scores():
    """Display top 5 scores using map()."""
    if high_scores:
        print("\n🏆 TOP 5 HIGH SCORES:")
        # Sort and slice
        top = sorted(high_scores, key=lambda x: x[1], reverse=True)[:5]
        # Map with lambda
        formatted = list(map(lambda x: f"{x[0]} - {x[1]} pts ({x[2]})", top))
        # For loop with enumerate
        for i, score in enumerate(formatted, 1):
            print(f"   {i}. {score}")
    else:
        print("\n🏆 No scores yet!")


def main():
    """Main menu with while loop."""
    print("=" * 50)
    print("⚔️  MATH BATTLE ARENA ⚔️".center(50))
    print("=" * 50)
    print("\nDefeat monsters by solving math!")

    # While loop
    while True:
        print("\n📋 MENU:")
        print("1. Start Game")
        print("2. High Scores")
        print("3. Exit")

        try:
            choice = input("\nOption (1-3): ").strip()

            if choice == "1":
                start_game()
            elif choice == "2":
                show_high_scores()
            elif choice == "3":
                print("\n👋 Goodbye!\n")
                break
            else:
                print("❌ Enter 1-3")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


# -------------------------------
# 🚀 Start
# -------------------------------

if __name__ == "__main__":
    main()