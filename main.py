import sqlite3
import datetime
import customtkinter as ctk
from tkinter import messagebox

def create_database():
    conn = sqlite3.connect("nots.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            konu TEXT,
            icerik TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_notlar():
    conn = sqlite3.connect("nots.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notlar ORDER BY id DESC")
    result = cursor.fetchall()
    conn.close()
    return result

def insert_not(konu, icerik):
    conn = sqlite3.connect("nots.db")
    cursor = conn.cursor()
    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO notlar (tarih, konu, icerik) VALUES (?, ?, ?)", (tarih, konu, icerik))
    conn.commit()
    conn.close()

def delete_not(not_id):
    conn = sqlite3.connect("nots.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notlar WHERE id=?", (not_id,))
    conn.commit()
    conn.close()

def update_not(not_id, konu, icerik):
    conn = sqlite3.connect("nots.db")
    cursor = conn.cursor()
    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("UPDATE notlar SET konu=?, icerik=?, tarih=? WHERE id=?", (konu, icerik, tarih, not_id))
    conn.commit()
    conn.close()

def search_not(keyword):
    conn = sqlite3.connect("nots.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notlar WHERE konu LIKE ? OR icerik LIKE ?", (f"%{keyword}%", f"%{keyword}%"))
    result = cursor.fetchall()
    conn.close()
    return result

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

class NotDefteriApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kişisel Not Defteri")
        self.root.geometry("700x500")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        title = ctk.CTkLabel(root, text="Kişisel Not Defteri", font=("Arial", 20, "bold"))
        title.pack(pady=12)

        search_frame = ctk.CTkFrame(root, corner_radius=10)
        search_frame.pack(pady=10, padx=20, fill="x")

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Arama yap...", width=400)
        self.search_entry.pack(side="left", padx=(10, 0), pady=10)
        self.search_entry.bind("<Return>", self.not_ara_event)

        search_button = ctk.CTkButton(search_frame, text="Ara", command=self.not_ara)
        search_button.pack(side="left", padx=10, pady=10)

        refresh_button = ctk.CTkButton(search_frame, text="Yenile", command=self.listele)
        refresh_button.pack(side="left", padx=10, pady=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(root, corner_radius=10)
        self.scrollable_frame.pack(pady=10, padx=20, fill="both", expand=True)

        btn_frame = ctk.CTkFrame(root)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Not Ekle", command=self.not_ekle_pencere).grid(row=0, column=0, padx=8)

        self.listele()

    def listele(self, notlar=None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if notlar is None:
            notlar = get_notlar()

        if not notlar:
            ctk.CTkLabel(self.scrollable_frame, text="Henüz hiç not yok.", font=("Arial", 14)).pack(pady=20)
            return

        for n in notlar:
            not_id, tarih, konu, icerik = n
            saat = tarih.split(" ")[1]

            frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=10)
            frame.pack(fill="x", pady=5, padx=10)
            frame.update()

            min_height = 150
            content_height = 30 + len(icerik.split('\n')) * 20
            final_height = max(min_height, content_height)
            frame.configure(height=final_height)

            konu_label = ctk.CTkLabel(frame, text=f"{konu}", font=("Arial", 14, "bold"),
                                      wraplength=550, anchor="w")
            konu_label.pack(fill="x", pady=(10, 5), padx=10)

            icerik_label = ctk.CTkLabel(frame, text=f"{icerik}", font=("Arial", 12),
                                        wraplength=550, justify="left", anchor="w")
            icerik_label.pack(fill="x", padx=10, pady=(0, 10))

            saat_label = ctk.CTkLabel(frame, text=f"Saat: {saat}", font=("Arial", 10), text_color="grey")
            saat_label.pack(anchor="e", padx=10, pady=(0, 5))

            btns = ctk.CTkFrame(frame, fg_color="transparent")
            btns.pack(anchor="e", pady=3, padx=10)
            ctk.CTkButton(btns, text="Düzenle", width=80,
                          command=lambda i=not_id, k=konu, ic=icerik: self.not_duzenle_pencere(i, k, ic)).pack(
                side="left", padx=5)
            ctk.CTkButton(btns, text="Sil", width=80, fg_color="red", hover_color="darkred",
                          command=lambda i=not_id: self.not_sil(i)).pack(side="left", padx=5)

    def not_ekle_pencere(self):
        self.ekle_window = ctk.CTkToplevel(self.root)
        self.ekle_window.title("Yeni Not Ekle")
        center_window(self.ekle_window, 400, 400)
        self.ekle_window.transient(self.root)

        konu_label = ctk.CTkLabel(self.ekle_window, text="Konu:", font=("Arial", 14))
        konu_label.pack(pady=5, padx=10)
        self.konu_entry = ctk.CTkEntry(self.ekle_window, width=350, placeholder_text="Notunuzun konusunu girin")
        self.konu_entry.pack(pady=5, padx=10)

        icerik_label = ctk.CTkLabel(self.ekle_window, text="İçerik:", font=("Arial", 14))
        icerik_label.pack(pady=5, padx=10)
        self.icerik_textbox = ctk.CTkTextbox(self.ekle_window, width=350, height=200)
        self.icerik_textbox.pack(pady=5, padx=10)

        ekle_button = ctk.CTkButton(self.ekle_window, text="Notu Kaydet", command=self.not_ekle)
        ekle_button.pack(pady=10)

    def not_ekle(self):
        konu = self.konu_entry.get().strip()
        icerik = self.icerik_textbox.get("1.0", "end-1c").strip()
        if not konu or not icerik:
            messagebox.showwarning("Uyarı", "Konu ve içerik boş bırakılamaz.")
            return

        insert_not(konu, icerik)
        self.ekle_window.destroy()
        self.listele()
        messagebox.showinfo("Başarılı", "Not eklendi.")

    def not_sil(self, not_id):
        if messagebox.askyesno("Notu Sil", "Bu notu silmek istediğinizden emin misiniz?"):
            delete_not(not_id)
            self.listele()
            messagebox.showinfo("Silindi", "Not silindi.")

    def not_duzenle_pencere(self, not_id, konu, icerik):
        self.duzenle_window = ctk.CTkToplevel(self.root)
        self.duzenle_window.title("Notu Düzenle")
        center_window(self.duzenle_window, 400, 400)
        self.duzenle_window.transient(self.root)

        konu_label = ctk.CTkLabel(self.duzenle_window, text="Yeni Konu:", font=("Arial", 14))
        konu_label.pack(pady=5, padx=10)
        self.yeni_konu_entry = ctk.CTkEntry(self.duzenle_window, width=350)
        self.yeni_konu_entry.insert(0, konu)
        self.yeni_konu_entry.pack(pady=5, padx=10)

        icerik_label = ctk.CTkLabel(self.duzenle_window, text="Yeni İçerik:", font=("Arial", 14))
        icerik_label.pack(pady=5, padx=10)
        self.yeni_icerik_textbox = ctk.CTkTextbox(self.duzenle_window, width=350, height=200)
        self.yeni_icerik_textbox.insert("1.0", icerik)
        self.yeni_icerik_textbox.pack(pady=5, padx=10)

        kaydet_button = ctk.CTkButton(self.duzenle_window, text="Değişiklikleri Kaydet",
                                      command=lambda: self.not_duzenle(not_id))
        kaydet_button.pack(pady=10)

    def not_duzenle(self, not_id):
        yeni_konu = self.yeni_konu_entry.get().strip()
        yeni_icerik = self.yeni_icerik_textbox.get("1.0", "end-1c").strip()
        if yeni_konu and yeni_icerik:
            update_not(not_id, yeni_konu, yeni_icerik)
            self.duzenle_window.destroy()
            self.listele()
            messagebox.showinfo("Başarılı", "Not güncellendi.")
        else:
            messagebox.showwarning("Uyarı", "Konu ve içerik boş bırakılamaz.")

    def not_ara(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.listele()
            return
        results = search_not(keyword)
        self.listele(results)

    def not_ara_event(self, event):
        self.not_ara()

if __name__ == "__main__":
    create_database()
    root = ctk.CTk()
    center_window(root, 700, 500)
    app = NotDefteriApp(root)
    root.mainloop()