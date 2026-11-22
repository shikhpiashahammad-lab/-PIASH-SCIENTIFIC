from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
from kivy.core.window import Window
import sqlite3, os
from datetime import date, timedelta

Window.clearcolor = (0.025, 0.035, 0.075, 1)

KV = r"""
#:import dp kivy.metrics.dp
<DarkLabel@Label>:
    color: .94,.95,1,1
    halign: "left"
    valign: "middle"
    text_size: self.size
<DarkButton@Button>:
    background_normal: ""
    background_color: .34,.16,.78,1
    color: 1,1,1,1
    bold: True
ScreenManager:
    Home:
    Add:
    History:
<Home>:
    name: "home"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: .025,.035,.075,1
            Rectangle:
                pos: self.pos
                size: self.size
        DarkLabel:
            text: "[b]PIASH[/b]\n[color=0.62,0.66,0.78,1]Personal Finance Manager[/color]"
            markup: True
            size_hint_y: None
            height: dp(65)
            font_size: "23sp"
        DarkLabel:
            text: app.tr("dashboard")
            size_hint_y: None
            height: dp(30)
            font_size: "18sp"
        BoxLayout:
            orientation: "vertical"
            padding: dp(14)
            spacing: dp(5)
            canvas.before:
                Color:
                    rgba: .075,.085,.16,1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(16)]
            DarkLabel:
                text: app.tr("month")
            DarkLabel:
                id: month_total
                text: "৳ 0"
                color: .15,.88,.48,1
                font_size: "30sp"
                bold: True
        GridLayout:
            cols: 2
            size_hint_y: None
            height: dp(85)
            spacing: dp(8)
            BoxLayout:
                orientation: "vertical"
                padding: dp(10)
                canvas.before:
                    Color:
                        rgba: .075,.085,.16,1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(14)]
                DarkLabel:
                    text: app.tr("today")
                DarkLabel:
                    id: today_total
                    text: "৳ 0"
                    font_size: "19sp"
                    bold: True
            BoxLayout:
                orientation: "vertical"
                padding: dp(10)
                canvas.before:
                    Color:
                        rgba: .075,.085,.16,1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(14)]
                DarkLabel:
                    text: app.tr("week")
                DarkLabel:
                    id: week_total
                    text: "৳ 0"
                    font_size: "19sp"
                    bold: True
        DarkButton:
            text: app.tr("add")
            size_hint_y: None
            height: dp(48)
            on_release: app.root.current = "add"
        DarkButton:
            text: app.tr("history")
            size_hint_y: None
            height: dp(48)
            on_release: app.root.current = "history"
        DarkButton:
            text: app.tr("language")
            size_hint_y: None
            height: dp(42)
            on_release: app.toggle_language()
        DarkLabel:
            id: status
            text: ""
            size_hint_y: None
            height: dp(28)
            color: .15,.88,.48,1
<Add>:
    name: "add"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(10)
        DarkLabel:
            text: app.tr("add_title")
            size_hint_y: None
            height: dp(42)
            font_size: "20sp"
        TextInput:
            id: amount
            hint_text: app.tr("amount")
            input_filter: "float"
            multiline: False
            size_hint_y: None
            height: dp(48)
        Spinner:
            id: category
            text: app.tr("food")
            values: app.categories()
            size_hint_y: None
            height: dp(48)
        TextInput:
            id: note
            hint_text: app.tr("note")
            multiline: False
            size_hint_y: None
            height: dp(48)
        DarkButton:
            text: app.tr("save")
            size_hint_y: None
            height: dp(48)
            on_release: app.save_expense(amount.text, category.text, note.text)
        DarkButton:
            text: app.tr("back")
            size_hint_y: None
            height: dp(44)
            on_release: app.root.current = "home"
        DarkLabel:
            id: message
            text: ""
<History>:
    name: "history"
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(8)
        DarkLabel:
            text: app.tr("history")
            size_hint_y: None
            height: dp(42)
            font_size: "20sp"
        ScrollView:
            GridLayout:
                id: rows
                cols: 1
                spacing: dp(6)
                size_hint_y: None
                height: self.minimum_height
        DarkButton:
            text: app.tr("back")
            size_hint_y: None
            height: dp(44)
            on_release: app.root.current = "home"
"""

