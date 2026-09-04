import customtkinter as ctk
import tkinter.messagebox as messagebox
import pandas as pd

class MesinView(ctk.CTkFrame):
    def __init__(self, master, user, data_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.user = user
        self.data_manager = data_manager
        self.current_page = 0
        self.rows_per_page = 12
        
        # ========== HEADER ==========
        header_area = ctk.CTkFrame(self, fg_color="transparent")
        header_area.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_area, text="Data Mesin", font=("Inter", 20, "bold"), 
                    text_color="#1E3A5F").pack(side="left")
        ctk.CTkLabel(header_area, text="Kelola data seluruh mesin", font=("Inter", 11), 
                    text_color="#7F8C8D").pack(side="left", padx=(10, 0))
        
        # Tombol Tambah (hanya admin)
        if hasattr(self.user, 'can_crud') and self.user.can_crud:
            ctk.CTkButton(header_area, text="+ Tambah Mesin", command=self.show_add_form,
                         fg_color="#27AE60", hover_color="#229954", height=35,
                         corner_radius=8, font=("Inter", 12, "bold")).pack(side="right")
        
        # ========== SEARCH BAR ==========
        search_card = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        search_card.pack(fill="x", pady=(0, 12))
        
        s_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        s_inner.pack(padx=15, pady=10, fill="x")
        
        ctk.CTkLabel(s_inner, text="Cari:", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50").pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(s_inner, placeholder_text="Kode atau nama mesin...", 
                                         width=250, height=34, corner_radius=8)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_table_data())
        
        ctk.CTkButton(s_inner, text="🔍 Cari", command=self.load_table_data,
                     fg_color="#3498DB", width=80, height=34, corner_radius=8).pack(side="left", padx=(0, 5))
        ctk.CTkButton(s_inner, text="⟳ Reset", command=self.reset_search,
                     fg_color="#95A5A6", width=80, height=34, corner_radius=8).pack(side="left")
        
        # ========== TABLE CONTAINER ==========
        self.table_card = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.table_card.pack(fill="both", expand=True)
        
        # ========== PAGINATION ==========
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", pady=(10, 0))
        
        self.load_table_data()

    def _get_user_perusahaan(self):
        """Mendapatkan nama perusahaan dari user yang login"""
        try:
            df_users = pd.read_csv(self.data_manager.users_file)
            user_row = df_users[df_users['username'] == self.user.username]
            if not user_row.empty:
                return str(user_row.iloc[0].get('perusahaan', '-')).strip()
        except Exception:
            pass
        return "-"
    
    def reset_search(self):
        self.search_entry.delete(0, 'end')
        self.current_page = 0
        self.load_table_data()
    
    def load_table_data(self):
        for widget in self.table_card.winfo_children():
            widget.destroy()
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()
        
        # Ambil data mesin dengan filter user
        df = self.data_manager.get_data_mesin(user=self.user)
        
        if df.empty:
            self._show_empty_state("📦 Belum ada data mesin di dalam sistem")
            return

        # Filter berdasarkan perusahaan untuk pelanggan
        if hasattr(self.user, 'role') and self.user.role == 'pelanggan':
            user_perusahaan = self._get_user_perusahaan()
            if not df.empty and 'perusahaan' in df.columns:
                df = df[df['perusahaan'].astype(str).str.strip().str.lower() == user_perusahaan.lower()]
            
            if df.empty:
                self._show_empty_state(f"📦 Tidak ada data mesin untuk {user_perusahaan}")
                return
        
        # Search filter
        search_text = self.search_entry.get().strip().lower()
        if search_text and not df.empty:
            df = df[df['kode_mesin'].astype(str).str.lower().str.contains(search_text, na=False) |
                    df['nama_mesin'].astype(str).str.lower().str.contains(search_text, na=False) |
                    df['kategori'].astype(str).str.lower().str.contains(search_text, na=False)]
            
            if df.empty:
                self._show_empty_state("🔍 Mesin yang Anda cari tidak ditemukan")
                return
        
        # Table layout
        table_inner = ctk.CTkFrame(self.table_card, fg_color="transparent")
        table_inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        headers = ["Kode", "Nama Mesin", "Kategori", "Lokasi", "Perusahaan", "Status", "Interval", "Aksi"]
        col_widths = [70, 180, 110, 100, 140, 80, 70, 100]
        
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            table_inner.grid_columnconfigure(i, weight=1, minsize=width)
        
        # Header
        for i, header in enumerate(headers):
            ctk.CTkLabel(table_inner, text=header, font=("Inter", 12, "bold"), 
                        text_color="#2C3E50").grid(row=0, column=i, padx=3, pady=10, sticky="w")
        
        # Separator
        line = ctk.CTkFrame(table_inner, fg_color="#E0E0E0", height=1)
        line.grid(row=1, column=0, columnspan=len(headers), sticky="ew", pady=(0, 10))
        
        # Pagination
        total_rows = len(df)
        total_pages = max(1, (total_rows + self.rows_per_page - 1) // self.rows_per_page)
        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)
        
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, total_rows)
        page_df = df.iloc[start_idx:end_idx]
        
        # Data rows
        row_num = 2
        for i, (_, row) in enumerate(page_df.iterrows()):
            kode = str(row.get('kode_mesin', '-'))
            nama = str(row.get('nama_mesin', '-'))[:25]
            kategori = str(row.get('kategori', '-'))[:15]
            lokasi = str(row.get('lokasi', '-'))[:15]
            perusahaan = str(row.get('perusahaan', '-'))[:18]
            status = str(row.get('status', '-'))
            interval = str(row.get('interval_servis_hari', '-'))
            
            status_color = "#27AE60" if status.lower() == 'aktif' else "#E74C3C" if status.lower() == 'rusak' else "#F39C12"
            
            ctk.CTkLabel(table_inner, text=kode, font=("Inter", 11), 
                        text_color="#2C3E50").grid(row=row_num, column=0, padx=3, pady=6, sticky="w")
            ctk.CTkLabel(table_inner, text=nama, font=("Inter", 11), 
                        text_color="#2C3E50").grid(row=row_num, column=1, padx=3, pady=6, sticky="w")
            ctk.CTkLabel(table_inner, text=kategori, font=("Inter", 11), 
                        text_color="#2C3E50").grid(row=row_num, column=2, padx=3, pady=6, sticky="w")
            ctk.CTkLabel(table_inner, text=lokasi, font=("Inter", 11), 
                        text_color="#2C3E50").grid(row=row_num, column=3, padx=3, pady=6, sticky="w")
            ctk.CTkLabel(table_inner, text=perusahaan, font=("Inter", 11), 
                        text_color="#2C3E50").grid(row=row_num, column=4, padx=3, pady=6, sticky="w")
            ctk.CTkLabel(table_inner, text=status, font=("Inter", 11, "bold"), 
                        text_color=status_color).grid(row=row_num, column=5, padx=3, pady=6, sticky="w")
            ctk.CTkLabel(table_inner, text=interval, font=("Inter", 11), 
                        text_color="#2C3E50").grid(row=row_num, column=6, padx=3, pady=6, sticky="w")
            
            # Action buttons
            action_frame = ctk.CTkFrame(table_inner, fg_color="transparent")
            action_frame.grid(row=row_num, column=7, padx=3, pady=3)
            
            ctk.CTkButton(action_frame, text="👁️", width=28, height=26, corner_radius=5,
                         fg_color="#EBF5FB", text_color="#3498DB",
                         command=lambda r=row: self.show_detail(r)).pack(side="left", padx=1)
            
            if hasattr(self.user, 'can_crud') and self.user.can_crud:
                ctk.CTkButton(action_frame, text="✏️", width=28, height=26, corner_radius=5,
                             fg_color="#FEF9E7", text_color="#F39C12",
                             command=lambda k=kode: self.show_edit_form(k)).pack(side="left", padx=1)
                ctk.CTkButton(action_frame, text="🗑️", width=28, height=26, corner_radius=5,
                             fg_color="#FDEDEC", text_color="#E74C3C",
                             command=lambda k=kode: self.delete_machine(k)).pack(side="left", padx=1)
            
            row_num += 1
            
            sep = ctk.CTkFrame(table_inner, fg_color="#F0F2F5", height=1)
            sep.grid(row=row_num, column=0, columnspan=len(headers), sticky="ew")
            row_num += 1
        
        # Pagination controls
        if total_pages > 1:
            info_label = ctk.CTkLabel(self.pagination_frame, 
                                      text=f"Menampilkan {start_idx + 1}-{end_idx} dari {total_rows} data", 
                                      font=("Inter", 11), text_color="#7F8C8D")
            info_label.pack(side="left", padx=10)
            
            nav_frame = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
            nav_frame.pack(side="right", padx=10)
            
            prev_btn = ctk.CTkButton(nav_frame, text="◀ Prev", width=80, height=32, corner_radius=6,
                                     fg_color="#1E3A5F" if self.current_page > 0 else "#CBD5E1",
                                     state="normal" if self.current_page > 0 else "disabled",
                                     command=self.prev_page)
            prev_btn.pack(side="left", padx=5)
            
            page_label = ctk.CTkLabel(nav_frame, text=f"{self.current_page + 1} / {total_pages}", 
                                      font=("Inter", 12, "bold"), text_color="#2C3E50")
            page_label.pack(side="left", padx=15)
            
            next_btn = ctk.CTkButton(nav_frame, text="Next ▶", width=80, height=32, corner_radius=6,
                                     fg_color="#1E3A5F" if self.current_page < total_pages - 1 else "#CBD5E1",
                                     state="normal" if self.current_page < total_pages - 1 else "disabled",
                                     command=self.next_page)
            next_btn.pack(side="left", padx=5)
    
    def _show_empty_state(self, message):
        empty_frame = ctk.CTkFrame(self.table_card, fg_color="transparent")
        empty_frame.pack(expand=True, fill="both")
        ctk.CTkLabel(empty_frame, text=message, font=("Inter", 15), text_color="#95A5A6").pack(pady=50)
        
        if hasattr(self.user, 'can_crud') and self.user.can_crud:
            ctk.CTkLabel(empty_frame, text="Klik tombol '+ Tambah Mesin' untuk memulai", 
                        font=("Inter", 12), text_color="#BDC3C7").pack()
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_table_data()
    
    def next_page(self):
        df = self.data_manager.get_data_mesin(user=self.user)
        
        if hasattr(self.user, 'role') and self.user.role == 'pelanggan':
            user_perusahaan = self._get_user_perusahaan()
            if not df.empty and 'perusahaan' in df.columns:
                df = df[df['perusahaan'].astype(str).str.strip().str.lower() == user_perusahaan.lower()]
        
        search_text = self.search_entry.get().strip().lower()
        if search_text and not df.empty:
            df = df[df['kode_mesin'].astype(str).str.lower().str.contains(search_text, na=False) |
                    df['nama_mesin'].astype(str).str.lower().str.contains(search_text, na=False)]
        
        total_pages = (len(df) + self.rows_per_page - 1) // self.rows_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.load_table_data()
    
    def show_add_form(self):
        form = ctk.CTkToplevel(self)
        form.title("Tambah Mesin Baru")
        form.geometry("520" if self.user.role == 'admin' else "500")
        form.grab_set()
        form.configure(fg_color="#F0F2F5")
        
        main_frame = ctk.CTkFrame(form, fg_color="white", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="Form Tambah Mesin", font=("Inter", 18, "bold"), 
                    text_color="#2C3E50").pack(pady=(20, 15))
        
        fields_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent", height=400)
        fields_frame.pack(padx=30, fill="both", expand=True)
        
        fields = [
            ("Kode Mesin *", "kode_mesin"),
            ("Nama Mesin *", "nama_mesin"),
            ("Kategori", "kategori"),
            ("Lokasi", "lokasi"),
            ("Perusahaan", "perusahaan"),
            ("Interval Servis (hari)", "interval_servis_hari")
        ]
        
        self.form_entries = {}
        
        for label, key in fields:
            ctk.CTkLabel(fields_frame, text=label, font=("Inter", 12, "bold"), 
                        text_color="#2C3E50", anchor="w").pack(fill="x", pady=(8, 3))
            entry = ctk.CTkEntry(fields_frame, height=35, corner_radius=8)
            
            if key == "perusahaan" and hasattr(self.user, 'role') and self.user.role == 'pelanggan':
                user_perusahaan = self._get_user_perusahaan()
                entry.insert(0, user_perusahaan)
                entry.configure(state="disabled")
            
            entry.pack(fill="x", pady=(0, 10))
            self.form_entries[key] = entry
        
        # Status ComboBox
        ctk.CTkLabel(fields_frame, text="Status", font=("Inter", 12, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(8, 3))
        status_combo = ctk.CTkComboBox(fields_frame, values=["Aktif", "Rusak", "Dalam Servis"], height=35, corner_radius=8)
        status_combo.set("Aktif")
        status_combo.pack(fill="x", pady=(0, 10))
        self.form_entries["status"] = status_combo
        
        # Note
        note_frame = ctk.CTkFrame(fields_frame, fg_color="#F8F9FA", corner_radius=6)
        note_frame.pack(fill="x", pady=(10, 5))
        ctk.CTkLabel(note_frame, text="ℹ️ Field bertanda * wajib diisi", 
                    font=("Inter", 9), text_color="#7F8C8D").pack(pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(15, 20))
        
        ctk.CTkButton(btn_frame, text="Simpan", command=self.save_machine,
                     fg_color="#27AE60", hover_color="#229954", height=38, corner_radius=8,
                     font=("Inter", 13, "bold")).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Batal", command=form.destroy,
                     fg_color="#95A5A6", hover_color="#7F8C8D", height=38, corner_radius=8,
                     font=("Inter", 13, "bold")).pack(side="left", expand=True, fill="x", padx=(5, 0))
    
    def save_machine(self):
        try:
            kode = self.form_entries["kode_mesin"].get().strip()
            nama = self.form_entries["nama_mesin"].get().strip()
            kategori = self.form_entries["kategori"].get().strip()
            lokasi = self.form_entries["lokasi"].get().strip()
            perusahaan = self.form_entries["perusahaan"].get().strip()
            interval = self.form_entries["interval_servis_hari"].get().strip()
            status = self.form_entries["status"].get()
            
            if not kode or not nama:
                messagebox.showerror("Error", "Kode dan Nama Mesin harus diisi!")
                return
            
            # Konversi interval
            try:
                interval_int = int(interval) if interval else 0
            except:
                interval_int = 0
            
            data = {
                'kode_mesin': kode,
                'nama_mesin': nama,
                'kategori': kategori,
                'lokasi': lokasi,
                'perusahaan': perusahaan,
                'status': status,
                'interval_servis_hari': interval_int,
                'jam_operasi': '',
                'tgl_instalasi': ''
            }
            
            success, msg = self.data_manager.tambah_mesin(data)
            if success:
                messagebox.showinfo("Sukses", msg)
                for widget in self.master.winfo_children():
                    if isinstance(widget, ctk.CTkToplevel):
                        widget.destroy()
                self.load_table_data()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")
    
    def show_detail(self, row):
        detail = ctk.CTkToplevel(self)
        detail.title("Detail Mesin")
        detail.geometry("500x450")
        detail.grab_set()
        detail.configure(fg_color="#F0F2F5")
        
        main_frame = ctk.CTkFrame(detail, fg_color="white", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="🔍 Detail Mesin", font=("Inter", 18, "bold"), 
                    text_color="#2C3E50").pack(pady=(20, 15))
        
        details = [
            ("Kode Mesin", row.get('kode_mesin', '-')),
            ("Nama Mesin", row.get('nama_mesin', '-')),
            ("Kategori", row.get('kategori', '-')),
            ("Lokasi", row.get('lokasi', '-')),
            ("Perusahaan", row.get('perusahaan', '-')),
            ("Status", row.get('status', '-')),
            ("Interval Servis", f"{row.get('interval_servis_hari', '-')} hari")
        ]
        
        for label, value in details:
            frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=6)
            
            ctk.CTkLabel(frame, text=f"{label}:", font=("Inter", 13, "bold"), 
                        width=130, anchor="w", text_color="#2C3E50").pack(side="left")
            ctk.CTkLabel(frame, text=str(value), font=("Inter", 13), 
                        text_color="#7F8C8D", anchor="w").pack(side="left", padx=(10, 0))
        
        ctk.CTkButton(main_frame, text="Tutup", command=detail.destroy,
                     fg_color="#3498DB", width=150, height=35, corner_radius=8).pack(pady=20)
    
    def show_edit_form(self, kode):
        df = self.data_manager.get_data_mesin(user=self.user)
        row = df[df['kode_mesin'].astype(str) == str(kode)]
        if row.empty:
            messagebox.showerror("Error", "Data tidak ditemukan!")
            return
        
        row = row.iloc[0]
        
        form = ctk.CTkToplevel(self)
        form.title(f"Edit Mesin - {kode}")
        form.geometry("520" if self.user.role == 'admin' else "500")
        form.grab_set()
        form.configure(fg_color="#F0F2F5")
        
        main_frame = ctk.CTkFrame(form, fg_color="white", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text=f"Edit Mesin: {kode}", font=("Inter", 18, "bold"), 
                    text_color="#2C3E50").pack(pady=(20, 15))
        
        fields_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent", height=400)
        fields_frame.pack(padx=30, fill="both", expand=True)
        
        edit_fields = [
            ("Nama Mesin", "nama_mesin", str(row.get('nama_mesin', ''))),
            ("Kategori", "kategori", str(row.get('kategori', ''))),
            ("Lokasi", "lokasi", str(row.get('lokasi', ''))),
            ("Perusahaan", "perusahaan", str(row.get('perusahaan', ''))),
            ("Interval Servis (hari)", "interval_servis_hari", str(row.get('interval_servis_hari', '')))
        ]
        
        self.edit_entries = {}
        
        for label, key, default in edit_fields:
            ctk.CTkLabel(fields_frame, text=label, font=("Inter", 12, "bold"), 
                        text_color="#2C3E50", anchor="w").pack(fill="x", pady=(8, 3))
            entry = ctk.CTkEntry(fields_frame, height=35, corner_radius=8)
            entry.insert(0, default)
            
            if key == "perusahaan" and hasattr(self.user, 'role') and self.user.role == 'pelanggan':
                entry.configure(state="disabled")
            
            entry.pack(fill="x", pady=(0, 10))
            self.edit_entries[key] = entry
        
        # Status ComboBox
        ctk.CTkLabel(fields_frame, text="Status", font=("Inter", 12, "bold"), 
                    text_color="#2C3E50", anchor="w").pack(fill="x", pady=(8, 3))
        status_combo = ctk.CTkComboBox(fields_frame, values=["Aktif", "Rusak", "Dalam Servis"], height=35, corner_radius=8)
        status_combo.set(str(row.get('status', 'Aktif')))
        status_combo.pack(fill="x", pady=(0, 10))
        self.edit_entries["status"] = status_combo
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(15, 20))
        
        ctk.CTkButton(btn_frame, text="Batal", command=form.destroy,
                     fg_color="#95A5A6", hover_color="#7F8C8D", height=38, corner_radius=8,
                     font=("Inter", 13, "bold")).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Simpan Perubahan", command=lambda: self._update_machine(kode, form),
                     fg_color="#1E3A5F", hover_color="#2C5282", height=38, corner_radius=8,
                     font=("Inter", 13, "bold")).pack(side="left", expand=True, fill="x", padx=(5, 0))
    
    def _update_machine(self, kode, form=None):
        try:
            data_update = {}
            
            for key, entry in self.edit_entries.items():
                if key == "perusahaan" and hasattr(self.user, 'role') and self.user.role == 'pelanggan':
                    value = self._get_user_perusahaan()
                else:
                    value = entry.get().strip() if hasattr(entry, 'get') else entry.get()
                
                if key == 'interval_servis_hari':
                    try:
                        value = int(float(value)) if value else 0
                    except:
                        value = 0
                elif key == 'status':
                    value = str(value) if value else 'Aktif'
                else:
                    value = str(value) if value else ''
                
                data_update[key] = value
            
            success, msg = self.data_manager.update_mesin(kode, data_update)
            if success:
                messagebox.showinfo("Sukses", msg)
                if form:
                    form.destroy()
                self.load_table_data()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")
    
    def delete_machine(self, kode):
        if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus mesin {kode}?"):
            success, msg = self.data_manager.hapus_mesin(kode)
            if success:
                messagebox.showinfo("Sukses", msg)
                self.load_table_data()
            else:
                messagebox.showerror("Error", msg)