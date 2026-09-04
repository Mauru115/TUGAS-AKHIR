import customtkinter as ctk
import tkinter.messagebox as messagebox
import webbrowser
from models import DataManager
import os

from view_dashboard import DashboardView
from view_mesin import MesinView
from view_riwayat_servis import RiwayatServisView
from view_visualisasi import VisualisasiView
from view_prediksi import PrediksiView
from view_laporan import LaporanView
from view_notifikasi import NotifikasiView
from view_akun import AkunView

ctk.set_appearance_mode("Light")
ctk.set_widget_scaling(0.85)  # Memperkecil semua widget
ctk.set_window_scaling(0.85)   # Memperkecil window

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MAINTORA - Sistem Informasi Pemeliharaan Mesin")
        self.geometry("1400x900")
        self.minsize(1280, 768)     # Minimum size
        
        # Proteksi OS: Jika di Mac/Linux gagal 'zoomed', aplikasi tidak akan crash
        try:
            self.state('zoomed')
        except Exception:
            self.geometry("1280x800")
            
        self.configure(fg_color="#F0F2F5") 
        
        self.data_manager = DataManager()
        self.current_user = None
        self.sidebar_visible = True
        self.nav_buttons = {}

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.show_auth_screen()

    def clear_container(self, container):
        for widget in container.winfo_children():
            widget.destroy()

    # ==========================================
    # 1. LAYAR LOGIN & FORGET PASSWORD
    # ==========================================
    def show_auth_screen(self):
        self.clear_container(self.main_container)
        
        bg_frame = ctk.CTkFrame(self.main_container, fg_color="#1E3A5F")
        bg_frame.pack(fill="both", expand=True)
        
        login_card = ctk.CTkFrame(bg_frame, fg_color="white", width=480, height=520, corner_radius=16)
        login_card.place(relx=0.5, rely=0.5, anchor="center")
        login_card.pack_propagate(False)

        title_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        title_frame.pack(pady=(50, 10))
        
        icon_frame = ctk.CTkFrame(title_frame, fg_color="#1E3A5F", width=60, height=60, corner_radius=12)
        icon_frame.pack(pady=(0, 15))
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="⚙️", font=("Inter", 28)).place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(title_frame, text="MAINTORA", font=("Inter", 28, "bold"), 
                    text_color="#1E3A5F").pack()
        ctk.CTkLabel(title_frame, text="Sistem Informasi Pemeliharaan Mesin", 
                    font=("Inter", 12), text_color="#7F8C8D").pack(pady=(2, 0))

        form_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        form_frame.pack(pady=20, padx=45, fill="both", expand=True)
        
        ctk.CTkLabel(form_frame, text="Username", font=("Inter", 12, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        self.ent_user = ctk.CTkEntry(form_frame, placeholder_text="Masukkan username", 
                                      height=42, corner_radius=8, border_color="#E0E0E0",
                                      border_width=1)
        self.ent_user.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Password", font=("Inter", 12, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        self.ent_pass = ctk.CTkEntry(form_frame, placeholder_text="Masukkan password", 
                                      show="*", height=42, corner_radius=8, border_color="#E0E0E0",
                                      border_width=1)
        self.ent_pass.pack(fill="x", pady=(0, 5))
        self.ent_pass.bind("<Return>", lambda e: self.do_login())

        fp_label = ctk.CTkLabel(form_frame, text="Lupa password?", text_color="#3498DB", 
                                font=("Inter", 11), cursor="hand2")
        fp_label.pack(anchor="e", pady=(5, 20))
        fp_label.bind("<Button-1>", lambda e: self.show_forget_password_screen())

        ctk.CTkButton(form_frame, text="MASUK", command=self.do_login, 
                      fg_color="#1E3A5F", hover_color="#2C5282", 
                      height=42, corner_radius=8, font=("Inter", 14, "bold")).pack(fill="x")

    def show_forget_password_screen(self):
        self.clear_container(self.main_container)
        
        bg_frame = ctk.CTkFrame(self.main_container, fg_color="#1E3A5F")
        bg_frame.pack(fill="both", expand=True)
        
        card = ctk.CTkFrame(bg_frame, fg_color="white", width=450, height=380, corner_radius=16)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="Lupa Password", font=("Inter", 22, "bold"), 
                    text_color="#1E3A5F").pack(pady=(40, 20))
        
        info_text = "Silakan hubungi admin untuk mereset password Anda.\n\nHubungi: 0822-2744-3334"
        ctk.CTkLabel(card, text=info_text, font=("Inter", 12), 
                    text_color="#7F8C8D", justify="center").pack(pady=20)
        
        ctk.CTkButton(card, text="Hubungi Admin via WhatsApp", 
                      command=lambda: webbrowser.open("https://wa.me/6282227443334"),
                      fg_color="#25D366", hover_color="#20B859", 
                      height=40, corner_radius=8).pack(pady=10, padx=40, fill="x")
        
        ctk.CTkButton(card, text="← Kembali ke Login", command=self.show_auth_screen,
                      fg_color="transparent", text_color="#3498DB", 
                      hover_color="#EBF5FB", height=40).pack(pady=5, padx=40, fill="x")

    def do_login(self):
        user = self.data_manager.login(self.ent_user.get(), self.ent_pass.get())
        if user:
            self.current_user = user
            self.show_main_layout()
        else:
            messagebox.showerror("Error", "Login gagal! Periksa username dan password Anda.")

    # ==========================================
    # 2. LAYAR UTAMA (SIDEBAR, HEADER, KONTEN)
    # ==========================================
    def show_main_layout(self):
        self.clear_container(self.main_container)
        self.nav_buttons.clear()
        
        # --- SIDEBAR (KIRI) ---
        self.sidebar = ctk.CTkFrame(self.main_container, width=240, corner_radius=0, fg_color="#1A2234")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        ctk.CTkLabel(self.sidebar, text="MAINTORA", font=("Inter", 20, "bold"), text_color="white", anchor="w").pack(pady=(20, 0), padx=20, fill="x")
        ctk.CTkLabel(self.sidebar, text="Sistem Informasi Pemeliharaan Mesin", font=("Inter", 11), text_color="#FFFFFF", anchor="w").pack(pady=(0, 30), padx=20, fill="x")
        
        # Definisi Navigasi
        self.navs = [
            ("🏠  Dashboard", "Dashboard", "Ringkasan kondisi mesin dan aktivitas pemeliharaan", DashboardView),
            ("⚙️  Data Mesin", "Data Mesin", "Kelola data seluruh mesin", MesinView),
            ("🔄  Riwayat Servis", "Riwayat Servis", "Kelola data riwayat servis", RiwayatServisView),
            ("📊  Visualisasi", "Visualisasi", "Pemantauan visual tren dan kondisi mesin", VisualisasiView),
            ("✨  Prediksi Anomali", "Prediksi Anomali", "Estimasi jadwal pemeliharaan berikutnya", PrediksiView),
            ("📄  Laporan", "Laporan", "Unduh data rekapitulasi mesin", LaporanView),
            ("🔔  Notifikasi", "Notifikasi", "Pusat informasi sistem", NotifikasiView),
            ("👤  Akun", "Akun", "Pusat informasi pelanggan", AkunView)
        ]
        
        for menu_text, title_text, sub_text, view_class in self.navs:
            btn = ctk.CTkButton(
                self.sidebar, text=menu_text, anchor="w", font=("Inter", 14),
                fg_color="transparent", text_color="#FFFFFF", hover_color="#042740", corner_radius=20, height=40,
                command=lambda mt=menu_text, tt=title_text, st=sub_text, vc=view_class: self.load_view(mt, tt, st, vc)
            )
            btn.pack(pady=5, padx=15, fill="x")
            self.nav_buttons[menu_text] = btn
            
        ctk.CTkButton(self.sidebar, text="🚪  Logout", command=self.show_auth_screen, fg_color="transparent", text_color="#CBD5E1", hover_color="#E63946", anchor="w").pack(pady=30, padx=20, fill="x", side="bottom")

        # --- KONTAINER KANAN ---
        self.right_container = ctk.CTkFrame(self.main_container, fg_color="#F4F6F9", corner_radius=0)
        self.right_container.pack(side="right", fill="both", expand=True)

        # 2A. HEADER DINAMIS (Atas Kanan)
        self.header_frame = ctk.CTkFrame(self.right_container, fg_color="white", corner_radius=0, height=70)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)

        header_left = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_left.pack(side="left", fill="y", padx=15, pady=10)

        # Hamburger Button ☰
        ctk.CTkButton(header_left, text="☰", font=("Inter", 24), width=40, fg_color="transparent", text_color="black", hover_color="#F0F0F0", command=self.toggle_sidebar).pack(side="left")
        
        # Area Teks Judul bersusun ke bawah
        title_area = ctk.CTkFrame(header_left, fg_color="transparent")
        title_area.pack(side="left", padx=10, fill="y")
        self.lbl_title = ctk.CTkLabel(title_area, text="Dashboard", font=("Inter", 22, "bold"), text_color="black", anchor="w")
        self.lbl_title.pack(fill="x")
        self.lbl_subtitle = ctk.CTkLabel(title_area, text="Ringkasan kondisi", font=("Inter", 12), text_color="gray", anchor="w")
        self.lbl_subtitle.pack(fill="x", pady=(0, 2))

        # 2B. AREA KONTEN (Tengah Kanan)
        self.content_frame = ctk.CTkScrollableFrame(self.right_container, fg_color="#F4F6F9", corner_radius=0)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 2C. FOOTER WATERMARK (Bawah Kanan)
        footer = ctk.CTkFrame(self.right_container, fg_color="white", corner_radius=0, height=50)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkLabel(footer, text="Copyright © Kelompok 2 | Tugas Akhir Praktik Pemrograman Komputer", font=("Inter", 12), text_color="black").pack(side="left", padx=20, pady=10)

        # Muat halaman pertama secara default
        first_menu, first_title, first_sub, first_class = self.navs[0]
        self.load_view(first_menu, first_title, first_sub, first_class)

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False
        else:
            self.sidebar.pack(side="left", fill="y", before=self.right_container)
            self.sidebar_visible = True

    def load_view(self, menu_text, title_text, sub_text, view_class):
        # 1. Update Highlight Tombol Aktif
        for text, btn in self.nav_buttons.items():
            if text == menu_text:
                btn.configure(fg_color="#599DEB", text_color="white") # Biru aktif
            else:
                btn.configure(fg_color="transparent", text_color="#CBD5E1") # Reset warna
                
        # 2. Update Teks Header (Susun bawah)
        self.lbl_title.configure(text=title_text)
        self.lbl_subtitle.configure(text=sub_text)

        # 3. Muat Konten Halaman
        self.clear_container(self.content_frame)
        if view_class:
            view_instance = view_class(master=self.content_frame, user=self.current_user, data_manager=self.data_manager)
            view_instance.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            ctk.CTkLabel(self.content_frame, text=f"Halaman {title_text} Sedang Dalam Pengembangan 🚧", font=("Inter", 16, "bold"), text_color="gray").pack(pady=50)

if __name__ == "__main__":
    app = App()
    app.mainloop()