class Home(Screen): pass
class Add(Screen): pass
class History(Screen): pass

class ExpenseTracker(App):
    lang = StringProperty("en")
    words = {
      "en":{"dashboard":"Expense Overview","month":"This Month's Expense","today":"Today's Expense","week":"This Week","add":"＋ Add Expense","history":"Transaction History","language":"বাংলা / English","add_title":"Add New Expense","amount":"Amount (BDT)","note":"Note (optional)","save":"SAVE EXPENSE","back":"BACK","food":"Food","transport":"Transport","shopping":"Shopping","education":"Education","others":"Others","saved":"Saved successfully"},
      "bn":{"dashboard":"খরচের সারাংশ","month":"এই মাসের মোট খরচ","today":"আজকের খরচ","week":"এই সপ্তাহের খরচ","add":"＋ খরচ যোগ করুন","history":"খরচের ইতিহাস","language":"বাংলা / English","add_title":"নতুন খরচ যোগ করুন","amount":"টাকার পরিমাণ (৳)","note":"বিবরণ (ঐচ্ছিক)","save":"খরচ সংরক্ষণ করুন","back":"ফিরে যান","food":"খাবার","transport":"যাতায়াত","shopping":"কেনাকাটা","education":"পড়াশোনা","others":"অন্যান্য","saved":"সফলভাবে সংরক্ষিত হয়েছে"}
    }
    def tr(self, key):
        return self.words[self.lang].get(key, key)
    def categories(self):
        return [self.tr(x) for x in ("food","transport","shopping","education","others")]
    def build(self):
        self.title = "Expense Tracker"
        self.db = os.path.join(self.user_data_dir, "expenses.db")
        con = sqlite3.connect(self.db)
        con.execute("CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY, amount REAL, category TEXT, note TEXT, spent_on TEXT)")
        con.commit(); con.close()
        root = Builder.load_string(KV)
        self.root = root
        self.refresh()
        return root
    def toggle_language(self):
        self.lang = "bn" if self.lang == "en" else "en"
        self.root.current = "home"
        self.refresh()
    def save_expense(self, amount, category, note):
        try:
            value = float(amount)
            if value <= 0: raise ValueError()
            con = sqlite3.connect(self.db)
            con.execute("INSERT INTO expenses(amount,category,note,spent_on) VALUES(?,?,?,?)",
                        (value, category, note, date.today().isoformat()))
            con.commit(); con.close()
            self.root.get_screen("add").ids.message.text = self.tr("saved")
            self.root.get_screen("add").ids.amount.text = ""
            self.root.get_screen("add").ids.note.text = ""
            self.refresh()
        except Exception:
            self.root.get_screen("add").ids.message.text = "Enter a valid amount / সঠিক পরিমাণ লিখুন"
    def total(self, start, end):
        con = sqlite3.connect(self.db)
        value = con.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE spent_on BETWEEN ? AND ?",
                            (start.isoformat(), end.isoformat())).fetchone()[0]
        con.close()
        return value
    def refresh(self):
        if not self.root: return
        today = date.today()
        home = self.root.get_screen("home")
        home.ids.month_total.text = "৳ {:,.0f}".format(self.total(today.replace(day=1), today))
        home.ids.today_total.text = "৳ {:,.0f}".format(self.total(today, today))
        home.ids.week_total.text = "৳ {:,.0f}".format(self.total(today-timedelta(days=today.weekday()), today))
        hist = self.root.get_screen("history").ids.rows
        hist.clear_widgets()
        from kivy.uix.label import Label
        con = sqlite3.connect(self.db)
        rows = con.execute("SELECT category,amount,spent_on,note FROM expenses ORDER BY id DESC LIMIT 100").fetchall()
        con.close()
        for cat, amount, day, note in rows:
            hist.add_widget(Label(text=f"{day}  |  {cat}  |  ৳{amount:,.0f}  {note or ''}",
                                  size_hint_y=None, height=dp(38), color=(.94,.95,1,1)))
if __name__ == "__main__":
    ExpenseTracker().run()
