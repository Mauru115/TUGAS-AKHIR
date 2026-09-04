import customtkinter as ctk
import tkinter.messagebox as messagebox

class PrediksiView(ctk.CTkFrame):
    def __init__(self, master, user, data_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.user = user
        self.data_manager = data_manager
        
        # Menyimpan jawaban kuesioner
        self.answers = {}
        
        # =========================================================================
        # 📐 HEADER AREA
        # =========================================================================
        header = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        header.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(header, text="🤖 AI Expert System - Diagnosa Mandiri", font=("Inter", 20, "bold"), 
                    text_color="#2C3E50").pack(pady=(15, 5))
        ctk.CTkLabel(header, text="Jawab kuesioner indikasi fisik di bawah ini untuk menganalisis potensi anomali pada mesin Anda.", 
                    font=("Inter", 11), text_color="#7F8C8D").pack(pady=(0, 15))
        
        # =========================================================================
        # 📊 MAIN CONTENT LAYOUT (Fleksibel memanjang ke bawah layar)
        # =========================================================================
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        
        # -------------------------------------------------------------------------
        # PANEL KIRI: Form Tanya Jawab (Frame Statis, ditarik mentok ke bawah)
        # -------------------------------------------------------------------------
        left_panel = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(left_panel, text="📋 Kuesioner Indikator Fisik Mesin", font=("Inter", 16, "bold"), 
                    text_color="#1E3A5F").pack(anchor="w", padx=20, pady=(20, 10))
        
        self.questions = [
            {
                "id": "getaran",
                "label": "1. Bagaimana kondisi getaran pada bodi mesin?",
                "options": [
                    ("Halus / Normal seperti biasa", 0),
                    ("Sedikit bergetar kasar / Ada hentakan sesekali", 1),
                    ("Bergetar hebat / Goyang tidak stabil", 2)
                ]
            },
            {
                "id": "suhu",
                "label": "2. Bagaimana kondisi suhu permukaan luar komponen utama?",
                "options": [
                    ("Hangat wajar / Normal", 0),
                    ("Lebih panas dari biasanya (Cukup menyengat)", 1),
                    ("Sangat panas (Overheat) / Muncul bau sangit", 2)
                ]
            },
            {
                "id": "suara",
                "label": "3. Apakah terdengar suara asing dari dalam mesin?",
                "options": [
                    ("Tidak ada, suara mesin terdengar konstan", 0),
                    ("Ada suara berdecit halus / Mendengung tidak stabil", 1),
                    ("Ada suara gesekan besi ekstrem / Dentuman keras", 2)
                ]
            },
            {
                "id": "fisik",
                "label": "4. Apakah terlihat ada kebocoran zat cair atau asap?",
                "options": [
                    ("Kering bersih / Tidak ada kebocoran", 0),
                    ("Ada rembesan oli tipis / Debu menumpuk tebal", 1),
                    ("Oli menetes deras / Keluar asap tipis", 2)
                ]
            },
            {
                "id": "performa",
                "label": "5. Bagaimana kecepatan atau output produksi saat ini?",
                "options": [
                    ("Stabil dan sesuai dengan target", 0),
                    ("Sedikit melambat / Kadang tersendat", 1),
                    ("Sering macet (Stuck) / Kecepatan drop drastis", 2)
                ]
            }
        ]
        
        # Render Pertanyaan ke GUI (Padding dirapatkan agar muat 1 layar)
        for q in self.questions:
            q_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
            q_frame.pack(fill="x", padx=20, pady=4, anchor="w")
            
            ctk.CTkLabel(q_frame, text=q["label"], font=("Inter", 13, "bold"), 
                        text_color="#2C3E50").pack(anchor="w", pady=(0, 2))
            
            var = ctk.StringVar(value="0") 
            self.answers[q["id"]] = var
            
            for option_text, weight in q["options"]:
                rb = ctk.CTkRadioButton(q_frame, text=option_text, value=str(weight), 
                                        variable=var, font=("Inter", 12), text_color="#5D6D7E",
                                        hover_color="#3498DB", border_color="#BDC3C7", radiobutton_height=18, radiobutton_width=18)
                rb.pack(anchor="w", padx=10, pady=2)
        
        # Tombol Analisis (Ditempel agak ke bawah)
        ctk.CTkButton(left_panel, text="🚀 Jalankan Diagnosa AI", command=self.process_diagnosa,
                     fg_color="#1E3A5F", hover_color="#2C5282", height=45,
                     font=("Inter", 14, "bold")).pack(padx=25, pady=(15, 20), fill="x", side="bottom")
        
        # -------------------------------------------------------------------------
        # PANEL KANAN: Hasil Evaluasi AI (Frame Statis, ditarik mentok ke bawah)
        # -------------------------------------------------------------------------
        self.right_panel = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=10)
        self.right_panel.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        self.show_default_message()
    
    def show_default_message(self):
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        # Container di tengah (Vertikal & Horizontal)
        center_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(center_frame, text="🔮", font=("Inter", 64)).pack(pady=(0, 20))
        ctk.CTkLabel(center_frame, text="Menunggu Pengisian Kuesioner", 
                    font=("Inter", 18, "bold"), text_color="#7F8C8D").pack(pady=(0, 5))
        ctk.CTkLabel(center_frame, text="Silakan isi seluruh kuesioner indikasi fisik di panel kiri,\nlalu klik tombol Jalankan Diagnosa AI.", 
                    font=("Inter", 13), text_color="#BDC3C7", justify="center").pack()
        
    def process_diagnosa(self):
        total_skor = 0
        detail_kondisi = {}
        
        for q_id, var in self.answers.items():
            skor_opsi = int(var.get())
            total_skor += skor_opsi
            detail_kondisi[q_id] = skor_opsi
            
        if total_skor >= 7 or any(v == 2 for v in detail_kondisi.values()):
            status_color = "#E74C3C" 
            status_text = "⚠️ ANOMALI KRITIKAL TERDETEKSI!"
            status_badge = "🔴 EMERGENCY"
            kesimpulan = "AI mendeteksi adanya malfungsi serius pada komponen internal mesin Anda. Gejala fisik luar menunjukkan kerusakan kumulatif yang butuh penanganan instan."
        elif 3 <= total_skor < 7:
            status_color = "#F39C12" 
            status_text = "⚠️ GEJALA ANOMALI RINGAN (WASPADA)"
            status_badge = "🟠 WARNING"
            kesimpulan = "Mesin beroperasi dalam kondisi suboptimal (tidak prima). Pola gejala ini menandakan adanya keausan part mikro yang jika dibiarkan akan memicu kerusakan fatal."
        else:
            status_color = "#27AE60" 
            status_text = "✅ KONDISI MESIN SEHAT & NORMAL"
            status_badge = "🟢 HEALTHY"
            kesimpulan = "Berdasarkan penilaian indikasi fisik makro, status mekanis dan kelistrikan mesin Anda berada dalam batas aman operasi standar."
            
        self.display_result(status_color, status_text, status_badge, kesimpulan, detail_kondisi)

    def display_result(self, color, text, badge, kesimpulan, detail):
        for widget in self.right_panel.winfo_children():
            widget.destroy()
            
        # 1. Status Banner Card
        banner = ctk.CTkFrame(self.right_panel, fg_color=color, corner_radius=10)
        banner.pack(fill="x", padx=25, pady=(25, 15))
        banner.configure(height=60)
        banner.pack_propagate(False)
        ctk.CTkLabel(banner, text=text, font=("Inter", 15, "bold"), text_color="white").pack(pady=18, padx=20, anchor="w")
        
        # 2. Score Metrics Card
        metrics_card = ctk.CTkFrame(self.right_panel, fg_color="#F8F9FA", corner_radius=10)
        metrics_card.pack(fill="x", padx=25, pady=10)
        
        ctk.CTkLabel(metrics_card, text="🧠 Hasil Diagnosa AI", font=("Inter", 14, "bold"), text_color="#2C3E50").pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(metrics_card, text=f"Klasifikasi Sistem: {badge}", font=("Inter", 13, "bold"), text_color="#2C3E50").pack(anchor="w", padx=20, pady=5)
        
        danger_count = sum(1 for v in detail.values() if v == 2)
        warning_count = sum(1 for v in detail.values() if v == 1)
        persen_risiko = (danger_count * 20) + (warning_count * 10)
        persen_risiko = min(100, persen_risiko if persen_risiko > 0 else 5)
        
        ctk.CTkLabel(metrics_card, text=f"Faktor Risiko Kerusakan: {persen_risiko}%", font=("Inter", 13), text_color="#1F618D").pack(anchor="w", padx=20, pady=(5, 15))
        
        # 3. Kesimpulan Narasi Card
        narrative_card = ctk.CTkFrame(self.right_panel, fg_color="#EBF5FB", corner_radius=10)
        narrative_card.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(narrative_card, text="📝 Analisis Masalah:", font=("Inter", 13, "bold"), text_color="#2980B9").pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(narrative_card, text=kesimpulan, font=("Inter", 12), text_color="#2C3E50", wraplength=450, justify="left").pack(anchor="w", padx=20, pady=(0, 20))
        
        # 4. Rekomendasi Solusi Pintar
        rec_card = ctk.CTkFrame(self.right_panel, fg_color="#FEF9E7", corner_radius=10)
        rec_card.pack(fill="x", padx=25, pady=(10, 25))
        ctk.CTkLabel(rec_card, text="💡 Solusi Tindakan:", font=("Inter", 13, "bold"), text_color="#7E5109").pack(anchor="w", padx=20, pady=(15, 5))
        
        solusi = self.generate_solusi_tindakan(detail)
        ctk.CTkLabel(rec_card, text=solusi, font=("Inter", 12), text_color="#7E5109", wraplength=450, justify="left").pack(anchor="w", padx=20, pady=(0, 20))
        
    def generate_solusi_tindakan(self, detail):
        if detail["getaran"] == 2 or detail["suara"] == 2:
            return "🔴 SEGERA MATIKAN MESIN! Getaran atau suara gesekan besi ekstrem menandakan bearing hancur atau poros as bengkok. Melanjutkan operasi berisiko mematahkan komponen utama roda gigi."
        elif detail["suhu"] == 2:
            return "🔴 BAHAYA OVERHEAT: Segera hentikan pasokan listrik ke motor penggerak. Biarkan mesin mendingin alami selama 1-2 jam. Periksa sirkulasi sistem pendingin (fan/coolant) dan cek resistensi lilitan kabel."
        elif detail["fisik"] == 2:
            return "🔴 KEBOCORAN AKTIF: Kuras/tampung sisa pelumas yang bocor agar tidak korslet ke area kelistrikan. Segera lakukan penggantian seal karet pembungkus tangki oli atau katup hidrolik."
        elif any(v == 1 for v in detail.values()):
            return "🟠 REKOMENDASI JANGKA PENDEK: Mesin masih aman berjalan maksimal 1-2 hari ke depan. Disarankan menjadwalkan inspeksi ringan (pemberian pelumas, pengencangan baut kendur, pembersihan filter filter udara) pada akhir jam operasional nanti."
        else:
            return "✅ REKOMENDASI: Pertahankan ritme kerja mesin saat ini. Lakukan pembersihan bodi mesin secara rutin setiap pergantian shift kerja."