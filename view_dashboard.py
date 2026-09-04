import customtkinter as ctk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, user, data_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.data_manager = data_manager
        self.user = user
        self.master_app = self._get_master_app(master)
        
        # Ambil data mesin
        try:
            df_mesin = data_manager.get_data_mesin()
            if df_mesin is None:
                df_mesin = pd.DataFrame()
        except Exception as e:
            print(f"Error loading data: {e}")
            df_mesin = pd.DataFrame()
        
        # Filter berdasarkan perusahaan untuk pelanggan
        try:
            user_role = getattr(self.user, 'role', '').lower()
            if user_role == 'pelanggan':
                nama_perusahaan = getattr(self.user, 'perusahaan', None)
                if nama_perusahaan and not df_mesin.empty and 'perusahaan' in df_mesin.columns:
                    df_mesin = df_mesin[df_mesin['perusahaan'].astype(str).str.lower() == str(nama_perusahaan).lower()]
        except Exception as filter_error:
            print(f"Gagal melakukan filtering dashboard: {filter_error}")
        
        total = len(df_mesin) if not df_mesin.empty else 0
        aktif = 0
        rusak = 0
        dalam_servis = 0
        
        if not df_mesin.empty and 'status' in df_mesin.columns:
            try:
                aktif = len(df_mesin[df_mesin['status'].str.lower() == 'aktif'])
                rusak = len(df_mesin[df_mesin['status'].str.lower() == 'rusak'])
                dalam_servis = len(df_mesin[df_mesin['status'].str.lower() == 'dalam servis'])
            except:
                aktif = total
                rusak = 0
                dalam_servis = 0
        
        # ========== KARTU STATISTIK ==========
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 15))
        
        cards_data = [
            ("Total Mesin", f"{total}", "Unit", "#3498DB", "⚙️"),
            ("Mesin Aktif", f"{aktif}", "Unit", "#27AE60", "✅"),
            ("Mesin Rusak", f"{rusak}", "Unit", "#E74C3C", "❌"),
            ("Dalam Servis", f"{dalam_servis}", "Unit", "#F39C12", "🔧"),
        ]
        
        for i, (title, val, unit, color, icon) in enumerate(cards_data):
            card = self._make_stat_card(cards_frame, title, val, unit, color, icon)
            card.grid(row=0, column=i, padx=(0 if i==0 else 8, 0), sticky="ew")
        cards_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        # ========== CHARTS ROW ==========
        charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        charts_frame.pack(fill="x", pady=(0, 15))
        charts_frame.grid_columnconfigure(0, weight=3)
        charts_frame.grid_columnconfigure(1, weight=2)
        
        # Line chart - Tren Suhu
        chart1 = ctk.CTkFrame(charts_frame, fg_color="white", corner_radius=10)
        chart1.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        
        c1_header = ctk.CTkFrame(chart1, fg_color="transparent")
        c1_header.pack(fill="x", padx=15, pady=(12, 0))
        ctk.CTkLabel(c1_header, text="Tren Suhu Mesin (°C)", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50").pack(side="left")
        self._draw_line_chart(chart1)
        
        # Pie chart - Distribusi Status (seperti gambar referensi)
        chart2 = ctk.CTkFrame(charts_frame, fg_color="white", corner_radius=10)
        chart2.grid(row=0, column=1, sticky="nsew")
        
        c2_header = ctk.CTkFrame(chart2, fg_color="transparent")
        c2_header.pack(fill="x", padx=15, pady=(12, 0))
        ctk.CTkLabel(c2_header, text="Distribusi Status Mesin", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50").pack(side="left")
        self._draw_pie_chart(chart2, aktif, rusak, dalam_servis, total)
        
        # ========== NOTIFIKASI + SERVIS TERAKHIR ==========
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True)
        bottom_frame.grid_columnconfigure(0, weight=2)
        bottom_frame.grid_columnconfigure(1, weight=3)
        
        # Notifikasi Servis Mendekati
        notif_card = ctk.CTkFrame(bottom_frame, fg_color="white", corner_radius=10)
        notif_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        
        ctk.CTkLabel(notif_card, text="Notifikasi Servis Mendekati", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50").pack(anchor="w", padx=15, pady=(12, 8))
        
        sep = ctk.CTkFrame(notif_card, fg_color="#E0E0E0", height=1)
        sep.pack(fill="x", padx=15, pady=(0, 8))
        
        # Notifikasi dari data real
        notif_items = []
        if not df_mesin.empty:
            for _, row in df_mesin.head(3).iterrows():
                kode = str(row.get('kode_mesin', '-'))
                nama = str(row.get('nama_mesin', '-'))[:25]
                interval = str(row.get('interval_servis_hari', '60'))
                notif_items.append({
                    "title": f"{kode} - {nama}",
                    "msg": f"Perlu servis dalam {interval} hari",
                    "color": "#F39C12"
                })
        
        if notif_items:
            for item in notif_items:
                n_frame = ctk.CTkFrame(notif_card, fg_color="#FFF9E6", corner_radius=8)
                n_frame.pack(fill="x", padx=12, pady=3)
                
                inner = ctk.CTkFrame(n_frame, fg_color="transparent")
                inner.pack(fill="x", padx=10, pady=8)
                
                dot = ctk.CTkFrame(inner, fg_color=item["color"], width=8, height=8, corner_radius=4)
                dot.pack(side="left", padx=(0, 8))
                dot.pack_propagate(False)
                
                text_f = ctk.CTkFrame(inner, fg_color="transparent")
                text_f.pack(side="left", fill="both", expand=True)
                ctk.CTkLabel(text_f, text=item["title"], font=("Inter", 11, "bold"), 
                            text_color="#2C3E50", anchor="w").pack(fill="x")
                ctk.CTkLabel(text_f, text=item["msg"], font=("Inter", 10), 
                            text_color="#7F8C8D", anchor="w").pack(fill="x")
        else:
            empty_notif = ctk.CTkFrame(notif_card, fg_color="#F8F9FA", corner_radius=8)
            empty_notif.pack(fill="x", padx=12, pady=10)
            ctk.CTkLabel(empty_notif, text="🔔 Belum ada notifikasi servis", 
                        font=("Inter", 11), text_color="#7F8C8D").pack(pady=10)
        
        see_all_notif = ctk.CTkLabel(notif_card, text="Lihat semua →", font=("Inter", 11), 
                                     text_color="#3498DB", cursor="hand2")
        see_all_notif.pack(anchor="w", padx=15, pady=(8, 12))
        see_all_notif.bind("<Button-1>", lambda e: self._go_to_notifikasi())
        
        # Servis Terakhir table
        servis_card = ctk.CTkFrame(bottom_frame, fg_color="white", corner_radius=10)
        servis_card.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(servis_card, text="Servis Terakhir", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50").pack(anchor="w", padx=15, pady=(12, 5))
        
        # Table header
        headers = ["Mesin", "Tanggal", "Jenis Kerusakan", "Teknisi"]
        col_widths = [130, 90, 160, 80]
        
        h_frame = ctk.CTkFrame(servis_card, fg_color="#F8F9FA", corner_radius=0)
        h_frame.pack(fill="x", padx=0)
        
        h_inner = ctk.CTkFrame(h_frame, fg_color="transparent")
        h_inner.pack(fill="x", padx=15, pady=8)
        for h, w in zip(headers, col_widths):
            ctk.CTkLabel(h_inner, text=h, width=w, font=("Inter", 11, "bold"), 
                        text_color="#7F8C8D", anchor="w").pack(side="left")
        
        # Data servis real
        df_servis = data_manager.get_data_servis()
        servis_data = []
        
        if df_servis is not None and not df_servis.empty:
            for _, row in df_servis.tail(5).iterrows():
                kode = str(row.get('kode_mesin', '-'))
                nama_mesin = kode
                if not df_mesin.empty:
                    m = df_mesin[df_mesin['kode_mesin'].astype(str) == kode]
                    if not m.empty:
                        nama_mesin = str(m.iloc[0]['nama_mesin'])[:18]
                servis_data.append({
                    'nama': f"{kode} - {nama_mesin}",
                    'tanggal': str(row.get('tanggal_perbaikan', '-'))[:10],
                    'kerusakan': str(row.get('jenis_kerusakan', '-'))[:20],
                    'teknisi': str(row.get('teknisi', '-'))[:10],
                })
        
        if servis_data:
            for row_data in servis_data[:5]:
                r_frame = ctk.CTkFrame(servis_card, fg_color="transparent")
                r_frame.pack(fill="x", padx=15, pady=5)
                
                ctk.CTkLabel(r_frame, text=row_data['nama'], width=col_widths[0], font=("Inter", 11), 
                            text_color="#2C3E50", anchor="w").pack(side="left")
                ctk.CTkLabel(r_frame, text=row_data['tanggal'], width=col_widths[1], font=("Inter", 11), 
                            text_color="#7F8C8D", anchor="w").pack(side="left")
                ctk.CTkLabel(r_frame, text=row_data['kerusakan'], width=col_widths[2], font=("Inter", 11), 
                            text_color="#2C3E50", anchor="w").pack(side="left")
                ctk.CTkLabel(r_frame, text=row_data['teknisi'], width=col_widths[3], font=("Inter", 11), 
                            text_color="#2C3E50", anchor="w").pack(side="left")
                
                ctk.CTkFrame(servis_card, fg_color="#F0F2F5", height=1).pack(fill="x", padx=15)
        else:
            empty_row = ctk.CTkFrame(servis_card, fg_color="transparent")
            empty_row.pack(fill="x", padx=15, pady=20)
            ctk.CTkLabel(empty_row, text="📋", font=("Inter", 24)).pack()
            ctk.CTkLabel(empty_row, text="Belum ada riwayat servis", 
                        font=("Inter", 11), text_color="#95A5A6").pack()
        
        lihat_btn = ctk.CTkLabel(servis_card, text="Lihat semua riwayat →", font=("Inter", 11), 
                                  text_color="#3498DB", cursor="hand2")
        lihat_btn.pack(anchor="center", pady=(8, 12))
        lihat_btn.bind("<Button-1>", lambda e: self._go_to_riwayat_servis())
    
    def _get_master_app(self, master):
        while master is not None:
            if hasattr(master, 'load_view') and hasattr(master, 'nav_buttons'):
                return master
            master = master.master
        return None
    
    def _go_to_notifikasi(self):
        if self.master_app and hasattr(self.master_app, 'load_view'):
            for menu_text, btn in self.master_app.nav_buttons.items():
                if "Notifikasi" in menu_text:
                    try:
                        btn.invoke()
                    except:
                        pass
                    break
    
    def _go_to_riwayat_servis(self):
        if self.master_app and hasattr(self.master_app, 'load_view'):
            for menu_text, btn in self.master_app.nav_buttons.items():
                if "Riwayat Servis" in menu_text:
                    try:
                        btn.invoke()
                    except:
                        pass
                    break
    
    def _make_stat_card(self, parent, title, value, unit, color, icon):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, height=95)
        card.pack_propagate(False)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)
        
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(left, text=icon, font=("Inter", 26), text_color=color).pack(anchor="w")
        ctk.CTkLabel(left, text=title, font=("Inter", 11), text_color="#7F8C8D", anchor="w").pack(fill="x")
        
        val_frame = ctk.CTkFrame(inner, fg_color="transparent")
        val_frame.pack(side="right", anchor="center")
        ctk.CTkLabel(val_frame, text=value, font=("Inter", 26, "bold"), text_color=color).pack()
        ctk.CTkLabel(val_frame, text=unit, font=("Inter", 10), text_color="#7F8C8D").pack()
        
        return card
    
    def _draw_line_chart(self, parent):
        """Grafik tren suhu dari data real"""
        try:
            plt.close('all')
            
            fig, ax = plt.subplots(figsize=(6, 2.8), dpi=90)
            fig.patch.set_facecolor('white')
            ax.set_facecolor('#F8F9FA')
            
            df_servis = self.data_manager.get_data_servis()
            suhu_data = []
            tanggal_data = []
            
            if df_servis is not None and not df_servis.empty and 'suhu_mesin' in df_servis.columns and 'tanggal_perbaikan' in df_servis.columns:
                for _, row in df_servis.iterrows():
                    suhu = row.get('suhu_mesin', '')
                    tanggal = row.get('tanggal_perbaikan', '')
                    if suhu and str(suhu) not in ['nan', 'None', ''] and tanggal:
                        try:
                            suhu_data.append(float(suhu))
                            tanggal_data.append(str(tanggal)[:10])
                        except:
                            pass
            
            if len(suhu_data) == 0:
                ax.text(0.5, 0.5, "Belum Ada Data Suhu\nTambahkan data suhu pada riwayat servis", 
                       ha='center', va='center', transform=ax.transAxes, fontsize=9, color='#95A5A6')
                ax.set_title('Tren Suhu Mesin', fontsize=11, fontweight='bold', pad=10)
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_visible(False)
            else:
                if len(tanggal_data) > 7:
                    tanggal_data = tanggal_data[-7:]
                    suhu_data = suhu_data[-7:]
                
                ax.plot(tanggal_data, suhu_data, marker='o', color='#3498DB', linewidth=2, markersize=6)
                ax.fill_between(range(len(tanggal_data)), suhu_data, alpha=0.1, color='#3498DB')
                
                for i, (x, y) in enumerate(zip(tanggal_data, suhu_data)):
                    ax.annotate(f'{y:.0f}°', (i, y), textcoords="offset points", xytext=(0, 8),
                               ha='center', fontsize=8, fontweight='bold', color='#3498DB')
                
                ax.set_xticks(range(len(tanggal_data)))
                ax.set_xticklabels(tanggal_data, rotation=45, ha='right', fontsize=7)
                ax.set_ylabel('Suhu (°C)', fontsize=8, color='#7F8C8D')
                ax.set_title('Tren Suhu Mesin', fontsize=11, fontweight='bold', pad=10)
                ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='#BDC3C7')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#E0E0E0')
                ax.spines['bottom'].set_color('#E0E0E0')
                
                ax.axhline(y=75, color='#E74C3C', linestyle='--', linewidth=1, alpha=0.7)
                ax.text(0.98, 0.95, 'Batas Waspada 75°C', transform=ax.transAxes, 
                       fontsize=7, color='#E74C3C', ha='right', va='top')
            
            fig.tight_layout(pad=1.0)
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(5, 10))
            
        except Exception as e:
            print(f"Error drawing line chart: {e}")
            self._show_fallback(parent, "Grafik Suhu")
    
    def _draw_pie_chart(self, parent, aktif, rusak, dalam_servis, total):
        """Grafik distribusi status - Pie Chart tanpa persentase di dalam"""
        try:
            plt.close('all')
            
            fig, ax = plt.subplots(figsize=(6, 4.5), dpi=100)
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            
            if total == 0:
                ax.text(0.5, 0.5, "Belum Ada Data Mesin", 
                    ha='center', va='center', transform=ax.transAxes, fontsize=12, color='#95A5A6')
                ax.set_title('Distribusi Status Mesin', fontsize=13, fontweight='bold', pad=15)
            else:
                # Data
                labels = ['Aktif', 'Rusak', 'Dalam Servis']
                sizes = [aktif, rusak, dalam_servis]
                colors = ['#2ECC71', '#E74C3C', '#F39C12']
                
                # Filter data yang nilainya > 0
                data_labels = []
                data_sizes = []
                data_colors = []
                for l, s, c in zip(labels, sizes, colors):
                    if s > 0:
                        data_labels.append(l)
                        data_sizes.append(s)
                        data_colors.append(c)
                
                if not data_labels:
                    data_labels = ['Aktif']
                    data_sizes = [1]
                    data_colors = ['#2ECC71']
                
                # PERBAIKAN: Saat autopct=None, hanya mengembalikan 2 nilai (wedges, texts)
                wedges, texts = ax.pie(
                    data_sizes,
                    labels=None,
                    colors=data_colors,
                    autopct=None,                    # Tidak ada persentase
                    startangle=90,
                    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
                )
                
                # LEGEND TERPISAH
                legend_labels = []
                for label, size, color in zip(data_labels, data_sizes, data_colors):
                    persen = (size / total) * 100
                    legend_labels.append(f'{label} - {size} ({persen:.1f}%)')
                
                legend = ax.legend(
                    wedges,
                    legend_labels,
                    loc='center left',
                    bbox_to_anchor=(1, 0.5),
                    fontsize=9,
                    title=f'Total: {total} Mesin',
                    title_fontsize=10,
                    frameon=True,
                    fancybox=False,
                    edgecolor='#E0E0E0'
                )
                legend.get_frame().set_facecolor('white')
                legend.get_frame().set_edgecolor('#E0E0E0')
                
                # Judul
                ax.set_title('Distribusi Status Mesin', fontsize=13, fontweight='bold', pad=15)
                
                # Total di tengah pie
                centre_circle = plt.Circle((0, 0), 0.4, fc='white', linewidth=0, alpha=0.2)
                ax.add_artist(centre_circle)
                ax.text(0, 0, f'{total}', ha='center', va='center', 
                    fontsize=16, fontweight='bold', color='#2C3E50')
            
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(5, 10))
            
        except Exception as e:
            print(f"Error drawing pie chart: {e}")
            # Fallback text
            fallback = ctk.CTkFrame(parent, fg_color="#F8F9FA", corner_radius=8)
            fallback.pack(fill="both", expand=True, padx=10, pady=10)
            ctk.CTkLabel(fallback, text="📊 Distribusi Status Mesin", font=("Inter", 12, "bold")).pack(pady=10)
            if total > 0:
                ctk.CTkLabel(fallback, text=f"✅ Aktif: {aktif} ({aktif/total*100:.1f}%)", font=("Inter", 11)).pack(anchor="w", padx=20)
                ctk.CTkLabel(fallback, text=f"❌ Rusak: {rusak} ({rusak/total*100:.1f}%)", font=("Inter", 11)).pack(anchor="w", padx=20)
                ctk.CTkLabel(fallback, text=f"🔧 Dalam Servis: {dalam_servis} ({dalam_servis/total*100:.1f}%)", font=("Inter", 11)).pack(anchor="w", padx=20)
            else:
                ctk.CTkLabel(fallback, text="Belum ada data mesin", font=("Inter", 11)).pack(pady=20)
    
    def _show_fallback(self, parent, title):
        """Tampilan fallback jika grafik error"""
        fallback_frame = ctk.CTkFrame(parent, fg_color="#F8F9FA", corner_radius=8)
        fallback_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(fallback_frame, text=f"📊 {title}", 
                    font=("Inter", 12, "bold"), text_color="#2C3E50").pack(pady=(10, 5))
        ctk.CTkLabel(fallback_frame, text="Data tidak tersedia untuk ditampilkan", 
                    font=("Inter", 10), text_color="#95A5A6", justify="center").pack(pady=20)