import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import filedialog
import pandas as pd
import os
from fpdf import FPDF

class LaporanView(ctk.CTkFrame):
    def __init__(self, master, user, data_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.data_manager = data_manager
        self.user = user
        
        # Palet warna
        self.colors = {
            "white": "#FFFFFF",
            "bg_light": "#F8F9FA",
            "text_dark": "#1E3A5F",
            "text_light": "#666666",
            "blue": "#1E3A5F",
            "green": "#27AE60",
            "red": "#E74C3C",
            "border": "#E0E0E0",
            "table_header": "#F0F2F5"
        }
        
        # Konfigurasi Grid Utama Halaman Laporan
        self.grid_columnconfigure(0, weight=2, uniform="report_cols")
        self.grid_columnconfigure(1, weight=3, uniform="report_cols")
        
        self.setup_ui()

    def setup_ui(self):
        # ========== KOLOM KIRI: FILTER & KONFIGURASI DATA ==========
        left_frame = ctk.CTkFrame(self, fg_color=self.colors["white"], corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=5)
        
        lbl_filter_title = ctk.CTkLabel(
            left_frame, text="Filter & Cakupan Data", 
            font=("Inter", 18, "bold"), text_color=self.colors["text_dark"]
        )
        lbl_filter_title.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Opsi 1: Kategori Mesin
        lbl_kat = ctk.CTkLabel(left_frame, text="Kategori Mesin", font=("Inter", 13, "bold"), text_color=self.colors["text_light"])
        lbl_kat.pack(anchor="w", padx=20, pady=(5, 2))
        self.combo_kategori = ctk.CTkComboBox(
            left_frame, values=["Semua Kategori", "Packaging", "Plastic", "Metalworking", "Logistics", "Utilities", 
                               "Food & Beverage", "Woodworking", "Textile", "Paper", "Printing", "Power", "Medical/Food"], 
            height=38, font=("Inter", 13), corner_radius=8
        )
        self.combo_kategori.set("Semua Kategori")
        self.combo_kategori.pack(fill="x", padx=20, pady=(0, 15))
        
        # Opsi 2: Rentang Periode Waktu
        lbl_periode = ctk.CTkLabel(left_frame, text="Periode Waktu Laporan", font=("Inter", 13, "bold"), text_color=self.colors["text_light"])
        lbl_periode.pack(anchor="w", padx=20, pady=(5, 2))
        self.combo_periode = ctk.CTkComboBox(
            left_frame, values=["Semua Waktu", "Bulan Ini", "3 Bulan Terakhir", "Tahun Ini"], 
            height=38, font=("Inter", 13), corner_radius=8
        )
        self.combo_periode.set("Semua Waktu")
        self.combo_periode.pack(fill="x", padx=20, pady=(0, 15))

        # Opsi 3: Status Kondisi Mesin
        lbl_status = ctk.CTkLabel(left_frame, text="Status Operasional", font=("Inter", 13, "bold"), text_color=self.colors["text_light"])
        lbl_status.pack(anchor="w", padx=20, pady=(5, 2))
        self.combo_status = ctk.CTkComboBox(
            left_frame, values=["Semua Status", "Aktif", "Rusak", "Dalam Servis"], 
            height=38, font=("Inter", 13), corner_radius=8
        )
        self.combo_status.set("Semua Status")
        self.combo_status.pack(fill="x", padx=20, pady=(0, 15))
        
        # Tombol Reset Filter
        btn_reset = ctk.CTkButton(
            left_frame, text="⟳ Reset Filter", command=self.reset_filter,
            fg_color="#6C757D", hover_color="#5A6268", height=35, corner_radius=8,
            font=("Inter", 12, "bold")
        )
        btn_reset.pack(padx=20, pady=(5, 15), fill="x")
        
        # Informasi Perusahaan yang login
        info_frame = ctk.CTkFrame(left_frame, fg_color="#E8F4FF", corner_radius=8, height=85)
        info_frame.pack(fill="x", padx=20, pady=10)
        info_frame.pack_propagate(False)
        
        if hasattr(self.user, 'role') and self.user.role == 'pelanggan':
            perusahaan = getattr(self.user, 'perusahaan', '-')
            info_text = f"🏢 Anda login sebagai Pelanggan\n   Perusahaan: {perusahaan}\n   Data hanya menampilkan mesin milik perusahaan Anda."
        else:
            info_text = "👑 Anda login sebagai Admin\n   Menampilkan semua data mesin."
        
        lbl_info = ctk.CTkLabel(
            info_frame, text=info_text, 
            font=("Inter", 10), text_color="#0056B3", justify="left"
        )
        lbl_info.place(relx=0.5, rely=0.5, anchor="center")

        # ========== KOLOM KANAN: KARTU PILIHAN EKSPOR LAPORAN ==========
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=5)
        
        # Pilihan Laporan 1
        self.create_export_card(
            right_frame, 
            title="📊 Laporan Inventaris & Data Mesin", 
            desc="Menghasilkan dokumen berisi spesifikasi mesin, kode identifikasi, kategori perangkat, dan status operasional terkini.",
            cmd_excel=self.preview_mesin,
            cmd_pdf=self.ekspor_mesin_pdf
        )
        
        # Pilihan Laporan 2
        self.create_export_card(
            right_frame, 
            title="🔧 Laporan Log Perbaikan & Riwayat Servis", 
            desc="Menghasilkan catatan lengkap berkala mengenai tindakan penanganan teknisi, akumulasi total biaya perbaikan, dan jadwal selanjutnya.",
            cmd_excel=self.preview_servis,
            cmd_pdf=self.ekspor_servis_pdf
        )
        
        # Pilihan Laporan 3
        self.create_export_card(
            right_frame, 
            title="📂 Ringkasan Eksekutif & Komprehensif Summary", 
            desc="Menggabungkan Master Mesin, Log Servis, dan statistik performa dalam satu file (Workbook) terpadu.",
            cmd_excel=self.preview_semua,
            cmd_pdf=None
        )

    def create_export_card(self, parent, title, desc, cmd_excel, cmd_pdf=None):
        card = ctk.CTkFrame(parent, fg_color=self.colors["white"], corner_radius=10)
        card.pack(fill="x", pady=(0, 15))
        
        lbl_title = ctk.CTkLabel(card, text=title, font=("Inter", 16, "bold"), text_color=self.colors["text_dark"])
        lbl_title.pack(anchor="w", padx=20, pady=(16, 6))
        
        lbl_desc = ctk.CTkLabel(
            card, text=desc, font=("Inter", 12), 
            text_color=self.colors["text_light"], wraplength=480, justify="left"
        )
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 16))
        
        btn_container = ctk.CTkFrame(card, fg_color="transparent")
        btn_container.pack(fill="x", padx=20, pady=(0, 16), anchor="w")
        
        if cmd_excel:
            btn_excel = ctk.CTkButton(
                btn_container, text="🟢 Preview & Ekspor Excel", font=("Inter", 12, "bold"),
                fg_color=self.colors["green"], hover_color="#218838", height=34, width=175, corner_radius=8,
                command=cmd_excel
            )
            btn_excel.pack(side="left", padx=(0, 10))
            
        if cmd_pdf:
            btn_pdf = ctk.CTkButton(
                btn_container, text="🔴 Cetak ke PDF", font=("Inter", 12, "bold"),
                fg_color=self.colors["red"], hover_color="#C82333", height=34, width=135, corner_radius=8,
                command=cmd_pdf
            )
            btn_pdf.pack(side="left")

    def reset_filter(self):
        """Reset semua filter ke default"""
        self.combo_kategori.set("Semua Kategori")
        self.combo_periode.set("Semua Waktu")
        self.combo_status.set("Semua Status")
        messagebox.showinfo("Info", "Filter telah direset ke default")

    # ========== LOGIKA PENGAMBILAN DATA DENGAN FILTER PERUSAHAAN ==========
    def dapatkan_data_terfilter(self):
        """Ambil data mesin dan servis dengan filter perusahaan untuk pelanggan"""
        try:
            df_mesin = self.data_manager.get_data_mesin(user=self.user)
            df_servis = self.data_manager.get_data_servis(user=self.user)
            
            # Konversi semua data ke string untuk menghindari error
            if not df_mesin.empty:
                for col in df_mesin.columns:
                    df_mesin[col] = df_mesin[col].astype(str)
                
                # Urutkan kolom agar rapi
                kolom_rapi = ['kode_mesin', 'nama_mesin', 'kategori', 'perusahaan', 'status', 
                              'interval_servis_hari', 'lokasi', 'jam_operasi', 'tgl_instalasi']
                kolom_ada = [k for k in kolom_rapi if k in df_mesin.columns]
                df_mesin = df_mesin[kolom_ada]
            
            if not df_servis.empty:
                for col in df_servis.columns:
                    df_servis[col] = df_servis[col].astype(str)
                
                # Urutkan kolom untuk servis
                kolom_rapi_servis = ['kode_mesin', 'tanggal_perbaikan', 'jenis_kerusakan', 
                                     'teknisi', 'biaya', 'suhu_mesin', 'catatan']
                kolom_ada = [k for k in kolom_rapi_servis if k in df_servis.columns]
                df_servis = df_servis[kolom_ada]
            
            # Filter berdasarkan kategori
            kat_terpilih = self.combo_kategori.get()
            if kat_terpilih != "Semua Kategori" and not df_mesin.empty:
                df_mesin = df_mesin[df_mesin['kategori'].str.lower() == kat_terpilih.lower()]
            
            # Filter berdasarkan status
            stat_terpilih = self.combo_status.get()
            if stat_terpilih != "Semua Status" and not df_mesin.empty:
                df_mesin = df_mesin[df_mesin['status'].str.lower() == stat_terpilih.lower()]
            
            # Filter servis berdasarkan mesin yang sudah difilter
            if not df_mesin.empty and not df_servis.empty:
                mesin_kodes = df_mesin['kode_mesin'].tolist()
                df_servis = df_servis[df_servis['kode_mesin'].isin(mesin_kodes)]
            
            return df_mesin, df_servis
        except Exception as e:
            print(f"Error filtering data: {e}")
            return pd.DataFrame(), pd.DataFrame()

    # ========== PREVIEW MESIN ==========
    def preview_mesin(self):
        try:
            df_mesin, _ = self.dapatkan_data_terfilter()
            
            if df_mesin.empty:
                if hasattr(self.user, 'role') and self.user.role == 'pelanggan':
                    perusahaan = getattr(self.user, 'perusahaan', '-')
                    messagebox.showwarning("Peringatan", 
                        f"Tidak ada data mesin untuk perusahaan {perusahaan}.\n\n"
                        f"Pastikan Anda telah menambahkan data mesin melalui menu Data Mesin.")
                else:
                    messagebox.showwarning("Peringatan", "Data mesin kosong dengan filter yang dipilih.")
                return
            
            df_preview = df_mesin.copy()
            self.tampilkan_jendela_preview(df_preview, "Pratinjau Data Mesin", self.ekspor_mesin_excel)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat preview: {e}")

    # ========== PREVIEW SERVIS ==========
    def preview_servis(self):
        try:
            _, df_servis = self.dapatkan_data_terfilter()
            
            if df_servis.empty:
                if hasattr(self.user, 'role') and self.user.role == 'pelanggan':
                    perusahaan = getattr(self.user, 'perusahaan', '-')
                    messagebox.showwarning("Peringatan", 
                        f"Tidak ada data riwayat servis untuk perusahaan {perusahaan}.\n\n"
                        f"Pastikan Anda telah menambahkan data servis melalui menu Riwayat Servis.")
                else:
                    messagebox.showwarning("Peringatan", "Tidak ditemukan data log riwayat transaksi servis.")
                return
            
            df_preview = df_servis.copy()
            self.tampilkan_jendela_preview(df_preview, "Pratinjau Riwayat Servis", self.ekspor_servis_excel)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat preview: {e}")

    # ========== PREVIEW SEMUA ==========
    def preview_semua(self):
        try:
            df_mesin, df_servis = self.dapatkan_data_terfilter()
            
            summary_data = {
                'Keterangan File': ['Total Aset Mesin', 'Total Catatan Servis', 'Estimasi Total Biaya Servis'],
                'Jumlah Tercatat': [
                    str(len(df_mesin)), 
                    str(len(df_servis)), 
                    "Belum ada data" if df_servis.empty else "Lihat file terpisah"
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            
            self.tampilkan_jendela_preview(df_summary, "Pratinjau Ringkasan Laporan", self.ekspor_semua_excel)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat preview: {e}")

    # ========== FITUR PREVIEW (POPUP JENDELA BARU) ==========
    def tampilkan_jendela_preview(self, df_preview, judul_laporan, fungsi_ekspor_lanjutan):
        try:
            preview_win = ctk.CTkToplevel(self)
            preview_win.title(f"Preview: {judul_laporan}")
            preview_win.geometry("1200x700")
            preview_win.configure(fg_color=self.colors["bg_light"])
            preview_win.attributes("-topmost", True)
            preview_win.grab_set()
            
            # Header Preview
            header_frame = ctk.CTkFrame(preview_win, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=15)
            
            ctk.CTkLabel(header_frame, text=judul_laporan, font=("Inter", 22, "bold"), 
                        text_color=self.colors["text_dark"]).pack(side="left")
            ctk.CTkLabel(header_frame, text=f"Menampilkan {len(df_preview)} baris数据", 
                        font=("Inter", 13), text_color=self.colors["text_light"]).pack(side="right", pady=5)
            
            # Tabel Data Preview dengan Scroll
            table_container = ctk.CTkScrollableFrame(preview_win, fg_color=self.colors["white"], corner_radius=10)
            table_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
            
            if not df_preview.empty:
                kolom = list(df_preview.columns)
                
                # ========== KONFIGURASI LEBAR KOLOM ==========
                lebar_kolom = {
                    'KODE MESIN': 90,
                    'NAMA MESIN': 200,
                    'KATEGORI': 120,
                    'PERUSAHAAN': 160,
                    'STATUS': 100,
                    'INTERVAL SERVIS HARI': 120,
                    'LOKASI': 120,
                    'JAM OPERASI': 100,
                    'TGL INSTALASI': 110,
                    'TANGGAL PERBAIKAN': 110,
                    'JENIS KERUSAKAN': 160,
                    'TEKNISI': 100,
                    'BIAYA': 120,
                    'SUHU MESIN': 90,
                    'CATATAN': 150
                }
                
                # Header tabel
                header_frame_tbl = ctk.CTkFrame(table_container, fg_color=self.colors["table_header"], corner_radius=6, height=45)
                header_frame_tbl.pack(fill="x", pady=(0, 8))
                header_frame_tbl.pack_propagate(False)
                
                header_inner = ctk.CTkFrame(header_frame_tbl, fg_color="transparent")
                header_inner.pack(fill="both", expand=True, padx=10)
                
                for col in kolom:
                    lebar = lebar_kolom.get(col.upper(), 120)
                    lbl = ctk.CTkLabel(
                        header_inner, 
                        text=str(col).replace('_', ' ').upper(), 
                        font=("Inter", 11, "bold"), 
                        text_color="#2C3E50", 
                        width=lebar, 
                        anchor="center"
                    )
                    lbl.pack(side="left", padx=2, pady=8)
                
                # Data rows
                for i, (_, row) in enumerate(df_preview.head(100).iterrows()):
                    bg_color = "#FAFBFC" if i % 2 == 0 else "white"
                    row_frame = ctk.CTkFrame(table_container, fg_color=bg_color, corner_radius=0, height=38)
                    row_frame.pack(fill="x", pady=1)
                    row_frame.pack_propagate(False)
                    
                    row_inner = ctk.CTkFrame(row_frame, fg_color="transparent")
                    row_inner.pack(fill="both", expand=True, padx=10)
                    
                    for col in kolom:
                        lebar = lebar_kolom.get(col.upper(), 120)
                        value = str(row[col]) if row[col] is not None else ''
                        
                        # Potong teks jika terlalu panjang
                        if len(value) > 25:
                            value = value[:22] + "..."
                        
                        # Tentukan perataan berdasarkan jenis data
                        if col.upper() in ['KODE MESIN', 'STATUS', 'INTERVAL SERVIS HARI', 'JAM OPERASI', 'BIAYA', 'SUHU MESIN']:
                            anchor = "center"
                        else:
                            anchor = "w"
                        
                        lbl = ctk.CTkLabel(
                            row_inner, 
                            text=value, 
                            font=("Inter", 10), 
                            text_color="#2C3E50", 
                            width=lebar, 
                            anchor=anchor
                        )
                        lbl.pack(side="left", padx=2, pady=5)
            else:
                ctk.CTkLabel(
                    table_container, 
                    text="⚠️ Tidak ada data yang sesuai dengan filter Anda.", 
                    font=("Inter", 14), 
                    text_color=self.colors["red"]
                ).pack(pady=50)

            # Tombol Aksi Bawah
            aksi_frame = ctk.CTkFrame(preview_win, fg_color="transparent")
            aksi_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            btn_batal = ctk.CTkButton(
                aksi_frame, 
                text="Tutup & Batal", 
                fg_color="#6C757D", 
                hover_color="#5A6268", 
                command=preview_win.destroy, 
                width=120, 
                height=38, 
                corner_radius=8,
                font=("Inter", 12, "bold")
            )
            btn_batal.pack(side="left")
            
            def lanjutkan_ekspor():
                preview_win.destroy()
                if fungsi_ekspor_lanjutan:
                    fungsi_ekspor_lanjutan()
                    
            btn_lanjut = ctk.CTkButton(
                aksi_frame, 
                text="✅ Konfirmasi Ekspor ke Excel", 
                fg_color=self.colors["green"], 
                hover_color="#218838", 
                font=("Inter", 13, "bold"),
                command=lanjutkan_ekspor, 
                width=220, 
                height=38, 
                corner_radius=8
            )
            btn_lanjut.pack(side="right")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka preview: {e}")

    # ========== EKSPOR EXCEL MESIN ==========
    def ekspor_mesin_excel(self):
        try:
            df_mesin, _ = self.dapatkan_data_terfilter()
            if df_mesin.empty:
                messagebox.showwarning("Peringatan", "Tidak ada data untuk diekspor!")
                return
            
            df_export = df_mesin.copy()
            for col in df_export.columns:
                df_export[col] = df_export[col].astype(str)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile="laporan_data_mesin.xlsx"
            )
            if file_path:
                df_export.to_excel(file_path, index=False, sheet_name="Master Data Mesin")
                messagebox.showinfo("Sukses", f"Dokumen laporan data mesin berhasil diekspor ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor data: {e}")

    # ========== EKSPOR EXCEL SERVIS ==========
    def ekspor_servis_excel(self):
        try:
            _, df_servis = self.dapatkan_data_terfilter()
            if df_servis.empty:
                messagebox.showwarning("Peringatan", "Tidak ada数据 untuk diekspor!")
                return
            
            df_export = df_servis.copy()
            for col in df_export.columns:
                df_export[col] = df_export[col].astype(str)
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile="laporan_riwayat_servis.xlsx"
            )
            if file_path:
                df_export.to_excel(file_path, index=False, sheet_name="Log Aktivitas Servis")
                messagebox.showinfo("Sukses", f"Dokumen laporan log riwayat servis berhasil diekspor ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor数据: {e}")

    # ========== EKSPOR EXCEL SEMUA ==========
    def ekspor_semua_excel(self):
        try:
            df_mesin, df_servis = self.dapatkan_data_terfilter()
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile="laporan_ringkasan_maintora.xlsx"
            )
            if file_path:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    if not df_mesin.empty:
                        df_export_mesin = df_mesin.copy()
                        for col in df_export_mesin.columns:
                            df_export_mesin[col] = df_export_mesin[col].astype(str)
                        df_export_mesin.to_excel(writer, sheet_name='Data Mesin', index=False)
                    
                    if not df_servis.empty:
                        df_export_servis = df_servis.copy()
                        for col in df_export_servis.columns:
                            df_export_servis[col] = df_export_servis[col].astype(str)
                        df_export_servis.to_excel(writer, sheet_name='Riwayat Servis', index=False)
                    
                    summary_data = {
                        'Total Aset Mesin Terdaftar': [str(len(df_mesin))],
                        'Total Log Kasus Servis': [str(len(df_servis))],
                        'Tanggal Ekspor': [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary Ringkasan', index=False)
                    
                messagebox.showinfo("Sukses", f"Ringkasan laporan berhasil diekspor ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor data: {e}")

    # ========== EKSPOR PDF MESIN ==========
    def ekspor_mesin_pdf(self):
        try:
            df_mesin, _ = self.dapatkan_data_terfilter()
            if df_mesin.empty:
                messagebox.showwarning("Peringatan", "Tidak ada数据 untuk diekspor!")
                return
            
            self.buat_dokumen_pdf(df_mesin, "Laporan Inventaris Mesin", "laporan_data_mesin.pdf")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor PDF: {e}")

    # ========== EKSPOR PDF SERVIS ==========
    def ekspor_servis_pdf(self):
        try:
            _, df_servis = self.dapatkan_data_terfilter()
            if df_servis.empty:
                messagebox.showwarning("Peringatan", "Tidak ada数据 untuk diekspor!")
                return
            
            self.buat_dokumen_pdf(df_servis, "Laporan Riwayat Servis", "laporan_riwayat_servis.pdf")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor PDF: {e}")

    # ========== HELPER CETAK PDF ==========
    def buat_dokumen_pdf(self, df, judul_laporan, default_filename):
        if df.empty:
            messagebox.showwarning("Peringatan", "Tidak ada数据 untuk diekspor.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_filename
        )
        
        if not file_path:
            return

        try:
            def hex_to_rgb(hex_str):
                hex_str = hex_str.lstrip('#')
                return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

            pdf = FPDF(orientation='L', unit='mm', format='A4') 
            pdf.add_page()
            
            # Judul
            pdf.set_font("Arial", 'B', 16)
            pdf.set_text_color(*hex_to_rgb("#1E3A5F"))
            pdf.cell(0, 12, judul_laporan, ln=True, align='C')
            pdf.ln(6)
            
            # Informasi tambahan
            pdf.set_font("Arial", '', 10)
            pdf.set_text_color(*hex_to_rgb("#666666"))
            if hasattr(self.user, 'role') and self.user.role == 'pelanggan':
                pdf.cell(0, 8, f"Perusahaan: {getattr(self.user, 'perusahaan', '-')}", ln=True, align='L')
            pdf.cell(0, 8, f"Tanggal Cetak: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='L')
            pdf.ln(8)

            # ========== KONFIGURASI LEBAR KOLOM PDF ==========
            lebar_kolom_pdf = {
                'KODE MESIN': 22,
                'NAMA MESIN': 45,
                'KATEGORI': 28,
                'PERUSAHAAN': 35,
                'STATUS': 18,
                'INTERVAL SERVIS HARI': 20,
                'LOKASI': 25,
                'JAM OPERASI': 20,
                'TGL INSTALASI': 22,
                'TANGGAL PERBAIKAN': 22,
                'JENIS KERUSAKAN': 40,
                'TEKNISI': 22,
                'BIAYA': 25,
                'SUHU MESIN': 18,
                'CATATAN': 30
            }
            
            kolom = list(df.columns)
            lebar_kolom_list = []
            nama_kolom_clean = []
            
            for col in kolom:
                clean_name = str(col).replace('_', ' ').upper()
                nama_kolom_clean.append(clean_name)
                lebar_kolom_list.append(lebar_kolom_pdf.get(clean_name, 25))

            # Header tabel dengan background biru
            pdf.set_font("Arial", 'B', 9)
            pdf.set_fill_color(*hex_to_rgb("#1E3A5F"))
            pdf.set_text_color(255, 255, 255)
            
            for i, col_name in enumerate(nama_kolom_clean):
                pdf.cell(lebar_kolom_list[i], 10, col_name, border=1, align='C', fill=True)
            pdf.ln()

            # Isi data dengan zebra striping
            pdf.set_font("Arial", '', 8)
            pdf.set_text_color(*hex_to_rgb("#333333"))
            
            status_zebra = False
            
            for _, row in df.iterrows():
                if status_zebra:
                    pdf.set_fill_color(*hex_to_rgb("#F8F9FA"))
                else:
                    pdf.set_fill_color(255, 255, 255)
                
                for i, item in enumerate(row):
                    teks = str(item) if item is not None else ''
                    lebar_cell = lebar_kolom_list[i]
                    
                    # Potong teks jika terlalu panjang
                    while pdf.get_string_width(teks) > (lebar_cell - 2):
                        teks = teks[:-1]
                        if pdf.get_string_width(teks + "...") <= (lebar_cell - 2):
                            teks += "..."
                            break
                    
                    # Tentukan alignment
                    if nama_kolom_clean[i] in ['KODE MESIN', 'STATUS', 'BIAYA', 'INTERVAL SERVIS HARI', 'JAM OPERASI', 'SUHU MESIN']:
                        align_mode = 'C'
                    else:
                        align_mode = 'L'
                        
                    pdf.cell(lebar_cell, 8, teks, border=1, align=align_mode, fill=True)
                
                pdf.ln()
                status_zebra = not status_zebra

            pdf.output(file_path)
            messagebox.showinfo("Sukses", f"Dokumen {judul_laporan} berhasil diekspor ke:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor data ke PDF: {e}")