import flet as ft
import time
import threading 
import json
import os

DATA_FILE = "data.json"
HISTORY_FILE = "history.json"
SETTINGS_FILE = "settings.json"

def main(page: ft.Page):
    page.title = "PlayStation Station Management"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"  
    page.padding = 20
    page.window_width = 450 
    page.window_height = 800

    def format_price(price):
        return f"{price:,}"

    default_settings = {
        "price_1": 1200,
        "price_2": 2000,
        "price_3": 2800,
        "price_4": 3500
    }

    def load_settings():
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return default_settings

    def save_settings(new_settings):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(new_settings, f, ensure_ascii=False, indent=4)

    settings = load_settings()

    def load_data():
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "PS4 - 1": {"status": "Available", "mode": None, "end_time": None, "start_time": None, "players": 1, "hourly_rate": 1200, "accumulated_time": 0, "original_fixed_time": 0, "overtime_time": 0},
            "PS4 - 2": {"status": "Available", "mode": None, "end_time": None, "start_time": None, "players": 1, "hourly_rate": 1200, "accumulated_time": 0, "original_fixed_time": 0, "overtime_time": 0},
            "PS4 - 3": {"status": "Available", "mode": None, "end_time": None, "start_time": None, "players": 1, "hourly_rate": 1200, "accumulated_time": 0, "original_fixed_time": 0, "overtime_time": 0},
        }

    def save_data():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(devices, f, ensure_ascii=False, indent=4)

    def save_history(device_name, time_played, total_price, mode, players, is_closed=False):
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except:
                    history = []
        
        history.append({
            "device": device_name,
            "players": players,
            "time_played": time_played,
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

    def toggle_drawer(e):
        page.drawer.open = not page.drawer.open
        page.update()

    def show_devices_view(e=None):
        page.drawer.open = False
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
                    ft.Text("Developed by", size=12, color=ft.Colors.GREY_500),
                    ft.Text("Rashed Hammoda", size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.LINK, color=ft.Colors.BLUE_400, size=20),
                            ft.Text("LinkedIn", color=ft.Colors.BLUE_400, size=16, weight=ft.FontWeight.BOLD)
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                        url="https://www.linkedin.com/in/rashed-hamoda-01b068436/",
                        tooltip="My LinkedIn Profile"
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                alignment=ft.Alignment.CENTER
            )
        ])
        update_ui()
        page.update()

    def show_pricing_view(e):
        page.drawer.open = False
        
        txt_p1 = ft.TextField(label="Price for 1 Player (12 Secs)", value=str(settings["price_1"]), keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)
        txt_p2 = ft.TextField(label="Price for 2 Players (12 Secs)", value=str(settings["price_2"]), keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)
        txt_p3 = ft.TextField(label="Price for 3 Players (12 Secs)", value=str(settings["price_3"]), keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)
        txt_p4 = ft.TextField(label="Price for 4 Players (12 Secs)", value=str(settings["price_4"]), keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)

        def save_prices(e):
            try:
                settings["price_1"] = int(txt_p1.value)
                settings["price_2"] = int(txt_p2.value)
                settings["price_3"] = int(txt_p3.value)
                settings["price_4"] = int(txt_p4.value)
                save_settings(settings)
                snack = ft.SnackBar(ft.Text("Prices saved successfully!"), bgcolor=ft.Colors.GREEN_700)
                page.overlay.append(snack)
                snack.open = True
                page.update()
            except:
                snack = ft.SnackBar(ft.Text("Please enter valid numbers!"), bgcolor=ft.Colors.RED_700)
                page.overlay.append(snack)
                snack.open = True
                page.update()

        current_page.controls.clear()
        current_page.controls.extend([
            ft.Text("Set Price per 12 Seconds", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
            ft.Divider(height=20, color="transparent"),
            txt_p1, txt_p2, txt_p3, txt_p4,
            ft.Divider(height=20, color="transparent"),
            ft.Button("SAVE PRICES", width=300, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=save_prices),
            ft.TextButton("BACK TO DEVICES", on_click=show_devices_view, style=ft.ButtonStyle(color=ft.Colors.GREY_400))
        ])
        page.update()

    def show_reports_view(e):
        page.drawer.open = False
        
        history_data = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    history_data = json.load(f)
                except:
                    history_data = []

        closed_sessions = [s for s in history_data if s.get("is_closed", False)]

        if not closed_sessions:
            current_page.controls.clear()
            current_page.controls.extend([
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=show_devices_view, icon_color=ft.Colors.WHITE),
                    ft.Text("REPORTS", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=20, color="transparent"),
                ft.Text("No closed reports yet.", size=24, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
            ])
            page.update()
            return

        daily_data = {}
        for session in closed_sessions:
            date = session.get("date", "Unknown")
            if date not in daily_data:
                daily_data[date] = {"sessions": [], "total_revenue": 0, "total_seconds": 0}
            
            daily_data[date]["sessions"].append(session)
            daily_data[date]["total_revenue"] += session.get("total_price", 0)
            
            time_str = session.get("time_played", "0 mins 0 secs")
            try:
                parts = time_str.split(" ")
                mins = int(parts[0])
                secs = int(parts[2])
                daily_data[date]["total_seconds"] += (mins * 60) + secs
            except:
                pass

        day_cards = []
        for date, info in sorted(daily_data.items(), reverse=True):
            total_mins, total_secs = divmod(info["total_seconds"], 60)
            total_hours, total_mins = divmod(total_mins, 60)
            time_str = f"{total_hours}h {total_mins}m {total_secs}s"
            
            def show_daily_popup(e, day_date=date, day_sessions=info["sessions"]):
                rows = []
                for s in reversed(day_sessions):
                    rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(s.get("device", ""), color=ft.Colors.WHITE)),
                                ft.DataCell(ft.Text(s.get("time_played", ""), color=ft.Colors.WHITE)),
                                ft.DataCell(ft.Text(str(s.get("players", 1)), color=ft.Colors.WHITE)),
                                ft.DataCell(ft.Text(format_price(s.get("total_price", 0)) + " SYP", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD)),
                            ]
                        )
                    )
                
                table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Device", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Time", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Players", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Price", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD)),
                    ],
                    rows=rows,
                    border=ft.Border.all(1, ft.Colors.GREY_800),
                    border_radius=10,
                    vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_800),
                    horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_800),
                )
                
                dialog = ft.AlertDialog(
                    title=ft.Text(f"Report: {day_date}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD),
                    bgcolor="#1E1E1E",
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([table], alignment=ft.MainAxisAlignment.CENTER)
                        ], scroll=ft.ScrollMode.ADAPTIVE),
                        width=480,
                        height=400,
                    ),
                    actions=[ft.TextButton("CLOSE", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.RED_400))],
                )
                page.show_dialog(dialog)
                
                page.update()

            card = ft.Container(
                content=ft.Column([
                    ft.Text(date, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Divider(height=10, color=ft.Colors.GREY_800),
                    ft.Row([
                        ft.Text(f"Revenue: {format_price(info['total_revenue'])} SYP", color=ft.Colors.GREEN_400, size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Time: {time_str}", color=ft.Colors.BLUE_300, size=14, weight=ft.FontWeight.BOLD),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]),
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
                ft.Text("REPORTS", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=20, color="transparent"),
            ft.Column(day_cards, spacing=10)
        ])
        page.update()

    def show_current_history_view(e):
        page.drawer.open = False
        
        history_data = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    history_data = json.load(f)
                except:
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
                title=ft.Text("End Day?", color=ft.Colors.RED_400, weight=ft.FontWeight.BOLD),
                content=ft.Text("This will move all current sessions to Reports. Are you sure?", color=ft.Colors.WHITE),
                bgcolor="#1E1E1E",
                inset_padding=ft.Padding.all(50),
                actions=[
                    ft.TextButton("CANCEL", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.GREY_400)),
                    ft.TextButton("YES, END DAY", on_click=do_end_day, style=ft.ButtonStyle(color=ft.Colors.RED_400)),
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            page.show_dialog(dialog_confirm)
            dialog_confirm.open = True
            page.update()

        rows = []
        for s in reversed(open_sessions):
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(s.get("device", ""), color=ft.Colors.WHITE)),
                        ft.DataCell(ft.Text(s.get("time_played", ""), color=ft.Colors.WHITE)),
                        ft.DataCell(ft.Text(str(s.get("players", 1)), color=ft.Colors.WHITE)),
                        ft.DataCell(ft.Text(format_price(s.get("total_price", 0)) + " SYP", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD)),
                    ]
                )
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Device", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Time", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Players", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Price", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD)),
            ],
            rows=rows,
            border=ft.Border.all(1, ft.Colors.GREY_800),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_800),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_800),
        )

        current_page.controls.clear()
        current_page.controls.extend([
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=show_devices_view, icon_color=ft.Colors.WHITE),
                ft.Text("CURRENT HISTORY", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300),
                ft.Container(expand=True),
                ft.Button("END DAY", bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, on_click=confirm_end_day),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
            ft.Divider(height=20, color="transparent"),
            # هون عرضنا الجدول مباشرة
            table if open_sessions else ft.Text("No current sessions yet.", size=24, color=ft.Colors.GREY_400, text_align=ft.TextAlign.CENTER),
        ])
        page.update()

    def handle_drawer_change(e):
        selected_index = e.control.selected_index
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
        controls=[
            ft.Container(height=20),
            ft.NavigationDrawerDestination(icon=ft.Icons.HOME, label="Devices"),
            ft.NavigationDrawerDestination(icon=ft.Icons.ATTACH_MONEY, label="Pricing"),
            ft.NavigationDrawerDestination(icon=ft.Icons.HISTORY, label="Current History"),
            ft.NavigationDrawerDestination(icon=ft.Icons.BAR_CHART, label="Reports"),
        ],
    )

    page.appbar = ft.AppBar(
        title=ft.Text("PLAYSTATION ARENA", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD),
        bgcolor="#121212",
        center_title=True,
        leading=ft.IconButton(icon=ft.Icons.MENU, on_click=toggle_drawer, icon_color=ft.Colors.WHITE),
    )

    def close_dialog(e):
        page.pop_dialog()
        page.update()

    def close_alert(e):
        page.pop_dialog()
        page.update()

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
            data["accumulated_time"] = 0
            
            notified_devices.discard(device_name) 
            save_data()
            page.pop_dialog()
            update_ui()
            refresh_alerts_table()

        dialog = ft.AlertDialog(
            title=ft.Text(f"Let Them Play?", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            content=ft.Text(f"Switch {device_name} to Open Time?", color=ft.Colors.WHITE),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            actions=[
                ft.TextButton("CANCEL", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.GREY_400)),
                ft.TextButton("YES", on_click=do_let_play, style=ft.ButtonStyle(color=ft.Colors.GREEN_400)),
            ],
            actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        page.show_dialog(dialog)
        
        page.update()

    def open_extend_popup(device_name):
        time_input = ft.TextField(label="Add Seconds", keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)
        
        def set_time(secs):
            time_input.value = str(secs)
            page.update()

        def add_custom_time(e):
            try:
                secs = int(time_input.value)
                if secs <= 0: raise ValueError
                
                devices[device_name]["accumulated_time"] = devices[device_name].get("accumulated_time", 0) + (time.time() - devices[device_name]["start_time"])
                
                devices[device_name]["mode"] = "fixed"
                devices[device_name]["start_time"] = time.time()
                devices[device_name]["end_time"] = time.time() + secs
                
                notified_devices.discard(device_name) 
                save_data()
                page.pop_dialog()
                update_ui()
                refresh_alerts_table() 
                
            except:
                snack = ft.SnackBar(ft.Text("Please enter valid seconds!"), bgcolor=ft.Colors.RED_700)
                page.overlay.append(snack)
                snack.open = True
                page.update()

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
            title=ft.Text(f"EXTEND TIME - {device_name}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                time_input,
                ft.Text("Quick Select:", size=14, color=ft.Colors.GREY_400),
                ft.Row([
                    ft.Button("3s", on_click=lambda _: set_time(3)),
                    ft.Button("6s", on_click=lambda _: set_time(6)),
                    ft.Button("12s", on_click=lambda _: set_time(12)),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=10, color="transparent"),
                ft.Button("ADD TIME", on_click=add_custom_time, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE),
                ft.Button("SWITCH TO OPEN TIME", on_click=switch_to_open_time, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("CANCEL", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog)
        
        page.update()

    def end_session(device_name):
        data = devices[device_name]
        
        # حساب الوقت الفعلي اللي لعبه
        if data["mode"] == "fixed":
            actual_seconds = time.time() - data["start_time"]
            # إذا لعب أكتر من الوقت المحدد، نحسب الوقت الإضافي
            if time.time() > data["end_time"]:
                actual_seconds = data["end_time"] - data["start_time"]
                overtime_seconds = time.time() - data["end_time"]
            else:
                overtime_seconds = 0
        elif data["mode"] == "open":
            actual_seconds = time.time() - data["start_time"]
            overtime_seconds = 0

        # التقريب لأقرب 3 ثواني
        rounded_actual = int(round(actual_seconds / 3.0) * 3)
        if rounded_actual == 0 and actual_seconds > 0: rounded_actual = 3
        
        rounded_overtime = int(round(overtime_seconds / 3.0) * 3)
        if rounded_overtime == 0 and overtime_seconds > 0: rounded_overtime = 3

        rate = data.get("hourly_rate", 1200)
        total_price = int((rounded_actual / 12.0) * rate) + int((rounded_overtime / 12.0) * rate)
        total_seconds = rounded_actual + rounded_overtime

        # بناء الفاتورة
        content_list = [
            ft.Text(f"Device: {device_name}", size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10, color=ft.Colors.GREY_800),
            ft.Text(f"Time Played: {rounded_actual} secs ({format_price(int((rounded_actual / 12.0) * rate))} SYP)", size=14, color=ft.Colors.GREY_400),
        ]
        
        if rounded_overtime > 0:
            content_list.append(ft.Text(f"Overtime: {rounded_overtime} secs ({format_price(int((rounded_overtime / 12.0) * rate))} SYP)", size=14, color=ft.Colors.YELLOW_500))
            
        content_list.extend([
            ft.Divider(height=10, color=ft.Colors.GREY_800),
            ft.Text(f"Total Time: {total_seconds} secs", size=16, color=ft.Colors.WHITE),
            ft.Text(f"Final Price: {format_price(total_price)} SYP", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_300)
        ])

        receipt = ft.AlertDialog(
            title=ft.Text(f"RECEIPT - {device_name}", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column(content_list, horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
            actions=[ft.TextButton("Close & Free Device", on_click=lambda e: reset_device_and_save(device_name, total_seconds, total_price, data["mode"], data.get("players", 1)), style=ft.ButtonStyle(color=ft.Colors.GREEN_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        page.dialog = receipt
        receipt.open = True
        page.update()

    def reset_device_and_save(device_name, played_seconds, total_price, mode, players):
        mins, secs = divmod(int(played_seconds), 60)
        actual_time_played = f"{mins} mins {secs} secs"
        save_history(device_name, actual_time_played, total_price, mode, players, is_closed=False)
        
        devices[device_name] = {"status": "Available", "mode": None, "end_time": None, "start_time": None, "players": 1, "hourly_rate": 1200, "accumulated_time": 0, "original_fixed_time": 0, "overtime_time": 0}
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
                            content=ft.Row([
                                ft.Text(f"{dev_name} OVERTIME!", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
                                ft.Text(f"Time Ended", size=14, color=ft.Colors.GREY_400),
                                ft.Row([
                                    ft.Button("LET THEM PLAY", bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=lambda e, d=dev_name: confirm_let_play(d)),
                                    ft.Button("END", bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, on_click=lambda e, d=dev_name: end_session(d))
                                ], spacing=10)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            bgcolor="#2A0000",
                            padding=15,
                            border_radius=10,
                            border=ft.Border.all(1, ft.Colors.RED_500)
                        )
                    )
        if len(alerts_container.controls) == 0:
            alerts_container.controls.append(ft.Text("No active alerts", color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER))
        page.update()

    def update_timers():
        while True:
            needs_update = False
            for dev_name, data in devices.items():
                if data["status"] == "Busy":
                    if data["mode"] == "fixed":
                        remaining = int(data["end_time"] - time.time())
                        if remaining <= 0:
                            overtime_seconds = int(time.time() - data["end_time"])
                            mins, secs = divmod(overtime_seconds, 60)
                            device_timer_text[dev_name].value = f"+{mins:02d}:{secs:02d}"
                            device_timer_text[dev_name].color = ft.Colors.YELLOW_500
                        else:
                            mins, secs = divmod(remaining, 60)
                            device_timer_text[dev_name].value = f"{mins:02d}:{secs:02d}"
                            device_timer_text[dev_name].color = ft.Colors.WHITE
                        needs_update = True
                    elif data["mode"] == "open":
                        elapsed = int(time.time() - data["start_time"])
                        mins, secs = divmod(elapsed, 60)
                        device_timer_text[dev_name].value = f"{mins:02d}:{secs:02d}"
                        needs_update = True
            if needs_update:
                try:
                    page.update()
                    refresh_alerts_table() 
                except:
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
                except:
                    pass
            time.sleep(0.5) 

    def start_session(device_name, seconds=None, is_open=False, players=1, rate=1200):
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
                
                if is_time_up:
                    card.bgcolor = "#3E2700" 
                    card.content.controls[1].value = f"● OVERTIME! ({devices[dev_name].get('players', 1)} Players)"
                    card.content.controls[1].color = ft.Colors.YELLOW_500
                else:
                    card.bgcolor = "#2A0000" 
                    card.border = ft.Border.all(2, ft.Colors.RED_500) 
                    card.shadow = ft.BoxShadow(blur_radius=15, color=ft.Colors.RED_500, offset=ft.Offset(0, 0)) 
                    card.content.controls[1].value = f"● IN USE ({devices[dev_name].get('players', 1)} Players)"
                    card.content.controls[1].color = ft.Colors.RED_400
                
                device_timer_text[dev_name].visible = True
                
                if devices[dev_name]["mode"] == "fixed" or devices[dev_name]["mode"] == "open":
                    card.content.controls[3].visible = False
                    card.content.controls[4].visible = True
                
                if devices[dev_name]["mode"] == "open":
                    elapsed = int(time.time() - devices[dev_name]["start_time"])
                    mins, secs = divmod(elapsed, 60)
                    device_timer_text[dev_name].value = f"{mins:02d}:{secs:02d}"
                    device_timer_text[dev_name].color = ft.Colors.WHITE
                elif devices[dev_name]["mode"] == "fixed":
                    remaining = int(devices[dev_name]["end_time"] - time.time())
                    if remaining > 0:
                        mins, secs = divmod(remaining, 60)
                        device_timer_text[dev_name].value = f"{mins:02d}:{secs:02d}"
                    else:
                        overtime_seconds = int(time.time() - devices[dev_name]["end_time"])
                        mins, secs = divmod(overtime_seconds, 60)
                        device_timer_text[dev_name].value = f"+{mins:02d}:{secs:02d}"
                        device_timer_text[dev_name].color = ft.Colors.YELLOW_500
            else:
                card.bgcolor = "#1E1E1E" 
                card.border = ft.Border.all(1, ft.Colors.GREY_700) 
                card.shadow = ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_54, offset=ft.Offset(0, 4)) 
                card.content.controls[1].value = "● AVAILABLE"
                card.content.controls[1].color = ft.Colors.GREEN_400
                device_timer_text[dev_name].value = ""
                device_timer_text[dev_name].visible = False
                card.content.controls[3].visible = False
                card.content.controls[4].visible = False
        page.update()

    def open_time_popup(e):
        device_name = e.control.data
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
            title=ft.Text(f"START SESSION - {device_name}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                ft.Text("Select Start Method:", size=18, color=ft.Colors.WHITE),
                ft.Button("START BY TIME", width=200, bgcolor="#333333", color=ft.Colors.WHITE, on_click=go_to_time_selection),
                ft.Button("START BY CASH", width=200, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, on_click=go_to_cash_selection),
                ft.Button("OPEN TIME", width=200, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=go_to_open_time)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("CANCEL", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog_main)
        dialog_main.open = True
        page.update()

    def open_custom_time_popup(device_name):
        time_input = ft.TextField(label="Seconds", keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)
        players_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("1", "1 Player"),
                ft.dropdown.Option("2", "2 Players"),
                ft.dropdown.Option("3", "3 Players"),
                ft.dropdown.Option("4", "4 Players"),
            ],
            value="1",
            width=200,
            color=ft.Colors.WHITE,
            border_color=ft.Colors.BLUE_300,
            label="Select Players",
        )

        def start_custom(e):
            try:
                secs = int(time_input.value)
                p = int(players_dropdown.value)
                rate = settings.get(f"price_{p}", 1200)
                if secs <= 0: raise ValueError
                start_session(device_name, seconds=secs, players=p, rate=rate)
            except:
                snack = ft.SnackBar(ft.Text("Please enter valid seconds!"), bgcolor=ft.Colors.RED_700)
                page.overlay.append(snack)
                snack.open = True
                page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"CUSTOM TIME - {device_name}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                time_input,
                ft.Text("Quick Select:", size=14, color=ft.Colors.GREY_400),
                ft.Row([
                    ft.Button("3s", on_click=lambda e: setattr(time_input, 'value', "3")),
                    ft.Button("6s", on_click=lambda e: setattr(time_input, 'value', "6")),
                    ft.Button("12s", on_click=lambda e: setattr(time_input, 'value', "12")),
                ], alignment=ft.MainAxisAlignment.CENTER),
                players_dropdown,
                ft.Button("START", on_click=start_custom, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("BACK", on_click=lambda e: open_time_popup(e), style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog)
        
        page.update()

    def open_cash_popup(device_name):
        amount_input = ft.TextField(label="Amount (SYP)", keyboard_type=ft.KeyboardType.NUMBER, color=ft.Colors.WHITE)
        players_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("1", "1 Player"),
                ft.dropdown.Option("2", "2 Players"),
                ft.dropdown.Option("3", "3 Players"),
                ft.dropdown.Option("4", "4 Players"),
            ],
            value="1",
            width=200,
            color=ft.Colors.WHITE,
            border_color=ft.Colors.BLUE_300,
            label="Select Players",
        )

        def calculate_and_start(e):
            try:
                amount = int(amount_input.value)
                p = int(players_dropdown.value)
                rate = settings.get(f"price_{p}", 1200)
                
                calculated_seconds = (amount / rate) * 12
                rounded_seconds = int(round(calculated_seconds / 3.0) * 3)
                
                if rounded_seconds <= 0: raise ValueError
                start_session(device_name, seconds=rounded_seconds, players=p, rate=rate)
            except:
                snack = ft.SnackBar(ft.Text("Please enter a valid amount!"), bgcolor=ft.Colors.RED_700)
                page.overlay.append(snack)
                snack.open = True
                page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(f"START BY CASH - {device_name}", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                amount_input,
                players_dropdown,
                ft.Button("CALCULATE & START", on_click=calculate_and_start, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("BACK", on_click=lambda e: open_time_popup(e), style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog)
        
        page.update()

    def open_open_time_popup(device_name):
        players_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("1", "1 Player"),
                ft.dropdown.Option("2", "2 Players"),
                ft.dropdown.Option("3", "3 Players"),
                ft.dropdown.Option("4", "4 Players"),
            ],
            value="1",
            width=200,
            color=ft.Colors.WHITE,
            border_color=ft.Colors.BLUE_300,
            label="Select Players",
        )

        def start_open(e):
            p = int(players_dropdown.value)
            rate = settings.get(f"price_{p}", 1200)
            start_session(device_name, is_open=True, players=p, rate=rate)

        dialog = ft.AlertDialog(
            title=ft.Text(f"OPEN TIME - {device_name}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                players_dropdown,
                ft.Button("START", on_click=start_open, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("BACK", on_click=lambda e: open_time_popup(e), style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog)
        
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
            title=ft.Text(f"START SESSION - {device_name}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                ft.Text("Select Start Method:", size=18, color=ft.Colors.WHITE),
                ft.Button("START BY TIME", width=200, bgcolor="#333333", color=ft.Colors.WHITE, on_click=go_to_time_selection),
                ft.Button("START BY CASH", width=200, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, on_click=go_to_cash_selection),
                ft.Button("OPEN TIME", width=200, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=go_to_open_time)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("CANCEL", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog_main)
        dialog_main.open = True
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
            title=ft.Text(f"START SESSION - {device_name}", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            bgcolor="#1E1E1E",
            inset_padding=ft.Padding.all(50),
            content=ft.Column([
                ft.Text("Select Start Method:", size=18, color=ft.Colors.WHITE),
                ft.Button("START BY TIME", width=200, bgcolor="#333333", color=ft.Colors.WHITE, on_click=go_to_time_selection),
                ft.Button("START BY CASH", width=200, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, on_click=go_to_cash_selection),
                ft.Button("OPEN TIME", width=200, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=go_to_open_time)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, tight=True),
            actions=[ft.TextButton("CANCEL", on_click=close_dialog, style=ft.ButtonStyle(color=ft.Colors.RED_400))],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        page.show_dialog(dialog_main)
        dialog_main.open = True
        page.update()

    def create_device_card(device_name):
        timer_text = ft.Text("", size=22, weight=ft.FontWeight.BOLD, visible=False, font_family="monospace")
        device_timer_text[device_name] = timer_text

        extend_btn = ft.Button("EXTEND TIME", bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, visible=False, on_click=lambda e: open_extend_popup(device_name))
        end_btn = ft.Button("END SESSION", bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, visible=False, on_click=lambda e: end_session(device_name))

        card_content = ft.Container(
            content=ft.Column([
                ft.Text(device_name, size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("● AVAILABLE", color=ft.Colors.GREEN_400, size=16, weight=ft.FontWeight.BOLD),
                timer_text,
                extend_btn, 
                end_btn     
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            width=320, height=280, 
            bgcolor="#1E1E1E",
            border_radius=20,
            alignment=ft.Alignment.CENTER,
            padding=20,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            on_click=lambda e: open_time_popup_from_card(device_name)
        )
        
        device_ui[device_name] = card_content
        return card_content

    page.add(current_page)
    
    show_devices_view()
    threading.Thread(target=update_timers, daemon=True).start()
    threading.Thread(target=blink_alerts, daemon=True).start()

ft.run(main)
