import customtkinter as ctk
import tkinter.messagebox as messagebox
import pandas as pd
import os
from datetime import datetime

class AkunView(ctk.CTkFrame):
    def __init__(self, master, user, data_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.user = user
        self.data_manager = data_manager
        
        # Data user saat ini
        self.current_username = user.username
        self.current_role = user.role
        
        # Ambil data lengkap dari users.csv
        self.user_data = self._get_user_data()
        
        self.render()
    
    def _get_user_data(self):
        """Ambil data user dari CSV"""
        try:
            df = pd.read_csv(self.data_manager.users_file)
            user_row = df[df['username'] == self.current_username]
            if not user_row.empty:
                return user_row.iloc[0].to_dict()
        except:
            pass
        return {
            'username': self.current_username,
            'role': self.current_role,
            'perusahaan': 'MAINTORA',
            'email': 'admin@maintora.com',
            'telp': '+62 812-3456-7890',
            'alamat': 'Kantor Pusat MAINTORA',
            'pic': 'Admin MAINTORA'
        }
    
    def render(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        # ========== HEADER ==========
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(header, text="INFORMASI AKUN", font=("Inter", 24, "bold"), 
                    text_color="#1E3A5F").pack(anchor="w")
        
        # ========== MAIN CONTENT ==========
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        
        # ========== KOTAKAN UTAMA (FULL WIDTH) ==========
        # Diubah ke pack(fill="both") agar memenuhi seluruh lebar halaman
        profil_card = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=10)
        profil_card.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Avatar (Sedikit diperbesar agar seimbang dengan font 14)
        avatar_frame = ctk.CTkFrame(profil_card, fg_color="#1E3A5F", corner_radius=60, width=100, height=100)
        avatar_frame.pack(pady=(30, 15))
        avatar_frame.pack_propagate(False)
        
        nama_pt = self.user_data.get('perusahaan', 'MAINTORA')
        if nama_pt == '-':
            nama_pt = 'MAINTORA'
        
        initial = nama_pt[0].upper()
        
        ctk.CTkLabel(avatar_frame, text=initial, font=("Inter", 40, "bold"), 
                    text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        
        # Nama Utama di bawah Avatar
        ctk.CTkLabel(profil_card, text=self.user_data.get('perusahaan', 'Admin MAINTORA'), 
                    font=("Inter", 22, "bold"), text_color="#1E3A5F").pack()
        ctk.CTkLabel(profil_card, text=self.user_data.get('role', 'Admin').capitalize(), 
                    font=("Inter", 13), text_color="#7F8C8D").pack(pady=(0, 10))
        
        # Garis pemisah
        separator = ctk.CTkFrame(profil_card, fg_color="#E0E0E0", height=1)
        separator.pack(fill="x", padx=40, pady=(15, 20))
        
        # Informasi Profil (Grid Internal)
        info_frame = ctk.CTkFrame(profil_card, fg_color="transparent")
        info_frame.pack(fill="x", padx=40, pady=(0, 30))
        info_frame.grid_columnconfigure(1, weight=1)
        
        info_items = [
            ("🏢 Nama Perusahaan", self.user_data.get('perusahaan', '-')),
            ("📞 Telepon", self.user_data.get('telp', '-')),
            ("📧 Email", self.user_data.get('email', '-')),
            ("📍 Alamat", self.user_data.get('alamat', '-')),
            ("👤 Person in Charge", self.user_data.get('pic', '-'))
        ]
        
        for idx, (label, value) in enumerate(info_items):
            # Label Kiri
            lbl = ctk.CTkLabel(info_frame, text=label, font=("Inter", 14, "bold"), 
                               width=200, text_color="#7F8C8D", anchor="w")
            lbl.grid(row=idx, column=0, sticky="w", pady=12)
            
            # Nilai Kanan (PERBAIKAN: wraplength dihapus agar teks dipaksa 1 baris lurus)
            val = ctk.CTkLabel(info_frame, text=value, font=("Inter", 14), 
                               text_color="#2C3E50", anchor="w")
            val.grid(row=idx, column=1, sticky="w", pady=12, padx=(20, 0))