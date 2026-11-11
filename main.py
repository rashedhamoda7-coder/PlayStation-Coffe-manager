import flet as ft
import time
import math
import threading
import json
import os

DATA_FILE = "data.json"
HISTORY_FILE = "history.json"
SETTINGS_FILE = "settings.json"

APP_VERSION = 2                      # 2 = التسعير بالساعة
WHATSAPP_NUMBER = "963986687958"
QUARTER = 900                        # ربع ساعة بالثواني

default_settings = {
    "version": APP_VERSION,
    "price_1": 1000,
    "price_2": 2000,
    "price_3": 3000,
    "price_4": 4000,
}


def round_to_quarter(seconds):
    """تقريب لأقرب ربع ساعة، وأقل شي ربع ساعة."""
    if seconds <= 0:
        return 0
    quarters = int(seconds / QUARTER + 0.5)
    if quarters == 0:
        quarters = 1
    return quarters * QUARTER


def price_for(seconds, rate):
    """السعر لعدد ثواني (من مضاعفات ربع الساعة) وسعر الساعة."""
    quarters = int(seconds // QUARTER)
    return int(quarters * rate / 4.0 + 0.5)


def format_duration(seconds):
    """مثال: ساعة و 30 دقيقة"""
    total_minutes = int(seconds / 60.0 + 0.5)
    hours, minutes = divmod(total_minutes, 60)
    parts = []
    if hours:
        if hours == 1:
            parts.append("ساعة")
        elif hours == 2:
            parts.append("ساعتين")
        elif hours <= 10:
            parts.append(f"{hours} ساعات")
        else:
            parts.append(f"{hours} ساعة")
    if minutes:
        if minutes == 1:
            parts.append("دقيقة")
        elif minutes == 2:
            parts.append("دقيقتين")
        elif minutes <= 10:
            parts.append(f"{minutes} دقائق")
        else:
            parts.append(f"{minutes} دقيقة")
    if not parts:
        return "0 دقيقة"
    return " و ".join(parts)


def format_clock(seconds, round_up=False):
    """عداد بالساعات والدقائق: 01:30"""
    if seconds < 0:
        seconds = 0
    if round_up:
        minutes = int(math.ceil(seconds / 60.0))
    else:
        minutes = int(seconds // 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}"


def players_text(n):
    if n == 1:
        return "لاعب واحد"
    if n == 2:
        return "لاعبين"
    return f"{n} لاعبين"


def fresh_device():
    return {
        "status": "Available", "mode": None, "end_time": None, "start_time": None,
        "players": 1, "hourly_rate": default_settings["price_1"],
        "accumulated_time": 0, "original_fixed_time": 0, "overtime_time": 0,
    }


def backup_old_files():
    """أول تشغيل بالنسخة الجديدة: نحفظ ملفات التجريب القديمة باسم .bak ونبدأ من جديد."""
    for path in (DATA_FILE, HISTORY_FILE, SETTINGS_FILE):
        if os.path.exists(path):
            try:
                os.replace(path, path + ".bak")
            except Exception:
                pass


def main(page: ft.Page):
    page.title = "Level Up"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 20
    page.window_width = 450
    page.window_height = 800

    def format_price(price):
        return f"{price:,}"

    def show_snack(text, color):
        snack = ft.SnackBar(ft.Text(text), bgcolor=color)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def build_sessions_table(sessions):
        def cell(text, ratio, color=ft.Colors.WHITE, bold=False):
            return ft.Container(
                content=ft.Text(
                    text,
                    size=12,
                    color=color,
                    weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL,
                    text_align=ft.TextAlign.CENTER,
                ),
                expand=ratio,
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.all(4),
            )

        controls = [
            ft.Row([
                cell("الجهاز", 2, ft.Colors.BLUE_300, True),
                cell("الوقت", 3, ft.Colors.BLUE_300, True),
                cell("اللاعبين", 2, ft.Colors.BLUE_300, True),
                cell("السعر", 3, ft.Colors.BLUE_300, True),
            ], spacing=0),
            ft.Divider(height=1, color=ft.Colors.GREY_800),
        ]
        for s in sessions:
            controls.append(
                ft.Row([
                    cell(s.get("device", ""), 2),
                    cell(format_duration(s.get("played_minutes", 0) * 60), 3),
                    cell(str(s.get("players", 1)), 2),
                    cell(format_price(s.get("total_price", 0)) + " ل.س", 3, ft.Colors.BLUE_300, True),
                ], spacing=0)
            )
            controls.append(ft.Divider(height=1, color=ft.Colors.GREY_800))

        return ft.Container(
            content=ft.Column(controls, spacing=0),
            border=ft.Border.all(1, ft.Colors.GREY_800),
            border_radius=10,
        )

    def save_settings(new_settings):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(new_settings, f, ensure_ascii=False, indent=4)

    def load_settings():
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                if saved.get("version") == APP_VERSION:
                    for key, value in default_settings.items():
                        saved.setdefault(key, value)
                    return saved
            except Exception:
                pass
        # ملفات قديمة (محسوبة على 12 ثانية): نحفظها ونبدأ من جديد
        backup_old_files()
        fresh = dict(default_settings)
        save_settings(fresh)
        return fresh

    settings = load_settings()

    def rate_for(players):
        return settings.get(f"price_{players}", default_settings[f"price_{players}"])

    def load_data():
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "PS4 - 1": fresh_device(),
            "PS4 - 2": fresh_device(),
            "PS4 - 3": fresh_device(),
        }

    def save_data():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(devices, f, ensure_ascii=False, indent=4)

    def save_history(device_name, played_seconds, total_price, mode, players, is_closed=False):
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except Exception:
                    history = []

        history.append({
            "device": device_name,
            "players": players,
            "played_minutes": int(played_seconds // 60),
            "time_played": format_duration(played_seconds),
            "total_price": total_price,
            "mode": mode,
            "date": time.strftime("%Y-%m-%d"),
            "time": time.strftime("%H:%M:%S"),
            "is_closed": is_closed
        })

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

    devices = load_data()
    device_ui = {}
    device_timer_text = {}
    notified_devices = set()

    current_page = ft.ListView(expand=True, spacing=10, padding=20)
    alerts_container = ft.Column()

    async def open_drawer(e):
        # نفس طريقة السحب: بيفتح القائمة الجانبية
        try:
            await page.show_drawer()
        except Exception:
            page.drawer.open = True
            page.update()

    def show_devices_view(e=None):
        page.drawer.open = False
        page.drawer.selected_index = 0
        current_page.controls.clear()

        current_page.controls.extend([
            ft.Divider(height=20, color="transparent"),
            ft.Container(
                content=ft.Row([
                    create_device_card("PS4 - 1"),
                    create_device_card("PS4 - 2"),
                    create_device_card("PS4 - 3")
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20, wrap=True),
                alignment=ft.Alignment.CENTER,
                expand=True
            ),
            ft.Divider(height=30, color="transparent"),
            alerts_container,
            ft.Divider(height=40, color="transparent"),
            ft.Container(
                content=ft.Column([
                    ft.Text("تطوير", size=12, color=ft.Colors.GREY_500),
                    ft.Text("Rashed Hammoda", size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LINK, color=ft.Colors.BLUE_400, size=20),
                            ft.Text("LinkedIn", color=ft.Colors.BLUE_400, size=16, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                        url="https://www.linkedin.com/in/rashed-hamoda-01b068436/",
                        tooltip="صفحتي على لينكدإن"
                    ),
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHAT, color="#25D366", size=20),
                            ft.Text("تواصل مباشر عبر واتساب", color="#25D366", size=16, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                        url=f"https://wa.me/{WHATSAPP_NUMBER}",
                        tooltip="واتساب"
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                alignment=ft.Alignment.CENTER
            )
        ])
        update_ui()
        page.update()

    def show_pricing_view(e):
        page.drawer.open = False
        page.drawer.selected_index = 1

        txt_p1 = ft.TextField(label="سعر الساعة للاعب واحد", value=str(settings["price_1"]), keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)
        txt_p2 = ft.TextField(label="سعر الساعة للاعبين", value=str(settings["price_2"]), keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)
        txt_p3 = ft.TextField(label="سعر الساعة لثلاثة لاعبين", value=str(settings["price_3"]), keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)
        txt_p4 = ft.TextField(label="سعر الساعة لأربعة لاعبين", value=str(settings["price_4"]), keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)

        def save_prices(e):
            try:
                values = [int(t.value) for t in (txt_p1, txt_p2, txt_p3, txt_p4)]
                if any(v <= 0 for v in values):
                    raise ValueError
            except Exception:
                show_snack("اكتب أرقام صحيحة", ft.Colors.RED_700)
                return
            settings["price_1"], settings["price_2"], settings["price_3"], settings["price_4"] = values
            save_settings(settings)
            show_snack("تم حفظ الأسعار", ft.Colors.GREEN_700)

        current_page.controls.clear()
        current_page.controls.extend([
            ft.Text("سعر الساعة", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
            ft.Divider(height=20, color="transparent"),
            txt_p1, txt_p2, txt_p3, txt_p4,
            ft.Divider(height=20, color="transparent"),
            ft.Button("حفظ الأسعار", width=300, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=save_prices),
            ft.TextButton("رجوع للأجهزة", on_click=show_devices_view, style=ft.ButtonStyle(color=ft.Colors.GREY_400))
        ])
        page.update()

    def show_reports_view(e):
        page.drawer.open = False
        page.drawer.selected_index = 3

        history_data = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    history_data = json.load(f)
                except Exception:
                    history_data = []

        closed_sessions = [s for s in history_data if s.get("is_closed", False)]

        if not closed_sessions:
            current_page.controls.clear()
            current_page.controls.extend([
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=show_devices_view, icon_color=ft.Colors.WHITE),
                    ft.Text("التقارير", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=20, color="transparent"),
                ft.Text("ما في تقارير بعد.", size=24, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
            ])
            page.update()
            return

        daily_data = {}
        for session in closed_sessions:
            date = session.get("date", "Unknown")
            if date not in daily_data:
                daily_data[date] = {"sessions": [], "total_revenue": 0, "total_minutes": 0}

            daily_data[date]["sessions"].append(session)
            daily_data[date]["total_revenue"] += session.get("total_price", 0)
            daily_data[date]["total_minutes"] += session.get("played_minutes", 0)

        day_cards = []
        for date, info in sorted(daily_data.items(), reverse=True):
            time_str = format_duration(info["total_minutes"] * 60)

            def show_daily_popup(e, day_date=date, day_sessions=info["sessions"]):
                table = build_sessions_table(list(reversed(day_sessions)))
                screen_w = getattr(page, "width", None) or 360
                dialog_width = min(480, screen_w - 40)

                dialog = ft.AlertDialog(
                    title=ft.Text(f"تقرير يوم {day_date}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD),
                    bgcolor="#1E1E1E",
                    inset_padding=ft.Padding.all(10),
                    content_padding=ft.Padding.all(10),
                    content=ft.Container(
                        content=ft.Column([table], scroll=ft.ScrollMode.ADAPTIVE),
                        width=dialog_width,
                        height=400,
                    ),
                    actions=[ft.TextButton("إغلاق", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.RED_400))],
                )
                page.show_dialog(dialog)
                page.update()

            card = ft.Container(
                content=ft.Column([
                    ft.Text(date, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Divider(height=10, color=ft.Colors.GREY_800),
                    ft.Text(f"الإيرادات: {format_price(info['total_revenue'])} ل.س", color=ft.Colors.GREEN_400, size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"الوقت: {time_str}", color=ft.Colors.BLUE_300, size=14, weight=ft.FontWeight.BOLD),
                ], horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                bgcolor="#1E1E1E",
                padding=15,
                border_radius=10,
                border=ft.Border.all(1, ft.Colors.GREY_800),
                on_click=show_daily_popup,
                ink=True
            )
            day_cards.append(card)

        current_page.controls.clear()
        current_page.controls.extend([
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=show_devices_view, icon_color=ft.Colors.WHITE),
                ft.Text("التقارير", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=20, color="transparent"),
            ft.Column(day_cards, spacing=10)
        ])
        page.update()

    def show_current_history_view(e):
        page.drawer.open = False
        page.drawer.selected_index = 2

        history_data = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    history_data = json.load(f)
                except Exception:
                    history_data = []

        open_sessions = [s for s in history_data if not s.get("is_closed", False)]

        def confirm_end_day(e):
            def do_end_day(e):
                new_history = []
                for s in history_data:
                    if not s.get("is_closed", False):
                        s["is_closed"] = True
                    new_history.append(s)

                with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                    json.dump(new_history, f, ensure_ascii=False, indent=4)

                page.pop_dialog()
                show_current_history_view(None)

            dialog_confirm = ft.AlertDialog(
                title=ft.Text("إنهاء اليوم؟", color=ft.Colors.RED_400, weight=ft.FontWeight.BOLD),
                content=ft.Text("رح تنتقل كل الجلسات الحالية للتقارير. متأكد؟", color=ft.Colors.WHITE),
                bgcolor="#1E1E1E",
                inset_padding=ft.Padding.all(50),
                actions=[
                    ft.TextButton("إلغاء", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.GREY_400)),
                    ft.TextButton("نعم، إنهاء اليوم", on_click=do_end_day, style=ft.ButtonStyle(color=ft.Colors.RED_400)),
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            page.show_dialog(dialog_confirm)
            dialog_confirm.open = True
            page.update()

        table = build_sessions_table(list(reversed(open_sessions)))

        current_page.controls.clear()
        current_page.controls.extend([
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=show_devices_view, icon_color=ft.Colors.WHITE),
                ft.Column([
                    ft.Text("السجل الحالي", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
                    ft.Button("إنهاء اليوم", bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, on_click=confirm_end_day),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Divider(height=20, color="transparent"),
            table if open_sessions else ft.Text("ما في جلسات حالياً.", size=24, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
        ])
        page.update()

    async def handle_drawer_change(e):
        selected_index = e.control.selected_index
        try:
            await page.close_drawer()
        except Exception:
            pass
        page.drawer.open = False
        page.update()
        if selected_index == 0:
            show_devices_view()
        elif selected_index == 1:
            show_pricing_view(e)
        elif selected_index == 2:
            show_current_history_view(e)
        elif selected_index == 3:
            show_reports_view(e)

    page.drawer = ft.NavigationDrawer(
        bgcolor="#1E1E1E",
        on_change=handle_drawer_change,
        selected_index=0,
        controls=[
            ft.Container(height=20),
            ft.NavigationDrawerDestination(icon=ft.Icons.HOME, label="الأجهزة"),
            ft.NavigationDrawerDestination(icon=ft.Icons.ATTACH_MONEY, label="الأسعار"),
            ft.NavigationDrawerDestination(icon=ft.Icons.HISTORY, label="السجل الحالي"),
            ft.NavigationDrawerDestination(icon=ft.Icons.BAR_CHART, label="التقارير"),
        ],
    )

    page.appbar = ft.AppBar(
        title=ft.Row([
            ft.Icon(ft.Icons.SPORTS_ESPORTS, color=ft.Colors.BLUE_300),
            ft.Text("LEVEL UP", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8, tight=True),
        bgcolor="#121212",
        center_title=True,
        leading=ft.IconButton(icon=ft.Icons.MENU, on_click=open_drawer, icon_color=ft.Colors.WHITE),
    )

    def close_dialog(e):
        page.pop_dialog()
        page.update()

    def close_alert(e):
        page.pop_dialog()
        page.update()

    def make_players_dropdown():
        return ft.Dropdown(
            options=[
                ft.dropdown.Option("1", "لاعب واحد"),
                ft.dropdown.Option("2", "لاعبين"),
                ft.dropdown.Option("3", "3 لاعبين"),
                ft.dropdown.Option("4", "4 لاعبين"),
            ],
            value="1",
            width=200,
            color=ft.Colors.WHITE,
            border_color=ft.Colors.BLUE_300,
            label="عدد اللاعبين",
        )

    def quick_time_buttons(on_pick):
        return ft.Row([
            ft.Button("ساعة", on_click=lambda e: on_pick(60)),
            ft.Button("ساعة ونص", on_click=lambda e: on_pick(90)),
            ft.Button("ساعتين", on_click=lambda e: on_pick(120)),
        ], alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=8, run_spacing=8)

    def confirm_let_play(device_name):
        def do_let_play(e):
            data = devices[device_name]

            if data.get("original_fixed_time", 0) == 0:
                data["original_fixed_time"] = data["end_time"] - data["start_time"]
                if data["original_fixed_time"] < 0: data["original_fixed_time"] = 0

            if time.time() > data["end_time"]:
                data["overtime_time"] = time.time() - data["end_time"]
            else:
                data["overtime_time"] = 0

            data["mode"] = "open"
            data["start_time"] = time.time()
            data["end_time"] = None

            notified_devices.discard(device_name)
            save_data()
            page.pop_dialog()
            update_ui()
            refresh_alerts_table()

        dialog = ft.AlertDialog(
            title=ft.Text("خليهم يكملوا؟", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            content=ft.Text(f"حوّل {device_name} لوقت مفتوح؟", color=ft.Colors.WHITE),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            actions=[
                ft.TextButton("إلغاء", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.GREY_400)),
                ft.TextButton("نعم", on_click=do_let_play, style=ft.ButtonStyle(color=ft.Colors.GREEN_400)),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        page.show_dialog(dialog)

        page.update()

    def open_extend_popup(device_name):
        time_input = ft.TextField(label="زيادة بالدقائق", keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)

        def set_minutes(minutes):
            time_input.value = str(minutes)
            page.update()

        def add_custom_time(e):
            try:
                minutes = int(time_input.value)
                if minutes <= 0: raise ValueError
            except Exception:
                show_snack("اكتب عدد دقائق صحيح", ft.Colors.RED_700)
                return

            devices[device_name]["accumulated_time"] = devices[device_name].get("accumulated_time", 0) + (time.time() - devices[device_name]["start_time"])

            devices[device_name]["mode"] = "fixed"
            devices[device_name]["start_time"] = time.time()
            devices[device_name]["end_time"] = time.time() + minutes * 60

            notified_devices.discard(device_name)
            save_data()
            page.pop_dialog()
            update_ui()
            refresh_alerts_table()

        def switch_to_open_time(e):
            devices[device_name]["accumulated_time"] = devices[device_name].get("accumulated_time", 0) + (time.time() - devices[device_name]["start_time"])

            devices[device_name]["mode"] = "open"
            devices[device_name]["start_time"] = time.time()
            devices[device_name]["end_time"] = None

            notified_devices.discard(device_name)
            save_data()
            page.pop_dialog()
            update_ui()
            refresh_alerts_table()

        dialog = ft.AlertDialog(
            title=ft.Text(f"زيادة وقت - {device_name}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                time_input,
                ft.Text("اختيار سريع:", size=14, color=ft.Colors.GREY_400),
                quick_time_buttons(set_minutes),
                ft.Divider(height=10, color="transparent"),
                ft.Button("زيادة الوقت", on_click=add_custom_time, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE),
                ft.Button("تحويل لوقت مفتوح", on_click=switch_to_open_time, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("إلغاء", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog)

        page.update()

    def end_session(device_name):
        data = devices[device_name]
        now = time.time()

        if data["mode"] == "fixed":
            actual_seconds = now - data["start_time"]
            if now > data["end_time"]:
                actual_seconds = data["end_time"] - data["start_time"]
                overtime_seconds = now - data["end_time"]
            else:
                overtime_seconds = 0
        elif data["mode"] == "open":
            actual_seconds = now - data["start_time"]
            overtime_seconds = 0
        else:
            return

        actual_seconds += data.get("accumulated_time", 0) + data.get("original_fixed_time", 0)
        overtime_seconds += data.get("overtime_time", 0)

        # التقريب مرة وحدة على مجموع الوقت، والسعر بيطلع من الوقت بعد التقريب
        rate = data.get("hourly_rate", default_settings["price_1"])
        total_seconds = round_to_quarter(actual_seconds + overtime_seconds)
        total_price = price_for(total_seconds, rate)

        content_list = [
            ft.Text(f"الجهاز: {device_name}", size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10, color=ft.Colors.GREY_800),
            ft.Text(f"وقت اللعب: {format_duration(actual_seconds)}", size=14, color=ft.Colors.GREY_400),
        ]

        if overtime_seconds > 0:
            content_list.append(ft.Text(f"وقت زيادة: {format_duration(overtime_seconds)}", size=14, color=ft.Colors.YELLOW_500))

        content_list.extend([
            ft.Divider(height=10, color=ft.Colors.GREY_800),
            ft.Text(f"الوقت المحسوب: {format_duration(total_seconds)}", size=16, color=ft.Colors.WHITE),
            ft.Text("(التقريب لأقرب ربع ساعة)", size=12, color=ft.Colors.GREY_500),
            ft.Text(f"السعر النهائي: {format_price(total_price)} ل.س", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300)
        ])

        receipt = ft.AlertDialog(
            title=ft.Text(f"الإيصال - {device_name}", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column(content_list, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
            actions=[ft.TextButton("إغلاق وتحرير الجهاز", on_click=lambda e: reset_device_and_save(device_name, total_seconds, total_price, data["mode"], data.get("players", 1)), style=ft.ButtonStyle(color=ft.Colors.GREEN_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        page.show_dialog(receipt)

    def reset_device_and_save(device_name, total_seconds, total_price, mode, players):
        save_history(device_name, total_seconds, total_price, mode, players, is_closed=False)

        devices[device_name] = fresh_device()
        notified_devices.discard(device_name)
        save_data()

        page.pop_dialog()
        update_ui()
        refresh_alerts_table()

    def refresh_alerts_table():
        alerts_container.controls.clear()

        for dev_name, data in devices.items():
            if data["status"] == "Busy":
                if data["mode"] == "fixed" and data["end_time"] <= time.time():
                    alerts_container.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Text(f"{dev_name}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER),
                                ft.Text("خلص الوقت!", size=14, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
                                ft.Row([
                                    ft.Button("خليهم يكملوا", bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=lambda e, d=dev_name: confirm_let_play(d)),
                                    ft.Button("إنهاء", bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, on_click=lambda e, d=dev_name: end_session(d))
                                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                            bgcolor="#2A0000",
                            padding=15,
                            border_radius=10,
                            border=ft.Border.all(1, ft.Colors.RED_500),
                            width=300
                        )
                    )
        if len(alerts_container.controls) == 0:
            alerts_container.controls.append(ft.Text("ما في تنبيهات", color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER))
        page.update()

    def timer_info(data):
        """نص العداد ولونه للجهاز المشغول (ساعات ودقائق)."""
        now = time.time()
        if data["mode"] == "fixed":
            remaining = data["end_time"] - now
            if remaining <= 0:
                return "+" + format_clock(now - data["end_time"]), ft.Colors.YELLOW_500
            return format_clock(remaining, round_up=True), ft.Colors.WHITE
        if data["mode"] == "open":
            return format_clock(now - data["start_time"]), ft.Colors.WHITE
        return "", ft.Colors.WHITE

    def update_timers():
        while True:
            needs_update = False
            for dev_name, data in devices.items():
                if data["status"] == "Busy" and data["mode"] in ("fixed", "open"):
                    text, color = timer_info(data)
                    device_timer_text[dev_name].value = text
                    device_timer_text[dev_name].color = color
                    needs_update = True
            if needs_update:
                try:
                    page.update()
                    refresh_alerts_table()
                except Exception:
                    pass
            time.sleep(1)

    def blink_alerts():
        while True:
            needs_update = False
            for dev_name, data in devices.items():
                if data["status"] == "Busy" and data["mode"] == "fixed" and data["end_time"] <= time.time():
                    current_border = device_ui[dev_name].border
                    if current_border and current_border.top.color == ft.Colors.RED_500:
                        device_ui[dev_name].border = ft.Border.all(2, ft.Colors.YELLOW_500)
                        device_ui[dev_name].shadow = ft.BoxShadow(blur_radius=20, color=ft.Colors.YELLOW_500, offset=ft.Offset(0, 0))
                    else:
                        device_ui[dev_name].border = ft.Border.all(2, ft.Colors.RED_500)
                        device_ui[dev_name].shadow = ft.BoxShadow(blur_radius=20, color=ft.Colors.RED_500, offset=ft.Offset(0, 0))
                    needs_update = True

            if needs_update:
                try:
                    page.update()
                except Exception:
                    pass
            time.sleep(0.5)

    def start_session(device_name, seconds=None, is_open=False, players=1, rate=None):
        if rate is None:
            rate = rate_for(players)

        if is_open:
            devices[device_name]["mode"] = "open"
            devices[device_name]["start_time"] = time.time()
        else:
            devices[device_name]["mode"] = "fixed"
            devices[device_name]["start_time"] = time.time()
            devices[device_name]["end_time"] = time.time() + seconds

        devices[device_name]["status"] = "Busy"
        devices[device_name]["players"] = players
        devices[device_name]["hourly_rate"] = rate
        devices[device_name]["accumulated_time"] = 0
        devices[device_name]["original_fixed_time"] = 0
        devices[device_name]["overtime_time"] = 0
        save_data()
        update_ui()
        page.pop_dialog()
        page.update()
        refresh_alerts_table()

    def update_ui():
        for dev_name, ui_element in device_ui.items():
            card = ui_element
            if devices[dev_name]["status"] == "Busy":
                is_time_up = False
                if devices[dev_name]["mode"] == "fixed":
                    remaining = int(devices[dev_name]["end_time"] - time.time())
                    if remaining <= 0:
                        is_time_up = True

                players_label = players_text(devices[dev_name].get('players', 1))
                if is_time_up:
                    card.bgcolor = "#3E2700"
                    card.content.controls[0].content.controls[1].value = f"● وقت زيادة! ({players_label})"
                    card.content.controls[0].content.controls[1].color = ft.Colors.YELLOW_500
                else:
                    card.bgcolor = "#2A0000"
                    card.border = ft.Border.all(2, ft.Colors.RED_500)
                    card.shadow = ft.BoxShadow(blur_radius=15, color=ft.Colors.RED_500, offset=ft.Offset(0, 0))
                    card.content.controls[0].content.controls[1].value = f"● مشغول ({players_label})"
                    card.content.controls[0].content.controls[1].color = ft.Colors.RED_400

                device_timer_text[dev_name].visible = True

                if devices[dev_name]["mode"] == "fixed" or devices[dev_name]["mode"] == "open":
                    card.content.controls[1].visible = False # extend_btn
                    card.content.controls[2].visible = True  # end_btn

                text, color = timer_info(devices[dev_name])
                device_timer_text[dev_name].value = text
                device_timer_text[dev_name].color = color
            else:
                card.bgcolor = "#1E1E1E"
                card.border = ft.Border.all(1, ft.Colors.GREY_700)
                card.shadow = ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_54, offset=ft.Offset(0, 4))
                card.content.controls[0].content.controls[1].value = "● متاح"
                card.content.controls[0].content.controls[1].color = ft.Colors.GREEN_400
                device_timer_text[dev_name].value = ""
                device_timer_text[dev_name].visible = False
                card.content.controls[1].visible = False
                card.content.controls[2].visible = False
        page.update()

    def open_time_popup_from_card(device_name):
        if devices[device_name]["status"] == "Busy":
            end_session(device_name)
            return

        def go_to_time_selection(e):
            page.pop_dialog()
            page.update()
            open_custom_time_popup(device_name)

        def go_to_cash_selection(e):
            page.pop_dialog()
            page.update()
            open_cash_popup(device_name)

        def go_to_open_time(e):
            page.pop_dialog()
            page.update()
            open_open_time_popup(device_name)

        dialog_main = ft.AlertDialog(
            title=ft.Text(f"بدء جلسة - {device_name}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                ft.Text("اختار طريقة البدء:", size=18, color=ft.Colors.WHITE),
                ft.Button("بالوقت", width=200, bgcolor="#333333", color=ft.Colors.WHITE, on_click=go_to_time_selection),
                ft.Button("بالمبلغ", width=200, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, on_click=go_to_cash_selection),
                ft.Button("وقت مفتوح", width=200, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=go_to_open_time)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("إلغاء", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog_main)
        dialog_main.open = True
        page.update()

    def back_to_start_popup(device_name):
        page.pop_dialog()
        page.update()
        open_time_popup_from_card(device_name)

    def open_custom_time_popup(device_name):
        time_input = ft.TextField(label="المدة بالدقائق", keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)
        players_dropdown = make_players_dropdown()

        def set_minutes(minutes):
            time_input.value = str(minutes)
            page.update()

        def start_custom(e):
            try:
                minutes = int(time_input.value)
                p = int(players_dropdown.value)
                if minutes <= 0: raise ValueError
            except Exception:
                show_snack("اكتب عدد دقائق صحيح", ft.Colors.RED_700)
                return
            start_session(device_name, seconds=minutes * 60, players=p, rate=rate_for(p))

        dialog = ft.AlertDialog(
            title=ft.Text(f"بالوقت - {device_name}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                time_input,
                ft.Text("اختيار سريع:", size=14, color=ft.Colors.GREY_400),
                quick_time_buttons(set_minutes),
                players_dropdown,
                ft.Button("ابدأ", on_click=start_custom, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("رجوع", on_click=lambda e: back_to_start_popup(device_name), style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog)

        page.update()

    def open_cash_popup(device_name):
        amount_input = ft.TextField(label="المبلغ (ل.س)", keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)
        players_dropdown = make_players_dropdown()

        def calculate_and_start(e):
            try:
                amount = int(amount_input.value)
                p = int(players_dropdown.value)
                rate = rate_for(p)
                if amount <= 0 or rate <= 0: raise ValueError
            except Exception:
                show_snack("اكتب مبلغ صحيح", ft.Colors.RED_700)
                return

            # الوقت من المبلغ، بعد التقريب لأقرب ربع ساعة (والسعر بيتحسب من الوقت المقرّب)
            seconds = round_to_quarter(amount / rate * 3600.0)
            start_session(device_name, seconds=seconds, players=p, rate=rate)

        dialog = ft.AlertDialog(
            title=ft.Text(f"بالمبلغ - {device_name}", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                amount_input,
                players_dropdown,
                ft.Button("احسب وابدأ", on_click=calculate_and_start, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("رجوع", on_click=lambda e: back_to_start_popup(device_name), style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog)

        page.update()

    def open_open_time_popup(device_name):
        players_dropdown = make_players_dropdown()

        def start_open(e):
            p = int(players_dropdown.value)
            start_session(device_name, is_open=True, players=p, rate=rate_for(p))

        dialog = ft.AlertDialog(
            title=ft.Text(f"وقت مفتوح - {device_name}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                players_dropdown,
                ft.Button("ابدأ", on_click=start_open, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("رجوع", on_click=lambda e: back_to_start_popup(device_name), style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog)

        page.update()

    def create_device_card(device_name):
        timer_text = ft.Text("", size=22, weight=ft.FontWeight.BOLD, visible=False, font_family="monospace")
        device_timer_text[device_name] = timer_text

        extend_btn = ft.Button("زيادة الوقت", bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, visible=False, on_click=lambda e: open_extend_popup(device_name))
        end_btn = ft.Button("إنهاء الجلسة", bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, visible=False, on_click=lambda e: end_session(device_name))

        clickable_text = ft.GestureDetector(
            content=ft.Column([
                ft.Text(device_name, size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("● متاح", color=ft.Colors.GREEN_400, size=16, weight=ft.FontWeight.BOLD),
                timer_text,
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            on_tap=lambda e: open_time_popup_from_card(device_name)
        )

        card_content = ft.Container(
            content=ft.Column([
                clickable_text,
                extend_btn,
                end_btn
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            width=320, height=280,
            bgcolor="#1E1E1E",
            border_radius=20,
            alignment=ft.Alignment.CENTER,
            padding=20,
            on_click=lambda e: open_time_popup_from_card(device_name),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
        )

        device_ui[device_name] = card_content
        return card_content

    page.add(current_page)

    show_devices_view()
    threading.Thread(target=update_timers, daemon=True).start()
    threading.Thread(target=blink_alerts, daemon=True).start()

ft.run(main)
