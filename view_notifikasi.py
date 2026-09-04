import customtkinter as ctk
from datetime import datetime, timedelta
import pandas as pd

class NotifikasiView(ctk.CTkFrame):
    def __init__(self, master, user, data_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.user = user
        self.data_manager = data_manager

        self.active_filter = "semua"
        self.status_notifikasi = {}
        
        self.notifikasi_data = self._get_notifikasi_dari_data()
        self.render()

    def _get_notifikasi_dari_data(self):
        """Ambil notifikasi dari data real (mesin dan servis)"""
        notifikasi = []
        now = datetime.now()
        
        df_mesin = self.data_manager.get_data_mesin()
        
        if hasattr(self.user, 'role') and self.user.role == 'pelanggan':
            nama_perusahaan = getattr(self.user, 'perusahaan', '')
            if nama_perusahaan and not df_mesin.empty and 'perusahaan' in df_mesin.columns:
                df_mesin = df_mesin[df_mesin['perusahaan'].astype(str).str.lower() == str(nama_perusahaan).lower()]
        
        # Notifikasi dari data mesin
        if not df_mesin.empty:
            for _, row in df_mesin.iterrows():
                kode = str(row.get('kode_mesin', '-'))
                nama = str(row.get('nama_mesin', '-'))[:35]
                interval = row.get('interval_servis_hari', 0)
                try:
                    interval = int(interval) if interval and str(interval).isdigit() else 0
                except:
                    interval = 0
                status = str(row.get('status', 'Aktif'))
                
                if interval > 0:
                    notif_id_str = f"servis_{kode}"
                    status_notif = self.status_notifikasi.get(notif_id_str, {"dibaca": False, "clear": False})
                    
                    notifikasi.append({
                        "id": notif_id_str,
                        "judul": f"Jadwal Servis - {kode}",
                        "pesan": f"Mesin {kode} - {nama} memerlukan servis dalam {interval} hari.",
                        "tipe": "servis",
                        "dibaca": status_notif.get("dibaca", False),
                        "clear": status_notif.get("clear", False),
                        "waktu": now - timedelta(days=interval//3),
                        "kode_mesin": kode,
                        "nama_mesin": nama,
                        "interval": interval,
                        "status_mesin": status
                    })
        
        # Notifikasi dari data servis
        df_servis = self.data_manager.get_data_servis()
        if not df_servis.empty:
            for _, row in df_servis.tail(5).iterrows():
                kode = str(row.get('kode_mesin', '-'))
                tanggal = str(row.get('tanggal_perbaikan', '-'))
                kerusakan = str(row.get('jenis_kerusakan', '-'))[:25]
                if tanggal and tanggal != '-' and tanggal != 'nan':
                    try:
                        tgl_servis = datetime.strptime(tanggal, "%Y-%m-%d")
                        if (now - tgl_servis).days <= 30:
                            notif_id_str = f"servis_selesai_{kode}_{tanggal}"
                            status_notif = self.status_notifikasi.get(notif_id_str, {"dibaca": False, "clear": False})
                            
                            notifikasi.append({
                                "id": notif_id_str,
                                "judul": f"Servis Selesai - {kode}",
                                "pesan": f"Servis mesin {kode} selesai tgl {tanggal}. Jenis: {kerusakan}.",
                                "tipe": "servis",
                                "dibaca": status_notif.get("dibaca", False),
                                "clear": status_notif.get("clear", False),
                                "waktu": tgl_servis,
                                "kode_mesin": kode,
                                "tanggal_servis": tanggal,
                                "jenis_kerusakan": kerusakan
                            })
                    except:
                        pass
        
        notifikasi.sort(key=lambda x: x["waktu"], reverse=True)
        return notifikasi[:15]

    def _format_waktu(self, waktu: datetime) -> str:
        now = datetime.now()
        delta = now - waktu
        if delta.seconds < 60 and delta.days == 0:
            return "Baru saja"
        elif delta.seconds < 3600 and delta.days == 0:
            menit = delta.seconds // 60
            return f"{menit} menit"
        elif delta.days == 0:
            jam = delta.seconds // 3600
            return f"{jam} jam"
        elif delta.days == 1:
            return "Kemarin"
        elif delta.days < 7:
            return f"{delta.days} hari"
        else:
            return waktu.strftime("%d/%m/%Y")

    def _tipe_config(self, tipe: str):
        if tipe == "servis":
            return ("🔧", "#DBEAFE", "#1D4ED8", "Servis")
        else:
            return ("ℹ️", "#DCFCE7", "#16A34A", "Sistem")

    def render(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.show_notifikasi_view()

    def show_notifikasi_view(self):
        self.notifikasi_data = self._get_notifikasi_dari_data()
        
        # ========== STATISTIK RINGKAS (DIPERBESAR) ==========
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 15), padx=5)
        
        for i in range(4):
            stats_row.columnconfigure(i, weight=1)

        total = len(self.notifikasi_data)
        belum_baca = sum(1 for n in self.notifikasi_data if not n.get("dibaca", False))
        belum_clear = sum(1 for n in self.notifikasi_data if not n.get("clear", False))
        sudah_clear = sum(1 for n in self.notifikasi_data if n.get("clear", False))

        # Label lebih pendek agar tidak terpotong
        stats = [
            ("Total", str(total), "#3498DB"),
            ("Belum\nDibaca", str(belum_baca), "#F59E0B"),
            ("Belum\nClear", str(belum_clear), "#E74C3C"),
            ("Sudah\nClear", str(sudah_clear), "#27AE60"),
        ]

        for col_idx, (label, nilai, warna) in enumerate(stats):
            card = ctk.CTkFrame(stats_row, fg_color=warna, corner_radius=8, height=70)
            card.grid(row=0, column=col_idx, padx=(0 if col_idx == 0 else 8, 0), sticky="ew")
            card.grid_propagate(False)
            
            # Nilai
            ctk.CTkLabel(card, text=nilai, font=("Inter", 20, "bold"), text_color="white").place(relx=0.5, rely=0.35, anchor="center")
            # Label (bisa multi-line)
            ctk.CTkLabel(card, text=label, font=("Inter", 10), text_color="white", justify="center").place(relx=0.5, rely=0.7, anchor="center")

        # ========== CARD UTAMA ==========
        main_card = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        main_card.pack(fill="both", expand=True)

        # ========== FILTER TABS ==========
        filter_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        filter_frame.pack(fill="x", padx=15, pady=(10, 8))

        filter_buttons = ctk.CTkFrame(filter_frame, fg_color="transparent")
        filter_buttons.pack(side="left")

        filters = [
            ("semua", "Semua"),
            ("belum_dibaca", "Belum Dibaca"),
            ("belum_clear", "Belum Clear"),
            ("sudah_clear", "Sudah Clear"),
        ]

        for key, label in filters:
            is_active = key == self.active_filter
            btn = ctk.CTkButton(
                filter_buttons,
                text=label,
                font=("Inter", 11, "bold" if is_active else "normal"),
                fg_color="#1E3A5F" if is_active else "#F0F2F5",
                text_color="white" if is_active else "#2C3E50",
                hover_color="#2C5282" if is_active else "#E0E0E0",
                corner_radius=6,
                height=32,
                width=105,
                command=lambda k=key: self._set_filter(k)
            )
            btn.pack(side="left", padx=3)

        ctk.CTkButton(
            filter_frame,
            text="✓ Tandai Semua Dibaca",
            fg_color="transparent",
            text_color="#1E3A5F",
            hover_color="#F0F2F5",
            border_width=1,
            border_color="#1E3A5F",
            font=("Inter", 11, "bold"),
            corner_radius=6,
            height=32,
            width=160,
            command=self._tandai_semua_dibaca
        ).pack(side="right")

        # ========== KONTEN NOTIFIKASI ==========
        content_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        data_tampil = self._filter_data()

        if not data_tampil:
            ctk.CTkLabel(
                content_frame,
                text="🔔\n\nTidak ada notifikasi",
                font=("Inter", 14), text_color="#9CA3AF",
                justify="center"
            ).pack(pady=50)
            return

        scroll_area = ctk.CTkScrollableFrame(content_frame, fg_color="transparent", height=480)
        scroll_area.pack(fill="both", expand=True)

        for notif in data_tampil:
            self._render_notif_item(scroll_area, notif)

    def _render_notif_item(self, parent, notif: dict):
        ikon, badge_bg, badge_fg, label_tipe = self._tipe_config(notif.get("tipe", "sistem"))
        is_unread = not notif.get("dibaca", False)
        is_clear = notif.get("clear", False)

        if is_clear:
            row_bg = "#E8F5E9"
            border_color = "#A5D6A7"
        elif is_unread:
            row_bg = "#F0F7FF"
            border_color = "#90CAF9"
        else:
            row_bg = "#FAFAFA"
            border_color = "#E0E0E0"

        row = ctk.CTkFrame(
            parent,
            fg_color=row_bg,
            corner_radius=8,
            border_width=1,
            border_color=border_color,
            cursor="hand2"
        )
        row.pack(fill="x", pady=(0, 8))
        
        row.bind("<Button-1>", lambda e, n=notif: self.show_detail_notifikasi(n))
        
        content = ctk.CTkFrame(row, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)

        # Baris 1: Status + Judul + Badge + Waktu
        title_row = ctk.CTkFrame(content, fg_color="transparent")
        title_row.pack(fill="x")

        if is_clear:
            status_icon = "✅"
        elif is_unread:
            status_icon = "🔴"
        else:
            status_icon = "📖"
        
        ctk.CTkLabel(title_row, text=status_icon, font=("Inter", 12)).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            title_row,
            text=notif.get("judul", "Notifikasi"),
            font=("Inter", 12, "bold"),
            text_color="#1A2234",
            anchor="w"
        ).pack(side="left")

        badge = ctk.CTkFrame(title_row, fg_color=badge_bg, corner_radius=4)
        badge.pack(side="left", padx=8)
        ctk.CTkLabel(badge, text=label_tipe, font=("Inter", 9, "bold"), text_color=badge_fg, padx=6).pack(pady=1)

        ctk.CTkLabel(
            title_row,
            text=self._format_waktu(notif["waktu"]),
            font=("Inter", 10),
            text_color="#9CA3AF",
            anchor="e"
        ).pack(side="right")

        # Baris 2: Pesan (dipotong lebih pendek agar tidak overflow)
        pesan = notif.get("pesan", "")
        if len(pesan) > 70:
            pesan = pesan[:67] + "..."
        
        ctk.CTkLabel(
            content,
            text=pesan,
            font=("Inter", 10),
            text_color="#6B7280",
            anchor="w",
            wraplength=550,
            justify="left"
        ).pack(fill="x", pady=(5, 0))

        # Baris 3: Tombol aksi
        action_row = ctk.CTkFrame(content, fg_color="transparent")
        action_row.pack(fill="x", pady=(8, 0))

        if is_unread and not is_clear:
            ctk.CTkButton(
                action_row, text="✓ Tandai Dibaca", font=("Inter", 10),
                fg_color="transparent", text_color="#599DEB", hover_color="#EBF4FF",
                border_width=1, border_color="#599DEB", corner_radius=4,
                height=28, width=120,
                command=lambda n=notif: self._tandai_satu_dibaca(n)
            ).pack(side="left", padx=(0, 8))

        if not is_clear:
            ctk.CTkButton(
                action_row, text="✅ Tandai Selesai", font=("Inter", 10),
                fg_color="transparent", text_color="#27AE60", hover_color="#E8F5E9",
                border_width=1, border_color="#27AE60", corner_radius=4,
                height=28, width=120,
                command=lambda n=notif: self._tandai_clear(n)
            ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            action_row, text="🗑️ Hapus", font=("Inter", 10),
            fg_color="transparent", text_color="#E63946", hover_color="#FEE2E2",
            border_width=1, border_color="#E63946", corner_radius=4,
            height=28, width=80,
            command=lambda n=notif: self._hapus_notif(n)
        ).pack(side="left")

    def show_detail_notifikasi(self, notif: dict):
        detail_window = ctk.CTkToplevel(self)
        detail_window.title("Detail Notifikasi")
        detail_window.geometry("550x480")
        detail_window.grab_set()
        detail_window.configure(fg_color="#F0F2F5")
        
        header = ctk.CTkFrame(detail_window, fg_color="white", corner_radius=0, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="📋 Detail Notifikasi", font=("Inter", 15, "bold"), 
                    text_color="#1E3A5F").pack(side="left", padx=15, pady=12)
        ctk.CTkButton(header, text="✕", width=25, height=25, corner_radius=12,
                     fg_color="#F0F2F5", text_color="#7F8C8D", command=detail_window.destroy).pack(side="right", padx=12)
        
        main_frame = ctk.CTkFrame(detail_window, fg_color="white", corner_radius=12)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        is_clear = notif.get("clear", False)
        is_unread = not notif.get("dibaca", False)
        
        status_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=8)
        status_frame.pack(fill="x", padx=12, pady=(10, 8))
        
        if is_clear:
            status_text = "✅ STATUS: SELESAI"
            status_color = "#27AE60"
        elif is_unread:
            status_text = "🔴 STATUS: BELUM DIBACA"
            status_color = "#E74C3C"
        else:
            status_text = "📖 STATUS: SUDAH DIBACA"
            status_color = "#7F8C8D"
        
        ctk.CTkLabel(status_frame, text=status_text, font=("Inter", 12, "bold"), 
                    text_color=status_color).pack(pady=8)
        
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=12, pady=8)
        
        details = [
            ("Judul", notif.get("judul", "-")),
            ("Pesan", notif.get("pesan", "-")),
            ("Tipe", notif.get("tipe", "-").capitalize()),
            ("Waktu", self._format_waktu(notif.get("waktu", datetime.now()))),
        ]
        
        if notif.get("kode_mesin"):
            details.append(("Kode Mesin", notif.get("kode_mesin", "-")))
        if notif.get("nama_mesin"):
            details.append(("Nama Mesin", notif.get("nama_mesin", "-")))
        if notif.get("interval"):
            details.append(("Interval Servis", f"{notif.get('interval')} hari"))
        if notif.get("tanggal_servis"):
            details.append(("Tanggal Servis", notif.get("tanggal_servis", "-")))
        
        for label, value in details:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f"{label}:", font=("Inter", 11, "bold"), 
                        width=110, anchor="w", text_color="#2C3E50").pack(side="left")
            ctk.CTkLabel(row, text=value, font=("Inter", 11), 
                        text_color="#7F8C8D", anchor="w", wraplength=350).pack(side="left", padx=(8, 0))
        
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=12, pady=(8, 10))
        
        if not is_clear:
            ctk.CTkButton(
                action_frame, text="✅ Tandai Selesai",
                command=lambda: self._tandai_clear_dari_detail(notif, detail_window),
                fg_color="#27AE60", height=35, font=("Inter", 11, "bold")
            ).pack(side="left", padx=(0, 8), fill="x", expand=True)
        
        ctk.CTkButton(
            action_frame, text="🗑️ Hapus Notifikasi",
            command=lambda: self._hapus_notif_dari_detail(notif, detail_window),
            fg_color="#E74C3C", height=35, font=("Inter", 11, "bold")
        ).pack(side="left", fill="x", expand=True)
        
        if not notif.get("dibaca", False):
            notif["dibaca"] = True
            self._update_status_in_memory(notif)
            self.render()

    def _update_status_in_memory(self, notif: dict):
        notif_id = notif.get("id")
        self.status_notifikasi[notif_id] = {
            "dibaca": notif.get("dibaca", False),
            "clear": notif.get("clear", False)
        }

    def _set_filter(self, key: str):
        self.active_filter = key
        self.render()

    def _filter_data(self):
        if self.active_filter == "semua":
            return self.notifikasi_data
        elif self.active_filter == "belum_dibaca":
            return [n for n in self.notifikasi_data if not n.get("dibaca", False)]
        elif self.active_filter == "belum_clear":
            return [n for n in self.notifikasi_data if not n.get("clear", False)]
        elif self.active_filter == "sudah_clear":
            return [n for n in self.notifikasi_data if n.get("clear", False)]
        else:
            return [n for n in self.notifikasi_data if n.get("tipe") == self.active_filter]

    def _tandai_satu_dibaca(self, notif: dict):
        for n in self.notifikasi_data:
            if n.get("id") == notif.get("id"):
                n["dibaca"] = True
                self._update_status_in_memory(n)
                break
        self.render()

    def _tandai_semua_dibaca(self):
        for n in self.notifikasi_data:
            n["dibaca"] = True
            self._update_status_in_memory(n)
        self.render()

    def _tandai_clear(self, notif: dict):
        for n in self.notifikasi_data:
            if n.get("id") == notif.get("id"):
                n["clear"] = True
                n["dibaca"] = True
                self._update_status_in_memory(n)
                break
        self.render()
    
    def _tandai_clear_dari_detail(self, notif: dict, window):
        for n in self.notifikasi_data:
            if n.get("id") == notif.get("id"):
                n["clear"] = True
                n["dibaca"] = True
                self._update_status_in_memory(n)
                break
        window.destroy()
        self.render()

    def _hapus_notif(self, notif: dict):
        self.notifikasi_data = [n for n in self.notifikasi_data if n.get("id") != notif.get("id")]
        if notif.get("id") in self.status_notifikasi:
            del self.status_notifikasi[notif.get("id")]
        self.render()
    
    def _hapus_notif_dari_detail(self, notif: dict, window):
        self._hapus_notif(notif)
        window.destroy()