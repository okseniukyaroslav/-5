import os
import sys
import json
import random
from datetime import datetime

DATA_DIR = "alchemist_data"
SAVE_FILE = os.path.join(DATA_DIR, "savegame.json")

INGREDIENT_POOL = [
    "Зоряний пил", "Квітковий нектар", "Сльоза дракона", "Мох вічності", "Вогняний корінь",
    "Крижаний кристалі", "Тіньовий лист", "Ртутний сік", "Пέρα кошової риби", "Серце саламандри",
    "Луска василіска", "Пливучий гриб", "Срібна роса", "Грозовий мох", "Пампушковий корінь",
    "Золота пилюка", "Кров троля", "Попіл фенікса", "Жало скорпіона", "Корінь мандрагори",
    "Інійне перо", "Мертва вода", "Гірський кришталь", "Ефірна смола", "Пил феї",
    "Коготь грифона", "Оголене серце", "Вовча ягода", "Зоряна живиця", "Світний лишайник",
    "Панцир скарабея", "Крило метелика-привида", "Ядро метеорита", "Сльоза русалки", "Павутина безодні",
    "Морозний сік", "Багряний бутон", "Квітковий шип", "Перо сирина", "Кіготь гарпії",
    "Сірка вулканів", "Солоний бурштин", "Пил єдинорога", "Деревний мозок", "Яблуко розбрату",
    "Іржаве залізо", "Свячена крейда", "Трухлявий пень", "Корінь болотяника", "Смола мантикори",
]

while len(INGREDIENT_POOL) < 200:
    idx = len(INGREDIENT_POOL) + 1
    INGREDIENT_POOL.append(f"Екзотичний інгредієнт #{idx}")

POTION_POOL = [
    {"name": "Зілля здоров'я", "cost": 15, "req": {"Зоряний пил": 2, "Квітковий нектар": 1}},
    {"name": "Зілля майна", "cost": 20, "req": {"Сльоза дракона": 1, "Мох вічності": 2}},
    {"name": "Вогняний еліксир", "cost": 25, "req": {"Вогняний корінь": 2, "Серце саламандри": 1}},
    {"name": "Крижаний щит", "cost": 25, "req": {"Крижаний кристалі": 2, "Інійне перо": 1}},
    {"name": "Еліксир невидимки", "cost": 30, "req": {"Тіньовий лист": 2, "Пил феї": 1}},
    {"name": "Протиотрута", "cost": 18, "req": {"Ртутний сік": 1, "Пампушковий корінь": 2}},
    {"name": "Зілля сили", "cost": 35, "req": {"Кров троля": 2, "Коготь грифона": 1}},
    {"name": "Зілля мудрості", "cost": 40, "req": {"Золота пилюка": 1, "Мертва вода": 2}},
    {"name": "Еліксир швидкості", "cost": 22, "req": {"Жало скорпіона": 2, "Крило метелика-привида": 1}},
    {"name": "Зілля регенерації", "cost": 45, "req": {"Попіл фенікса": 1, "Корінь мандрагори": 2}},
]

while len(POTION_POOL) < 50:
    idx = len(POTION_POOL) + 1
    c_ing = random.sample(INGREDIENT_POOL, 2)
    POTION_POOL.append({
        "name": f"Містичне зілля #{idx}",
        "cost": 10 + (idx % 40),
        "req": {c_ing[0]: 1, c_ing[1]: 1}
    })

def ensure_dir():
    try:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
    except Exception as e:
        print(f"[Помилка створення директорії]: {e}")

def load_game():
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[Помилка завантаження збереження]: {e}")
    return None

def save_game(state):
    try:
        ensure_dir()
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[Помилка збереження гри]: {e}")

