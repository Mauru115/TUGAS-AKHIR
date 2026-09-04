import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class VisualisasiView(ctk.CTkFrame):
    def __init__(self, master, user, data_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.data_manager = data_manager
        self.user = user
        
        # Header
        header = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="📈 Visualisasi Data", font=("Inter", 20, "bold"), 
                    text_color="#2C3E50").pack(pady=15)
        ctk.CTkLabel(header, text="Tren suhu mesin dan distribusi status pemeliharaan", 
                    font=("Inter", 11), text_color="#7F8C8D").pack(pady=(0, 15))
        
        # Chart selection
        select_frame = ctk.CTkFrame(self, fg_color="transparent")
        select_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(select_frame, text="Pilih Visualisasi:", font=("Inter", 13, "bold"), 
                    text_color="#2C3E50").pack(side="left", padx=(0, 10))
        
        self.chart_type = ctk.CTkComboBox(select_frame, 
                                          values=["Distribusi Status", "Tren Suhu Mesin", "Biaya Servis per Bulan"],
                                          width=200, height=35)
        self.chart_type.pack(side="left", padx=(0, 10))
        self.chart_type.set("Distribusi Status")
        
        ctk.CTkButton(select_frame, text="Tampilkan", command=self.update_chart,
                     fg_color="#3498DB", width=100, height=35).pack(side="left")
        
        # Chart container
        self.chart_container = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.chart_container.pack(fill="both", expand=True)
        
        self.update_chart()
    
    def update_chart(self):
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        chart_type = self.chart_type.get()
        
        if chart_type == "Distribusi Status":
            self.draw_status_chart()
        elif chart_type == "Tren Suhu Mesin":
            self.draw_temperature_chart()
        else:
            self.draw_cost_chart()
    
    def draw_status_chart(self):
        """Grafik distribusi status - Pie Chart tanpa persentase di dalam"""
        fig, ax = plt.subplots(figsize=(8, 5.5), dpi=100)
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        df_mesin = self.data_manager.get_data_mesin()
        
        # Filter untuk pelanggan
        if hasattr(self.user, 'role') and self.user.role == 'pelanggan':
            nama_perusahaan = getattr(self.user, 'perusahaan', '')
            if nama_perusahaan and not df_mesin.empty and 'perusahaan' in df_mesin.columns:
                df_mesin = df_mesin[df_mesin['perusahaan'].astype(str).str.lower() == str(nama_perusahaan).lower()]
        
        if df_mesin.empty or 'status' not in df_mesin.columns:
            ax.text(0.5, 0.5, "Belum Ada Data Mesin\nTambahkan data mesin terlebih dahulu", 
                ha='center', va='center', transform=ax.transAxes, fontsize=12, color='#95A5A6')
            ax.set_title('Distribusi Status Mesin', fontsize=14, fontweight='bold', pad=20)
        else:
            status_counts = df_mesin['status'].value_counts()
            labels = status_counts.index.tolist()
            sizes = status_counts.values.tolist()
            total = sum(sizes)
            
            # Warna
            color_map = {
                'Aktif': '#2ECC71',
                'Rusak': '#E74C3C', 
                'Dalam Servis': '#F39C12'
            }
            colors = [color_map.get(l, '#3498DB') for l in labels]
            
            # PERBAIKAN: Saat autopct=None, hanya mengembalikan 2 nilai (wedges, texts)
            # BUKAN 3 nilai (wedges, texts, autotexts)
            wedges, texts = ax.pie(
                sizes,
                labels=None,
                colors=colors,
                autopct=None,                    # Tidak ada persentase
                startangle=90,
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )
            
            # LEGEND TERPISAH di kanan
            legend_labels = []
            for label, size, color in zip(labels, sizes, colors):
                persen = (size / total) * 100 if total > 0 else 0
                legend_labels.append(f'{label} - {size} ({persen:.1f}%)')
            
            legend = ax.legend(
                wedges,
                legend_labels,
                loc='center left',
                bbox_to_anchor=(1, 0.5),
                fontsize=10,
                title=f'📊 Total Mesin: {total}',
                title_fontsize=11,
                frameon=True,
                fancybox=False,
                edgecolor='#E0E0E0'
            )
            legend.get_frame().set_facecolor('white')
            
            # Judul
            ax.set_title('Distribusi Status Mesin', fontsize=15, fontweight='bold', pad=25)
            
            # Total di tengah pie
            centre_circle = plt.Circle((0, 0), 0.4, fc='white', linewidth=0, alpha=0.2)
            ax.add_artist(centre_circle)
            ax.text(0, 0, f'{total}', ha='center', va='center', 
                fontsize=18, fontweight='bold', color='#2C3E50')
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)
    
    def draw_temperature_chart(self):
        """Grafik tren suhu dari data real"""
        fig, ax = plt.subplots(figsize=(9, 5), dpi=100)
        fig.patch.set_facecolor('white')
        ax.set_facecolor('#F8F9FA')
        
        df_servis = self.data_manager.get_data_servis()
        
        if df_servis.empty or 'suhu_mesin' not in df_servis.columns:
            ax.text(0.5, 0.5, "Belum Ada Data Suhu\nTambahkan data suhu pada riwayat servis", 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12, color='#95A5A6')
            ax.set_title('Tren Suhu Mesin', fontsize=13, fontweight='bold', pad=15)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
        else:
            suhu_data = []
            tanggal_data = []
            
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
                       ha='center', va='center', transform=ax.transAxes, fontsize=12, color='#95A5A6')
            else:
                if len(tanggal_data) > 7:
                    tanggal_data = tanggal_data[-7:]
                    suhu_data = suhu_data[-7:]
                
                ax.plot(tanggal_data, suhu_data, marker='o', color='#3498DB', linewidth=2, markersize=7)
                ax.fill_between(range(len(tanggal_data)), suhu_data, alpha=0.1, color='#3498DB')
                
                for i, (x, y) in enumerate(zip(tanggal_data, suhu_data)):
                    ax.annotate(f'{y:.0f}°', (i, y), textcoords="offset points", xytext=(0, 10),
                               ha='center', fontsize=9, fontweight='bold', color='#3498DB')
                
                ax.set_xticks(range(len(tanggal_data)))
                ax.set_xticklabels(tanggal_data, rotation=45, ha='right', fontsize=9)
                ax.set_ylabel('Suhu (°C)', fontsize=11, color='#2C3E50')
                ax.set_xlabel('Tanggal Servis', fontsize=11, color='#2C3E50')
                ax.set_title('Tren Suhu Mesin', fontsize=13, fontweight='bold', pad=15)
                ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='#BDC3C7')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#E0E0E0')
                ax.spines['bottom'].set_color('#E0E0E0')
                
                ax.axhline(y=75, color='#E74C3C', linestyle='--', linewidth=1.5, alpha=0.7, label='Batas Waspada (75°C)')
                ax.legend(loc='upper left', fontsize=9)
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)
    
    def draw_cost_chart(self):
        """Grafik biaya servis dari data real"""
        fig, ax = plt.subplots(figsize=(9, 5), dpi=100)
        fig.patch.set_facecolor('white')
        ax.set_facecolor('#F8F9FA')
        
        # Ambil data servis dengan filter user
        df_servis = self.data_manager.get_data_servis(user=self.user)
        
        # Debug: Cetak jumlah data
        print(f"DEBUG draw_cost_chart: Jumlah data servis = {len(df_servis)}")
        
        if df_servis.empty or 'biaya' not in df_servis.columns:
            ax.text(0.5, 0.5, "Belum Ada Data Biaya Servis\nTambahkan data biaya pada riwayat servis", 
                ha='center', va='center', transform=ax.transAxes, fontsize=12, color='#95A5A6')
            ax.set_title('Total Biaya Servis', fontsize=13, fontweight='bold', pad=15)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
        else:
            # Konversi biaya ke numeric
            df_servis['biaya'] = pd.to_numeric(df_servis['biaya'], errors='coerce').fillna(0)
            
            # Konversi tanggal
            df_servis['tanggal_parsed'] = pd.to_datetime(df_servis['tanggal_perbaikan'], errors='coerce')
            
            # Buat kolom bulan
            df_servis['bulan'] = df_servis['tanggal_parsed'].dt.strftime('%Y-%m')
            df_servis['nama_bulan'] = df_servis['tanggal_parsed'].dt.strftime('%B %Y')
            
            # Kelompokkan berdasarkan bulan
            monthly_cost = df_servis.groupby('bulan')['biaya'].sum().sort_index()
            
            if len(monthly_cost) == 0:
                ax.text(0.5, 0.5, "Belum Ada Data Biaya Servis\nPeriode ini tidak ada data biaya", 
                    ha='center', va='center', transform=ax.transAxes, fontsize=12, color='#95A5A6')
            else:
                # Siapkan data untuk chart
                months = monthly_cost.index.tolist()
                costs = monthly_cost.values.tolist()
                
                # Buat nama bulan yang lebih readable
                bulan_names = []
                for m in months:
                    try:
                        tgl = datetime.strptime(m + "-01", "%Y-%m-%d")
                        bulan_names.append(tgl.strftime("%b %Y"))
                    except:
                        bulan_names.append(m)
                
                # Buat bar chart
                bars = ax.bar(bulan_names, costs, color='#3498DB', edgecolor='white', linewidth=2)
                ax.set_xlabel('Bulan', fontsize=11, color='#2C3E50')
                ax.set_ylabel('Biaya Servis (Rp)', fontsize=11, color='#2C3E50')
                ax.set_title('Total Biaya Servis per Bulan', fontsize=13, fontweight='bold', pad=15)
                
                # Rotasi label bulan agar tidak bertumpuk
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
                
                # Tambahkan nilai di atas bar
                for bar, value in zip(bars, costs):
                    if value > 0:
                        # Format nilai dalam jutaan
                        if value >= 1_000_000:
                            label_text = f'Rp {value/1_000_000:.1f}J'
                        else:
                            label_text = f'Rp {value:,.0f}'
                        
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (max(costs) * 0.02),
                            label_text, ha='center', va='bottom', fontsize=9, fontweight='bold', color='#2C3E50')
                
                # Grid
                ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='#BDC3C7')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#E0E0E0')
                ax.spines['bottom'].set_color('#E0E0E0')
                
                # Total biaya keseluruhan
                total_biaya = sum(costs)
                ax.text(0.98, 0.98, f'Total: Rp {total_biaya:,.0f}', 
                    transform=ax.transAxes, ha='right', va='top',
                    fontsize=10, fontweight='bold', color='#1E3A5F',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)