import math
import flet as ft
from typing import List, Dict

import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
class PizzaCalculator:
    def __init__(self):
        self.results = []

    def calculate_single_pizza(self, diameter: float, price: float, name: str = ""):
        if diameter <= 0 or price <= 0:
            return None
        area = math.pi * (diameter * diameter) / 4
        ratio = area / price
        return {
            "type": "Одна пицца",
            "name": name if name else "Без названия",
            "diameter": diameter,
            "price": price,
            "area": area,
            "ratio": ratio
        }

    def calculate_set(self, pizzas: List[Dict], set_name: str = ""):
        if not pizzas:
            return None
        total_area = 0
        total_price = 0
        for pizza in pizzas:
            if pizza["diameter"] <= 0 or pizza["price"] <= 0:
                return None
            area = math.pi * (pizza["diameter"] * pizza["diameter"]) / 4
            total_area += area
            total_price += pizza["price"]
        ratio = total_area / total_price if total_price > 0 else 0
        return {
            "type": "Сет из пицц",
            "name": set_name if set_name else f"Сет из {len(pizzas)} пицц",
            "pizzas": pizzas,
            "total_area": total_area,
            "total_price": total_price,
            "ratio": ratio
        }


def main(page: ft.Page):
    page.title = "Калькулятор пиццы"
    page.window_icon = resource_path("assets/icon.png")
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.Colors.ORANGE_50

    calculator = PizzaCalculator()
    mode = "single"
    set_pizzas = []

    single_name = ft.TextField(label="Название пиццы (необязательно)", width=300, hint_text="Например: Маргарита")
    single_diameter = ft.TextField(label="Диаметр (см)", keyboard_type=ft.KeyboardType.NUMBER, width=300,
                                   hint_text="Например: 30")
    single_price = ft.TextField(label="Цена (руб)", keyboard_type=ft.KeyboardType.NUMBER, width=300,
                                hint_text="Например: 599")

    set_name = ft.TextField(label="Название сета (необязательно)", width=300, hint_text="Например: Семейный сет")
    set_container = ft.Column(spacing=10)

    results_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=400)

    def update_results_list():
        results_list.controls.clear()
        if not calculator.results:
            results_list.controls.append(ft.Text("📋 Нет сохраненных результатов", italic=True, color=ft.Colors.GREY))
        else:
            for i, item in enumerate(calculator.results):
                color = ft.Colors.GREEN_700 if i == 0 else ft.Colors.BLACK87
                results_list.controls.append(ft.Container(
                    content=ft.Text(item["text"], color=color, size=12),
                    padding=10, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=8,
                    margin=ft.margin.only(bottom=6), bgcolor=ft.Colors.WHITE,
                ))
        page.update()

    def add_result_to_list(result):
        if result["type"] == "Одна пицца":
            text = f"🍕 {result['name']}: {result['diameter']:.0f}см, {result['price']:.0f}руб → {result['ratio']:.2f} см²/руб"
        else:
            text = f"📦 {result['name']}: "
            pizza_details = []
            for i, pizza in enumerate(result["pizzas"], 1):
                pizza_details.append(f"{i}.{pizza['name']}({pizza['diameter']:.0f}см)" if pizza[
                    "name"] else f"{i}.{pizza['diameter']:.0f}см")
            text += ", ".join(pizza_details) + f" → {result['ratio']:.2f} см²/руб"
        calculator.results.insert(0, {"text": text, "ratio": result["ratio"]})
        calculator.results = calculator.results[:10]
        update_results_list()
        page.snack_bar = ft.SnackBar(ft.Text(f"✅ Добавлено! Соотношение: {result['ratio']:.2f} см²/руб"), duration=2000)
        page.snack_bar.open = True
        page.update()

    def add_pizza_to_set(e):
        pizza_name = ft.TextField(label="Название пиццы (необязательно)", width=280, hint_text="Например: Пепперони")
        pizza_diameter = ft.TextField(label="Диаметр (см)", keyboard_type=ft.KeyboardType.NUMBER, width=280)
        pizza_price = ft.TextField(label="Цена (руб)", keyboard_type=ft.KeyboardType.NUMBER, width=280)
        delete_btn = ft.ElevatedButton("Удалить", on_click=lambda e, idx=len(set_pizzas): remove_pizza(idx))
        pizza_card = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text(f"🍕 Пицца {len(set_pizzas) + 1}", size=16, weight=ft.FontWeight.BOLD), delete_btn],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                pizza_name, pizza_diameter, pizza_price,
            ], spacing=10),
            border=ft.border.all(1, ft.Colors.GREY_400), border_radius=10, padding=15, margin=ft.margin.only(bottom=10),
            bgcolor=ft.Colors.WHITE,
        )
        set_pizzas.append({"name": pizza_name, "diameter": pizza_diameter, "price": pizza_price, "card": pizza_card,
                           "delete": delete_btn})
        set_container.controls.append(pizza_card)
        page.update()

    def remove_pizza(index):
        if index < len(set_pizzas):
            set_container.controls.pop(index)
            set_pizzas.pop(index)
            for i, pizza in enumerate(set_pizzas):
                pizza["card"].content.controls[0].controls[0].value = f"🍕 Пицца {i + 1}"
                pizza["delete"].on_click = lambda e, idx=i: remove_pizza(idx)
            page.update()

    def clear_set():
        set_name.value = ""
        for pizza in set_pizzas:
            pizza["name"].value = ""
            pizza["diameter"].value = ""
            pizza["price"].value = ""
        page.update()

    def calculate(e):
        try:
            if mode == "single":
                if not single_diameter.value or not single_price.value:
                    page.snack_bar = ft.SnackBar(ft.Text("⚠️ Заполните поля"), duration=2000)
                    page.snack_bar.open = True
                    return
                diameter = float(single_diameter.value)
                price = float(single_price.value)
                name = single_name.value or ""
                if diameter <= 0 or price <= 0:
                    raise ValueError
                result = calculator.calculate_single_pizza(diameter, price, name)
                if result:
                    add_result_to_list(result)
                    single_name.value = ""
                    single_diameter.value = ""
                    single_price.value = ""
                    page.update()
            else:
                pizzas = []
                for pizza in set_pizzas:
                    name_val = pizza["name"].value or ""
                    diam_val = pizza["diameter"].value
                    price_val = pizza["price"].value
                    if not diam_val or not price_val:
                        page.snack_bar = ft.SnackBar(ft.Text("⚠️ Заполните все поля"), duration=2000)
                        page.snack_bar.open = True
                        return
                    diam = float(diam_val)
                    price = float(price_val)
                    if diam <= 0 or price <= 0:
                        raise ValueError
                    pizzas.append({"name": name_val, "diameter": diam, "price": price})
                if len(pizzas) < 2:
                    page.snack_bar = ft.SnackBar(ft.Text("⚠️ Добавьте хотя бы 2 пиццы"), duration=2000)
                    page.snack_bar.open = True
                    return
                result = calculator.calculate_set(pizzas, set_name.value or "")
                if result:
                    add_result_to_list(result)
                    clear_set()
                    page.update()
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Введите числа больше 0"), duration=2000)
            page.snack_bar.open = True
            page.update()

    def change_mode(e):
        nonlocal mode
        mode = e.control.data
        if mode == "single":
            single_container.visible = True
            set_interface.visible = False
            add_pizza_btn.visible = False
            btn_single.bgcolor = ft.Colors.ORANGE_100
            btn_set.bgcolor = None
        else:
            single_container.visible = False
            set_interface.visible = True
            add_pizza_btn.visible = True
            btn_single.bgcolor = None
            btn_set.bgcolor = ft.Colors.ORANGE_100
        page.update()

    single_container = ft.Container(
        content=ft.Column([single_name, single_diameter, single_price], spacing=15,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        visible=True, bgcolor=ft.Colors.WHITE, border_radius=10, padding=20
    )

    set_interface = ft.Column([set_name, ft.Text("Пиццы в сете:", size=14, weight=ft.FontWeight.BOLD), set_container],
                              spacing=15, visible=False)

    btn_single = ft.ElevatedButton("🍕 Одна пицца", data="single", on_click=change_mode, width=150)
    btn_set = ft.ElevatedButton("📦 Сет из пицц", data="set", on_click=change_mode, width=150)
    mode_switch = ft.Row([btn_single, btn_set], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    add_pizza_btn = ft.ElevatedButton("➕ Добавить пиццу", on_click=add_pizza_to_set, visible=False)
    calculate_btn = ft.ElevatedButton("🧮 Рассчитать", on_click=calculate, width=300, height=50)
    clear_btn = ft.TextButton("🗑️ Очистить историю",
                              on_click=lambda e: [calculator.results.clear(), update_results_list()])

    update_results_list()

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("🍕 Калькулятор пиццы 🍕", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.ORANGE_700),
                ft.Text("Узнайте, какая пицца выгоднее! (чем больше см. на 1 руб, тем выгоднее),", size=16, color=ft.Colors.GREY),
                ft.Divider(),
                mode_switch, ft.Container(height=10),
                single_container, set_interface, add_pizza_btn,
                ft.Container(height=10), calculate_btn,
                ft.Container(height=10), clear_btn,
                ft.Divider(),
                ft.Text("📊 Последние 10 расчетов:", size=18, weight=ft.FontWeight.BOLD),
                results_list
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20
        )
    )

    add_pizza_to_set(None)
    add_pizza_to_set(None)


ft.app(target=main)