def add_to_inventory(slots_dict, max_slots, max_stack, item_name, quantity):
    try:
        rem = quantity
        for slot_id in range(max_slots):
            s_key = str(slot_id)
            if s_key in slots_dict:
                if slots_dict[s_key]["name"] == item_name:
                    space = max_stack - slots_dict[s_key]["count"]
                    if space > 0:
                        add_amt = min(rem, space)
                        slots_dict[s_key]["count"] += add_amt
                        rem -= add_amt
                        if rem <= 0:
                            return 0
        for slot_id in range(max_slots):
            s_key = str(slot_id)
            if s_key not in slots_dict:
                if rem > 0:
                    add_amt = min(rem, max_stack)
                    slots_dict[s_key] = {"name": item_name, "count": add_amt}
                    rem -= add_amt
                    if rem <= 0:
                        return 0
        return rem
    except Exception as e:
        print(f"[Помилка інвентарю]: {e}")
        return quantity

def remove_from_inventory(slots_dict, max_slots, item_name, quantity):
    try:
        rem = quantity
        slots_to_clear = []
        for slot_id in range(max_slots):
            s_key = str(slot_id)
            if s_key in slots_dict and slots_dict[s_key]["name"] == item_name:
                if slots_dict[s_key]["count"] >= rem:
                    slots_dict[s_key]["count"] -= rem
                    rem = 0
                    if slots_dict[s_key]["count"] == 0:
                        slots_to_clear.append(s_key)
                    break
                else:
                    rem -= slots_dict[s_key]["count"]
                    slots_to_clear.append(s_key)
        for s_key in slots_to_clear:
            if s_key in slots_dict:
                del slots_dict[s_key]
        return rem == 0
    except Exception as e:
        print(f"[Помилка видалення з інвентарю]: {e}")
        return False

def count_item_in_inventory(slots_dict, max_slots, item_name):
    try:
        total = 0
        for slot_id in range(max_slots):
            s_key = str(slot_id)
            if s_key in slots_dict and slots_dict[s_key]["name"] == item_name:
                total += slots_dict[s_key]["count"]
        return total
    except Exception as e:
        print(f"[Помилка підрахунку предметів]: {e}")
        return 0

def daily_ingredient_drop(state):
    try:
        new_ings = random.sample(INGREDIENT_POOL, 5)
        print("\n--- НОВИЙ ІГРОВИЙ ДЕНЬ ---")
    
        for ing in new_ings:
            leftover = add_to_inventory(state["ingredients"], 25, 25, ing, 1)
            if leftover > 0:
                print(f"Сховище інгредієнтів переповнене! Втрачено: {ing} ({leftover} шт.)")
            else:
                print(f"Отримано інгредієнт: {ing} (1 шт.)")
    except Exception as e:
        print(f"[Помилка щоденного дропу]: {e}")

def show_inventories(state):
    try:
        print("\n=== ВАШІ ІНВЕНТАРІ ===")
        print("--- Інгредієнти (макс 25 слотів по 25 шт.) ---")
        ing_empty = True
        for i in range(25):
            s_key = str(i)
            if s_key in state["ingredients"]:
                item = state["ingredients"][s_key]
                print(f"  Слот {i+1:2d}: {item['name']} - {item['count']} шт.")
                ing_empty = False
        if ing_empty:
            print("  (Інвентар інгредієнтів порожній)")

        print("\n--- Зілля (макс 10 слотів по 10 шт.) ---")
        pot_empty = True
        for i in range(10):
            s_key = str(i)
            if s_key in state["potions"]:
                item = state["potions"][s_key]
                print(f"  Слот {i+1:2d}: {item['name']} - {item['count']} шт.")
                pot_empty = False
        if pot_empty:
            print("  (Інвентар зілля порожній)")
        print(f"\nЗолото: {state['gold']} | День: {state['day']} / 15 | Борг перед гільдією: {state['debt']} золота")
    except Exception as e:
        print(f"[Помилка відображення інвентарю]: {e}")

