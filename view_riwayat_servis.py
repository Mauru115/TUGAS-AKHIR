import customtkinter as ctk
import tkinter.messagebox as messagebox
from datetime import datetime
import pandas as pd

class RiwayatServisView(ctk.CTkFrame):
    def __init__(self, master, user, data_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.user = user
        self.data_manager = data_manager
        self.current_page = 0
        self.rows_per_page = 10
        
        # ========== HEADER ==========
        header_area = ctk.CTkFrame(self, fg_color="transparent")
        header_area.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(header_area, text="Riwayat Servis", font=("Inter", 20, "bold"), 
                    text_color="#1E3A5F").pack(side="left")
        ctk.CTkLabel(header_area, text="Kelola data riwayat servis mesin", font=("Inter", 11), 
                    text_color="#7F8C8D").pack(side="left", padx=(10, 0))
        
        # Tombol Tambah (hanya admin)
        if hasattr(self.user, 'can_crud') and self.user.can_crud:
            ctk.CTkButton(header_area, text="+ Tambah Riwayat", command=self.show_add_form,
                         fg_color="#27AE60", hover_color="#229954", height=34,
                         corner_radius=8, font=("Inter", 12, "bold")).pack(side="right")
        
        # ========== FILTER BAR ==========
        filter_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        filter_frame.pack(fill="x", pady=(0, 12))
        
        filter_inner = ctk.CTkFrame(filter_frame, fg_color="transparent")
        filter_inner.pack(padx=15, pady=10, fill="x")
        
        ctk.CTkLabel(filter_inner, text="Filter:", font=("Inter", 12, "bold"), 
                    text_color="#2C3E50").pack(side="left", padx=(0, 10))
        
        self.filter_kode = ctk.CTkEntry(filter_inner, placeholder_text="Kode Mesin", 
                                        width=130, height=32, corner_radius=6)
        self.filter_kode.pack(side="left", padx=(0, 10))
        
        self.filter_teknisi = ctk.CTkEntry(filter_inner, placeholder_text="Teknisi", 
                                           width=130, height=32, corner_radius=6)
        self.filter_teknisi.pack(side="left", padx=(0, 10))
        
        self.filter_tanggal = ctk.CTkEntry(filter_inner, placeholder_text="Tanggal (YYYY-MM-DD)", 
                                           width=150, height=32, corner_radius=6)
        self.filter_tanggal.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(filter_inner, text="🔍 Cari", command=self.load_table_data,
                     fg_color="#3498DB", width=80, height=32, corner_radius=6).pack(side="left", padx=(0, 5))
        ctk.CTkButton(filter_inner, text="⟳ Reset", command=self.reset_filter,
                     fg_color="#95A5A6", width=80, height=32, corner_radius=6).pack(side="left")
        
        # ========== TABLE CONTAINER ==========
        self.table_card = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        
        # ========== PAGINATION ==========
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=(10, 0))
        
        self.load_table_data()
    
    def reset_filter(self):
        self.filter_kode.delete(0, 'end')
        self.filter_teknisi.delete(0, 'end')
        self.filter_tanggal.delete(0, 'end')
        self.current_page = 0
        self.load_table_data()
    
    def load_table_data(self):
        for widget in self.table_card.winfo_children():
            widget.destroy()
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()
        
        df_servis = self.data_manager.get_data_servis(user=self.user)
        df_mesin = self.data_manager.get_data_mesin(user=self.user)
        
        if df_servis.empty:
            empty_frame = ctk.CTkFrame(self.table_card, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both")
            ctk.CTkLabel(empty_frame, text="📋 Belum ada data riwayat servis", 
                        font=("Inter", 16), text_color="#95A5A6").pack(pady=50)
            if hasattr(self.user, 'can_crud') and self.user.can_crud:
                ctk.CTkLabel(empty_frame, text="Klik tombol '+ Tambah Riwayat' untuk menambahkan", 
                            font=("Inter", 12), text_color="#BDC3C7").pack()
            return
        
        # Apply filters
        filtered_df = df_servis.copy()
        
        kode_filter = self.filter_kode.get().strip().upper()
        teknisi_filter = self.filter_teknisi.get().strip()
        tanggal_filter = self.filter_tanggal.get().strip()
        
        if kode_filter:
            filtered_df = filtered_df[filtered_df['kode_mesin'].astype(str).str.upper().str.contains(kode_filter, na=False)]
        if teknisi_filter:
            filtered_df = filtered_df[filtered_df['teknisi'].astype(str).str.contains(teknisi_filter, na=False)]
        if tanggal_filter:
            filtered_df = filtered_df[filtered_df['tanggal_perbaikan'].astype(str).str.contains(tanggal_filter, na=False)]
        
        # Pagination
        total_rows = len(filtered_df)
        total_pages = max(1, (total_rows + self.rows_per_page - 1) // self.rows_per_page)
        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)
        
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, total_rows)
        page_df = filtered_df.iloc[start_idx:end_idx]
        
        # Table dengan scroll
        table_frame = ctk.CTkScrollableFrame(self.table_card, fg_color="transparent", height=450)
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header tabel
        headers = ["No", "Kode", "Nama Mesin", "Tanggal", "Jenis Kerusakan", "Teknisi", "Biaya", "Suhu", "Catatan", "Aksi"]
        col_widths = [40, 65, 160, 95, 140, 90, 100, 55, 120, 85]
        
        header_frame = ctk.CTkFrame(table_frame, fg_color="#F0F2F5", corner_radius=6, height=35)
        header_frame.pack(fill="x", pady=(0, 8))
        header_frame.pack_propagate(False)
        
        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill="both", expand=True, padx=10)
        
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(header_inner, text=header, width=width, font=("Inter", 10, "bold"), 
                        text_color="#2C3E50", anchor="w").pack(side="left")
        
        # Data rows
        for i, (idx, row) in enumerate(page_df.iterrows()):
            kode = str(row.get('kode_mesin', '-'))
            nama_mesin = self._get_machine_name(df_mesin, kode)
            tanggal = str(row.get('tanggal_perbaikan', '-'))[:10]
            kerusakan = str(row.get('jenis_kerusakan', '-'))[:22]
            teknisi = str(row.get('teknisi', '-'))[:10]
            
            # Biaya
            try:
                biaya = float(row.get('biaya', 0)) if row.get('biaya') else 0
                biaya_text = f"Rp {biaya:,.0f}" if biaya > 0 else "-"
            except:
                biaya_text = "-"
            
            # Suhu
            suhu = str(row.get('suhu_mesin', '-'))
            if suhu == 'nan' or suhu == '':
                suhu = '-'
            elif suhu.replace('.', '').isdigit():
                suhu = f"{float(suhu):.1f}°C"
            
            # Catatan
            catatan = str(row.get('catatan', '-'))
            if catatan == 'nan' or catatan == '':
                catatan = '-'
            elif len(catatan) > 15:
                catatan = catatan[:12] + "..."
            
            bg = "#FAFBFC" if i % 2 == 0 else "white"
            
            row_frame = ctk.CTkFrame(table_frame, fg_color=bg, corner_radius=0, height=34)
            row_frame.pack(fill="x", pady=1)
            row_frame.pack_propagate(False)
            
            row_inner = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_inner.pack(fill="both", expand=True, padx=10)
            
            # No urut
            ctk.CTkLabel(row_inner, text=str(start_idx + i + 1), width=col_widths[0], 
                        font=("Inter", 10), text_color="#7F8C8D", anchor="w").pack(side="left")
            
            # Kode
            ctk.CTkLabel(row_inner, text=kode, width=col_widths[1], 
                        font=("Inter", 10, "bold"), text_color="#1E3A5F", anchor="w").pack(side="left")
            
            # Nama Mesin
            ctk.CTkLabel(row_inner, text=nama_mesin[:20], width=col_widths[2], 
                        font=("Inter", 10), text_color="#2C3E50", anchor="w").pack(side="left")
            
            # Tanggal
            ctk.CTkLabel(row_inner, text=tanggal, width=col_widths[3], 
                        font=("Inter", 10), text_color="#7F8C8D", anchor="w").pack(side="left")
            
            # Kerusakan
            ctk.CTkLabel(row_inner, text=kerusakan, width=col_widths[4], 
                        font=("Inter", 10), text_color="#2C3E50", anchor="w").pack(side="left")
            
            # Teknisi
            ctk.CTkLabel(row_inner, text=teknisi, width=col_widths[5], 
                        font=("Inter", 10), text_color="#2C3E50", anchor="w").pack(side="left")
            
            # Biaya
            ctk.CTkLabel(row_inner, text=biaya_text, width=col_widths[6], 
                        font=("Inter", 10), text_color="#27AE60" if biaya_text != "-" else "#95A5A6", anchor="w").pack(side="left")
            
            # Suhu
            ctk.CTkLabel(row_inner, text=suhu, width=col_widths[7], 
                        font=("Inter", 10), text_color="#3498DB", anchor="w").pack(side="left")
            
            # Catatan
            ctk.CTkLabel(row_inner, text=catatan, width=col_widths[8], 
                        font=("Inter", 9), text_color="#7F8C8D", anchor="w").pack(side="left")
            
            # Aksi buttons
            act_frame = ctk.CTkFrame(row_inner, fg_color="transparent")
            act_frame.pack(side="left")
            
            ctk.CTkButton(act_frame, text="👁️", width=28, height=26, corner_radius=5,
                         fg_color="#EBF5FB", text_color="#3498DB",
                         command=lambda r=row: self._show_detail(r)).pack(side="left", padx=1)
            
            if hasattr(self.user, 'can_crud') and self.user.can_crud:
                ctk.CTkButton(act_frame, text="✏️", width=28, height=26, corner_radius=5,
                             fg_color="#FEF9E7", text_color="#F39C12",
                             command=lambda r=row, i=idx: self._show_edit_form(r, i)).pack(side="left", padx=1)
                ctk.CTkButton(act_frame, text="🗑️", width=28, height=26, corner_radius=5,
                             fg_color="#FDEDEC", text_color="#E74C3C",
                             command=lambda i=idx: self._delete_riwayat(i)).pack(side="left", padx=1)
        
        # Pagination
        if total_pages > 1:
            pag_inner = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
            pag_inner.pack(fill="x")
            
            ctk.CTkLabel(pag_inner, text=f"Menampilkan {start_idx + 1} - {end_idx} dari {total_rows} data", 
                        font=("Inter", 11), text_color="#7F8C8D").pack(side="left", padx=10)
            
            nav_frame = ctk.CTkFrame(pag_inner, fg_color="transparent")
            nav_frame.pack(side="right")
            
            ctk.CTkButton(nav_frame, text="◀ Prev", width=80, height=30, corner_radius=6,
                         fg_color="#1E3A5F" if self.current_page > 0 else "#CBD5E1",
                         state="normal" if self.current_page > 0 else "disabled",
                         command=self._prev_page).pack(side="left", padx=5)
            
            ctk.CTkLabel(nav_frame, text=f"{self.current_page + 1} / {total_pages}", 
                        font=("Inter", 12, "bold"), text_color="#2C3E50").pack(side="left", padx=15)
            
            ctk.CTkButton(nav_frame, text="Next ▶", width=80, height=30, corner_radius=6,
                         fg_color="#1E3A5F" if self.current_page < total_pages - 1 else "#CBD5E1",
                         state="normal" if self.current_page < total_pages - 1 else "disabled",
                         command=self._next_page).pack(side="left", padx=5)
    
    def _get_machine_name(self, df_mesin, kode_mesin):
        if df_mesin.empty:
            return kode_mesin
        result = df_mesin[df_mesin['kode_mesin'].astype(str) == str(kode_mesin)]
        if not result.empty:
            return result.iloc[0]['nama_mesin']
        return kode_mesin
    
    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_table_data()
    
    def _next_page(self):
        self.current_page += 1
        self.load_table_data()
    
    def show_add_form(self):
        """Form tambah riwayat servis"""
        form = ctk.CTkToplevel(self)
        form.title("Tambah Riwayat Servis")
        form.geometry("600x700")
        form.grab_set()
        form.configure(fg_color="#F0F2F5")
        form.resizable(True, True)
        form.minsize(550, 650)
        
        main_frame = ctk.CTkFrame(form, fg_color="white", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="Form Tambah Riwayat Servis", 
                    font=("Inter", 20, "bold"), text_color="#1E3A5F").pack(pady=(20, 10))
        ctk.CTkLabel(main_frame, text="Lengkapi data di bawah ini", 
                    font=("Inter", 11), text_color="#7F8C8D").pack(pady=(0, 20))
        
        # Scrollable form
        fields_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent", height=480)
        fields_frame.pack(padx=30, fill="both", expand=True)
        
        # Get machine list
        df_mesin = self.data_manager.get_data_mesin(user=self.user)
        mesin_options = [f"{row['kode_mesin']} - {row['nama_mesin']}" 
                         for _, row in df_mesin.iterrows()] if not df_mesin.empty else []
        
        # Kode Mesin
        ctk.CTkLabel(fields_frame, text="Kode Mesin *", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(10, 5))
        self.kode_mesin_combo = ctk.CTkComboBox(fields_frame, values=mesin_options, height=40, corner_radius=8)
        self.kode_mesin_combo.pack(fill="x", pady=(0, 15))
        
        # Tanggal Perbaikan
        ctk.CTkLabel(fields_frame, text="Tanggal Perbaikan *", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        self.tanggal_entry = ctk.CTkEntry(fields_frame, placeholder_text="YYYY-MM-DD", 
                                          height=40, corner_radius=8)
        self.tanggal_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.tanggal_entry.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(fields_frame, text="Format: 2025-06-01", font=("Inter", 10), 
                    text_color="#95A5A6").pack(anchor="w", pady=(0, 15))
        
        # Jenis Kerusakan
        ctk.CTkLabel(fields_frame, text="Jenis Kerusakan *", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        self.jenis_kerusakan_entry = ctk.CTkEntry(fields_frame, 
            placeholder_text="Contoh: Overheat, Error Sensor, Bearing Rusak", 
            height=40, corner_radius=8)
        self.jenis_kerusakan_entry.pack(fill="x", pady=(0, 15))
        
        # Teknisi
        ctk.CTkLabel(fields_frame, text="Teknisi *", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        self.teknisi_entry = ctk.CTkEntry(fields_frame, placeholder_text="Nama teknisi yang menangani", 
                                          height=40, corner_radius=8)
        self.teknisi_entry.pack(fill="x", pady=(0, 15))
        
        # Biaya
        ctk.CTkLabel(fields_frame, text="Biaya (Rp)", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        self.biaya_entry = ctk.CTkEntry(fields_frame, placeholder_text="Contoh: 2000000 atau 2.000.000", 
                                        height=40, corner_radius=8)
        self.biaya_entry.pack(fill="x", pady=(0, 15))
        
        # Suhu Mesin
        ctk.CTkLabel(fields_frame, text="Suhu Mesin (°C)", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        self.suhu_entry = ctk.CTkEntry(fields_frame, placeholder_text="Contoh: 75.5", 
                                       height=40, corner_radius=8)
        self.suhu_entry.pack(fill="x", pady=(0, 15))
        
        # Catatan
        ctk.CTkLabel(fields_frame, text="Catatan", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        self.catatan_entry = ctk.CTkTextbox(fields_frame, height=100, corner_radius=8, 
                                            border_width=1, border_color="#E0E0E0")
        self.catatan_entry.pack(fill="x", pady=(0, 15))
        
        # Note informasi
        note_frame = ctk.CTkFrame(fields_frame, fg_color="#F8F9FA", corner_radius=8)
        note_frame.pack(fill="x", pady=(5, 10))
        ctk.CTkLabel(note_frame, text="ℹ️ Field bertanda * wajib diisi", 
                    font=("Inter", 10), text_color="#7F8C8D").pack(pady=8)
        
        # Tombol (di luar scroll)
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(10, 20))
        
        ctk.CTkButton(btn_frame, text="Simpan", command=lambda: self._save_riwayat(form),
                     fg_color="#27AE60", hover_color="#229954", height=45, corner_radius=10,
                     font=("Inter", 14, "bold")).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        ctk.CTkButton(btn_frame, text="Batal", command=form.destroy,
                     fg_color="#95A5A6", hover_color="#7F8C8D", height=45, corner_radius=10,
                     font=("Inter", 14, "bold")).pack(side="left", expand=True, fill="x", padx=(10, 0))
    
    def _save_riwayat(self, form_window):
        selected = self.kode_mesin_combo.get()
        if not selected:
            messagebox.showerror("Error", "Pilih kode mesin terlebih dahulu!")
            return
        
        kode_mesin = selected.split(" - ")[0]
        tanggal = self.tanggal_entry.get().strip()
        jenis_kerusakan = self.jenis_kerusakan_entry.get().strip()
        teknisi = self.teknisi_entry.get().strip()
        biaya = self.biaya_entry.get().strip()
        suhu = self.suhu_entry.get().strip()
        catatan = self.catatan_entry.get("1.0", "end").strip()
        
        if not jenis_kerusakan or not teknisi or not tanggal:
            messagebox.showerror("Error", "Lengkapi semua field yang diperlukan (bertanda *)!")
            return
        
        # Validasi tanggal
        try:
            datetime.strptime(tanggal, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Format tanggal salah! Gunakan YYYY-MM-DD")
            return
        
        # Konversi biaya
        try:
            biaya_clean = biaya.replace('.', '').replace(',', '') if biaya else "0"
            biaya_val = float(biaya_clean) if biaya_clean else 0
        except:
            biaya_val = 0
        
        # Baca data existing
        try:
            df = pd.read_csv(self.data_manager.servis_file, dtype=str)
            df = df.fillna('')
        except:
            df = pd.DataFrame(columns=['kode_mesin', 'jenis_kerusakan', 'teknisi', 'biaya', 
                                       'suhu_mesin', 'catatan', 'tanggal_perbaikan', 'tanggal_perbaikan_selanjutnya'])
        
        # Buat data baru
        new_row = pd.DataFrame([{
            'kode_mesin': str(kode_mesin),
            'jenis_kerusakan': str(jenis_kerusakan),
            'teknisi': str(teknisi),
            'biaya': str(biaya_val),
            'suhu_mesin': str(suhu) if suhu else '',
            'catatan': str(catatan),
            'tanggal_perbaikan': str(tanggal),
            'tanggal_perbaikan_selanjutnya': ''
        }])
        
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(self.data_manager.servis_file, index=False)
        
        messagebox.showinfo("Sukses", "Riwayat servis berhasil ditambahkan!")
        
        # Tutup form
        if form_window:
            form_window.destroy()
        
        self.load_table_data()
    
    def _show_edit_form(self, row, index):
        """Form untuk mengedit semua data riwayat servis"""
        form = ctk.CTkToplevel(self)
        form.title("Edit Riwayat Servis")
        form.geometry("600x700")
        form.grab_set()
        form.configure(fg_color="#F0F2F5")
        form.resizable(True, True)
        form.minsize(550, 650)
        
        header = ctk.CTkFrame(form, fg_color="white", corner_radius=0, height=55)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="Edit Riwayat Servis", font=("Inter", 18, "bold"), 
                    text_color="#1E3A5F").pack(side="left", padx=20, pady=15)
        ctk.CTkButton(header, text="✕", width=30, height=30, corner_radius=15,
                     fg_color="#F0F2F5", text_color="#7F8C8D", hover_color="#E0E0E0",
                     command=form.destroy).pack(side="right", padx=20)
        
        main_frame = ctk.CTkFrame(form, fg_color="white", corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent", height=550)
        scroll_frame.pack(fill="both", expand=True)
        
        # Informasi mesin
        info_frame = ctk.CTkFrame(scroll_frame, fg_color="#F8F9FA", corner_radius=8)
        info_frame.pack(fill="x", pady=(0, 15))
        
        kode = str(row.get('kode_mesin', '-'))
        ctk.CTkLabel(info_frame, text=f"Mesin: {kode}", font=("Inter", 14, "bold"), 
                    text_color="#1E3A5F").pack(anchor="w", padx=15, pady=(10, 5))
        
        # 1. Tanggal Perbaikan
        ctk.CTkLabel(scroll_frame, text="Tanggal Perbaikan *", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(10, 5))
        
        tanggal_value = str(row.get('tanggal_perbaikan', ''))
        if tanggal_value == 'nan' or tanggal_value == 'None':
            tanggal_value = datetime.now().strftime("%Y-%m-%d")
        
        self.edit_tanggal_entry = ctk.CTkEntry(scroll_frame, placeholder_text="YYYY-MM-DD", 
                                               height=40, corner_radius=8)
        self.edit_tanggal_entry.insert(0, tanggal_value[:10])
        self.edit_tanggal_entry.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(scroll_frame, text="Format: 2025-06-01", font=("Inter", 10), 
                    text_color="#95A5A6").pack(anchor="w", pady=(0, 15))
        
        # 2. Jenis Kerusakan
        ctk.CTkLabel(scroll_frame, text="Jenis Kerusakan *", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        
        kerusakan_value = str(row.get('jenis_kerusakan', ''))
        if kerusakan_value == 'nan' or kerusakan_value == 'None':
            kerusakan_value = ''
        
        self.edit_kerusakan_entry = ctk.CTkEntry(scroll_frame, 
            placeholder_text="Contoh: Overheat, Error Sensor, Bearing Rusak", 
            height=40, corner_radius=8)
        self.edit_kerusakan_entry.insert(0, kerusakan_value)
        self.edit_kerusakan_entry.pack(fill="x", pady=(0, 15))
        
        # 3. Teknisi
        ctk.CTkLabel(scroll_frame, text="Teknisi *", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        
        teknisi_value = str(row.get('teknisi', ''))
        if teknisi_value == 'nan' or teknisi_value == 'None':
            teknisi_value = ''
        
        self.edit_teknisi_entry = ctk.CTkEntry(scroll_frame, placeholder_text="Nama teknisi", 
                                               height=40, corner_radius=8)
        self.edit_teknisi_entry.insert(0, teknisi_value)
        self.edit_teknisi_entry.pack(fill="x", pady=(0, 15))
        
        # 4. Biaya
        ctk.CTkLabel(scroll_frame, text="Biaya (Rp)", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        
        biaya_value = str(row.get('biaya', ''))
        if biaya_value == 'nan' or biaya_value == 'None':
            biaya_value = ''
        
        self.edit_biaya_entry = ctk.CTkEntry(scroll_frame, placeholder_text="Contoh: 2000000", 
                                             height=40, corner_radius=8)
        self.edit_biaya_entry.insert(0, biaya_value)
        self.edit_biaya_entry.pack(fill="x", pady=(0, 15))
        
        # 5. Suhu Mesin
        ctk.CTkLabel(scroll_frame, text="Suhu Mesin (°C)", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        
        suhu_value = str(row.get('suhu_mesin', ''))
        if suhu_value == 'nan' or suhu_value == 'None':
            suhu_value = ''
        
        self.edit_suhu_entry = ctk.CTkEntry(scroll_frame, placeholder_text="Contoh: 75.5", 
                                            height=40, corner_radius=8)
        self.edit_suhu_entry.insert(0, suhu_value)
        self.edit_suhu_entry.pack(fill="x", pady=(0, 15))
        
        # 6. Catatan
        ctk.CTkLabel(scroll_frame, text="Catatan", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(0, 5))
        
        catatan_value = str(row.get('catatan', ''))
        if catatan_value == 'nan' or catatan_value == 'None':
            catatan_value = ''
        
        self.edit_catatan_entry = ctk.CTkTextbox(scroll_frame, height=100, corner_radius=8, 
                                                 border_width=1, border_color="#E0E0E0")
        self.edit_catatan_entry.insert("1.0", catatan_value)
        self.edit_catatan_entry.pack(fill="x", pady=(0, 15))
        
        # Note
        note_frame = ctk.CTkFrame(scroll_frame, fg_color="#F8F9FA", corner_radius=6)
        note_frame.pack(fill="x", pady=(5, 10))
        ctk.CTkLabel(note_frame, text="ℹ️ Field bertanda * wajib diisi", 
                    font=("Inter", 10), text_color="#7F8C8D").pack(pady=8)
        
        # Tombol
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 0))
        
        ctk.CTkButton(btn_frame, text="Batal", command=form.destroy,
                     fg_color="white", text_color="#7F8C8D", border_width=1, border_color="#E0E0E0",
                     height=40, corner_radius=8, font=("Inter", 13, "bold")).pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        ctk.CTkButton(btn_frame, text="Simpan Perubahan", command=lambda: self._save_edit_riwayat(index, form),
                     fg_color="#27AE60", hover_color="#229954",
                     height=40, corner_radius=8, font=("Inter", 13, "bold")).pack(side="left", fill="x", expand=True, padx=(8, 0))
    
    def _save_edit_riwayat(self, index, form):
        """Menyimpan semua perubahan data riwayat servis"""
        try:
            # Ambil nilai dari form
            tanggal = self.edit_tanggal_entry.get().strip()
            kerusakan = self.edit_kerusakan_entry.get().strip()
            teknisi = self.edit_teknisi_entry.get().strip()
            biaya = self.edit_biaya_entry.get().strip()
            suhu = self.edit_suhu_entry.get().strip()
            catatan = self.edit_catatan_entry.get("1.0", "end").strip()
            
            # Validasi
            if not kerusakan or not teknisi or not tanggal:
                messagebox.showerror("Error", "Lengkapi semua field yang diperlukan (bertanda *)!")
                return
            
            # Validasi format tanggal
            try:
                datetime.strptime(tanggal, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Format tanggal salah! Gunakan YYYY-MM-DD")
                return
            
            # Konversi biaya
            try:
                biaya_clean = biaya.replace('.', '').replace(',', '') if biaya else "0"
                biaya_val = float(biaya_clean) if biaya_clean else 0
            except:
                biaya_val = 0
            
            # Baca file CSV
            df = pd.read_csv(self.data_manager.servis_file, dtype=str)
            df = df.fillna('')
            
            # Update data
            df.loc[index, 'tanggal_perbaikan'] = tanggal
            df.loc[index, 'jenis_kerusakan'] = kerusakan
            df.loc[index, 'teknisi'] = teknisi
            df.loc[index, 'biaya'] = str(biaya_val)
            df.loc[index, 'suhu_mesin'] = suhu if suhu else ''
            df.loc[index, 'catatan'] = catatan if catatan else ''
            
            # Simpan
            df.to_csv(self.data_manager.servis_file, index=False)
            
            messagebox.showinfo("Sukses", "Riwayat servis berhasil diperbarui!")
            form.destroy()
            self.load_table_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan: {e}")
    
    def _show_detail(self, row):
        detail = ctk.CTkToplevel(self)
        detail.title("Detail Riwayat Servis")
        detail.geometry("550x500")
        detail.grab_set()
        detail.configure(fg_color="#F0F2F5")
        
        main_frame = ctk.CTkFrame(detail, fg_color="white", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="📋 Detail Servis", 
                    font=("Inter", 18, "bold"), text_color="#2C3E50").pack(pady=(20, 15))
        
        # Biaya
        try:
            biaya = float(row.get('biaya', 0)) if row.get('biaya') else 0
            biaya_text = f"Rp {biaya:,.0f}" if biaya > 0 else "-"
        except:
            biaya_text = "-"
        
        details = [
            ("Kode Mesin", str(row.get('kode_mesin', '-'))),
            ("Tanggal Perbaikan", str(row.get('tanggal_perbaikan', '-'))),
            ("Jenis Kerusakan", str(row.get('jenis_kerusakan', '-'))),
            ("Teknisi", str(row.get('teknisi', '-'))),
            ("Biaya", biaya_text),
            ("Suhu Mesin", f"{row.get('suhu_mesin', '-')} °C" if row.get('suhu_mesin') else '-'),
            ("Catatan", str(row.get('catatan', '-')) or '-')
        ]
        
        for label, value in details:
            frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=6)
            
            ctk.CTkLabel(frame, text=f"{label}:", font=("Inter", 12, "bold"), 
                        width=130, anchor="w", text_color="#2C3E50").pack(side="left")
            ctk.CTkLabel(frame, text=value, font=("Inter", 12), 
                        text_color="#7F8C8D", anchor="w", wraplength=330).pack(side="left", padx=(10, 0))
        
        ctk.CTkButton(main_frame, text="Tutup", command=detail.destroy,
                     fg_color="#3498DB", width=150, height=35, corner_radius=8).pack(pady=20)
    
    def _delete_riwayat(self, index):
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus riwayat servis ini?"):
            try:
                df = pd.read_csv(self.data_manager.servis_file, dtype=str)
                df = df.drop(index)
                df.to_csv(self.data_manager.servis_file, index=False)
                messagebox.showinfo("Sukses", "Riwayat servis berhasil dihapus!")
                self.load_table_data()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus: {e}")