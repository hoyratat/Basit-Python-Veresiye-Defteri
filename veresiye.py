import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import csv

DB_FILE = "veresiye.db"

# ----------------- VERİTABANI -----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer TEXT,
                    amount REAL,
                    type TEXT,
                    note TEXT,
                    date TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

# ----------------- UYGULAMA -----------------
class VeresiyeApp:
    def __init__(self, master):
        self.master = master
        master.title("Veresiye Defteri")
        master.geometry("1024x768")

        # ----------------- ANA SCROLL -----------------
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # ----------------- TOPLAM BORÇ -----------------
        self.total_label = tk.Label(self.scrollable_frame, text="Toplam Tüm Müşteriler Borcu: 0", font=("Arial", 14, "bold"))
        self.total_label.pack(pady=5)

        # ----------------- ÜSTTE YENİ MÜŞTERİ -----------------
        top_frame = tk.Frame(self.scrollable_frame)
        top_frame.pack(pady=5, anchor="w")
        tk.Button(top_frame, text="Yeni Müşteri", command=self.add_customer).pack(side=tk.LEFT, padx=5)

        # ----------------- MÜŞTERİ SEÇİMİ -----------------
        frame = tk.Frame(self.scrollable_frame)
        frame.pack(pady=10, anchor="w")

        tk.Label(frame, text="Müşteri:").grid(row=0, column=0, sticky="w")
        self.customer_combo = ttk.Combobox(frame, values=self.load_customers(), width=20)
        self.customer_combo.grid(row=0, column=1, sticky="w")
        self.customer_combo.bind("<<ComboboxSelected>>", self.load_selected_customer_transactions)
        self.customer_combo.bind("<Double-1>", self.rename_customer)

        tk.Label(frame, text="Tutar:").grid(row=1, column=0, sticky="w")
        self.amount_entry = tk.Entry(frame, width=15)
        self.amount_entry.grid(row=1, column=1, sticky="w")

        tk.Label(frame, text="Tür:").grid(row=1, column=2, sticky="w")
        self.type_combo = ttk.Combobox(frame, values=["borç","tahsilat"], width=10)
        self.type_combo.grid(row=1, column=3, sticky="w")
        self.type_combo.current(0)

        tk.Label(frame, text="Not:").grid(row=2, column=0, sticky="w")
        self.note_entry = tk.Entry(frame, width=50)
        self.note_entry.grid(row=2, column=1, columnspan=3, sticky="w")

        tk.Button(frame, text="Ekle", command=self.add_transaction).grid(row=3, column=0, columnspan=4, pady=5, sticky="w")

        # ----------------- ÜSTTEKİ BORÇ TABLOSU -----------------
        self.tree = ttk.Treeview(self.scrollable_frame, columns=("Customer","TotalDebt","LastTransaction"), show='headings', height=10)
        self.tree.heading("Customer", text="Müşteri")
        self.tree.heading("TotalDebt", text="Toplam Borç")
        self.tree.heading("LastTransaction", text="Son İşlem Tarihi")
        self.tree.pack(pady=5, fill="x", side="top")

        # ----------------- ALTTAKİ SON İŞLEMLER (TÜM MÜŞTERİLER) -----------------
        self.last_tree = ttk.Treeview(self.scrollable_frame, columns=("Date","Customer","Amount","Type","Note"), show='headings', height=10)
        self.last_tree.heading("Date", text="Tarih")
        self.last_tree.heading("Customer", text="Müşteri")
        self.last_tree.heading("Amount", text="Tutar")
        self.last_tree.heading("Type", text="Tür")
        self.last_tree.heading("Note", text="Not")
        self.last_tree.pack(pady=10, fill="x")

        # ----------------- SEÇİLİ MÜŞTERİNİN SON İŞLEMLERİ -----------------
        self.selected_tree = ttk.Treeview(self.scrollable_frame, columns=("Date","Amount","Type","Note"), show='headings', height=10)
        self.selected_tree.heading("Date", text="Tarih")
        self.selected_tree.heading("Amount", text="Tutar")
        self.selected_tree.heading("Type", text="Tür")
        self.selected_tree.heading("Note", text="Not")
        self.selected_tree.pack(pady=10, fill="x")

        # ----------------- ADMIN BUTONLARI -----------------
        btn_frame = tk.Frame(self.scrollable_frame)
        btn_frame.pack(anchor="w", pady=5)
        tk.Button(btn_frame, text="Seçili İşlemi Sil", command=self.delete_transaction).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="CSV İndir", command=self.export_csv).pack(side=tk.LEFT, padx=5)

        self.load_transactions()

    # ----------------- FONKSİYONLAR -----------------
    def load_customers(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT DISTINCT customer FROM transactions")
        rows = sorted([r[0] for r in c.fetchall()])
        conn.close()
        return rows

    def add_customer(self):
        name = simpledialog.askstring("Yeni Müşteri", "Müşteri adı girin:")
        if name:
            current = list(self.customer_combo['values'])
            if name not in current:
                current.append(name)
                current.sort()
                self.customer_combo['values'] = current
                self.customer_combo.set(name)

    def rename_customer(self, event):
        old_name = self.customer_combo.get()
        if not old_name:
            return
        new_name = simpledialog.askstring("Müşteri Adı Değiştir", f"{old_name} yeni adı:")
        if new_name and new_name != old_name:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("UPDATE transactions SET customer=? WHERE customer=?", (new_name, old_name))
            conn.commit()
            conn.close()
            self.customer_combo['values'] = self.load_customers()
            self.customer_combo.set(new_name)
            self.load_transactions()

    def add_transaction(self):
        customer = self.customer_combo.get()
        if not customer:
            messagebox.showerror("Hata", "Müşteri seçin!")
            return
        try:
            amount = float(self.amount_entry.get())
        except:
            messagebox.showerror("Hata", "Geçerli tutar girin!")
            return
        t_type = self.type_combo.get()
        note = self.note_entry.get()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO transactions (customer, amount, type, note, date) VALUES (?, ?, ?, ?, ?)",
                  (customer, amount, t_type, note, date))
        conn.commit()
        conn.close()
        self.amount_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
        self.load_transactions()

    def load_transactions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in self.last_tree.get_children():
            self.last_tree.delete(row)
        for row in self.selected_tree.get_children():
            self.selected_tree.delete(row)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # Müşteri toplam borçları
        c.execute("""
            SELECT customer,
                   SUM(CASE WHEN type='borç' THEN amount ELSE 0 END) -
                   SUM(CASE WHEN type='tahsilat' THEN amount ELSE 0 END) as total_debt,
                   MAX(date) as last_date
            FROM transactions
            GROUP BY customer
            ORDER BY total_debt DESC
        """)
        rows = c.fetchall()
        for row in rows:
            self.tree.insert("", tk.END, values=(row[0], f"{row[1]:,.0f}", row[2]))

        # Tüm müşterilerin toplam borcu
        total_all = sum(row[1] for row in rows)
        self.total_label.config(text=f"Toplam Tüm Müşteriler Borcu: {total_all:,.0f}")

        # Son işlemler (en yeni 100 işlem)
        c.execute("""
            SELECT date, customer,
                   CASE WHEN type='borç' THEN -amount ELSE amount END as amount,
                   type, note
            FROM transactions
            ORDER BY date DESC
            LIMIT 100
        """)
        last_rows = c.fetchall()
        for row in last_rows:
            self.last_tree.insert("", tk.END, values=(row[0], row[1], f"{row[2]:,.0f}", row[3], row[4]))

        # Seçili müşteri varsa onun işlemleri
        self.load_selected_customer_transactions()
        conn.close()

    def load_selected_customer_transactions(self, event=None):
        customer = self.customer_combo.get()
        if not customer:
            return
        for row in self.selected_tree.get_children():
            self.selected_tree.delete(row)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT date,
                   CASE WHEN type='borç' THEN -amount ELSE amount END as amount,
                   type, note
            FROM transactions
            WHERE customer=?
            ORDER BY date DESC
            LIMIT 20
        """, (customer,))
        rows = c.fetchall()
        conn.close()

        for row in rows:
            self.selected_tree.insert("", tk.END, values=(row[0], f"{row[1]:,.0f}", row[2], row[3]))

    def delete_transaction(self):
        selected = self.last_tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Silinecek işlemi seçin!")
            return
        password = simpledialog.askstring("Şifre Gerekiyor", "Şifreyi girin:", show="*")
        if password != "123456":
            messagebox.showerror("Hata", "Şifre yanlış!")
            return
        confirm = messagebox.askyesno("Silme Onayı", "Seçili işlemleri silmek istediğinizden emin misiniz?")
        if not confirm:
            return
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        for s in selected:
            values = self.last_tree.item(s, "values")
            date, customer, amount, t_type, note = values
            try:
                amount_val = float(amount.replace(",", "").replace("-", ""))
            except:
                amount_val = 0
            c.execute("""DELETE FROM transactions 
                         WHERE customer=? AND date=? AND type=? AND ABS(amount)=?""",
                      (customer, date, t_type, amount_val))
        conn.commit()
        conn.close()
        self.load_transactions()

    def export_csv(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT date, customer,
                   CASE WHEN type='borç' THEN -amount ELSE amount END as amount,
                   type, note
            FROM transactions
            ORDER BY date ASC
        """)
        rows = c.fetchall()
        conn.close()

        filename = "veresiye_defteri.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(["Tarih", "Müşteri", "Tutar", "Tür", "Not"])
            for r in rows:
                writer.writerow([r[0], r[1], f"{r[2]:,.0f}", r[3], r[4]])

        messagebox.showinfo("CSV İndirildi", f"{filename} kaydedildi!")

# ----------------- UYGULAMAYI ÇALIŞTIR -----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = VeresiyeApp(root)
    root.mainloop()