def craft_potion(state):
    try:
        print("\n=== КНИГА РЕЦЕПТІВ ТА КРАФТІНГ ===")
        print("Доступні зілля для створення:")
        for idx, recipe in enumerate(POTION_POOL):
            req_str = ", ".join([f"{k}: {v}" for k, v in recipe["req"].items()])
            print(f"{idx + 1}. {recipe['name']} (Ціна продажу: {recipe['cost']} золота) [Рецепт: {req_str}]")
        
        choice = input("\nВведіть номер зілля для створення (або 0 для виходу): ").strip()
        if not choice.isdigit():
            print("Некоректний ввід.")
            return
        
        c_idx = int(choice) - 1
        if c_idx < 0 or c_idx >= len(POTION_POOL):
            return

        recipe = POTION_POOL[c_idx]
        
        for ing_name, needed_qty in recipe["req"].items():
            have_qty = count_item_in_inventory(state["ingredients"], 25, ing_name)
            if have_qty < needed_qty:
                print(f"Недостатньо інгредієнта '{ing_name}'. Потрібно {needed_qty}, є {have_qty}.")
                return

        for ing_name, needed_qty in recipe["req"].items():
            remove_from_inventory(state["ingredients"], 25, ing_name, needed_qty)

        leftover = add_to_inventory(state["potions"], 10, 10, recipe["name"], 1)
        if leftover > 0:
            print("Слотів для зілля немає! Зілля розбилося через переповнення інвентарю!")
        else:
            print(f"Успішно створено: {recipe['name']}!")
    except Exception as e:
        print(f"[Помилка крафту]: {e}")

def end_day_market(state):
    try:
        print("\n=== РИНКОВИЙ ДЕНЬ (ПРОДАЖ ЗІЛЛЯ) ===")
        earned = 0
        pots_to_sell = list(state["potions"].items())
        
        for s_key, item in pots_to_sell:
            potion_data = next((p for p in POTION_POOL if p["name"] == item["name"]), None)
            price = potion_data["cost"] if potion_data else 10
            total_price = price * item["count"]
            earned += total_price
            print(f"Продано {item['count']} шт. '{item['name']}' за {total_price} золота.")
        
        state["potions"] = {}
        state["gold"] += earned
        
        print(f"Загалом виручено за день: {earned} золота.")
        
        tax = 20
        print(20 * "=")
        print(f"Гільдія вимагає податок/борг за день: {tax} золота.")
        state["gold"] -= tax
        
        state["day"] += 1
    except Exception as e:
        print(f"[Помилка ринкового дня]: {e}")

def check_game_over(state):
    try:
        if state["gold"] < 0:
            print("\n❌ ПОРАЗКА! Ви збанкрутували через борги перед гільдією алхіміків.")
            return True
        if state["day"] > 15:
            if state["gold"] >= 200:
                print(f"\n🎉 ПЕРЕМОГА! Ви успішно пережили 15 днів і накопичили {state['gold']} золота!")
                return True
            else:
                print(f"\n❌ ПОРАЗКА! Час вийшов, а ви назбирали лише {state['gold']} золота з 200 необхідних.")
                return True
        return False
    except Exception as e:
        print(f"[Помилка перевірки умов гри]: {e}")
        return False

def main():
    try:
        state = load_game()
        if not state:
            state = {
                "gold": 50,
                "day": 1,
                "debt": 0,
                "ingredients": {},
                "potions": {}
            }
            daily_ingredient_drop(state)

        while True:
            if check_game_over(state):
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
                break

            show_inventories(state)
            print("\n1. Зварити зілля")
            print("2. Переспати ніч та продати зілля на ринку (Наступний день)")
            print("3. Зберегти та вийти")
            
            choice = input("Оберіть дію: ").strip()
            if choice == "1":
                craft_potion(state)
                save_game(state)
            elif choice == "2":
                end_day_market(state)
                daily_ingredient_drop(state)
                save_game(state)
            elif choice == "3":
                save_game(state)
                print("Гру збережено. До зустрічі!")
                break
            else:
                print("Невірний вибір, спробуйте ще раз.")
    except Exception as e:
        print(f"[Критична помилка виконання програми]: {e}")

if __name__ == "__main__":
    main()