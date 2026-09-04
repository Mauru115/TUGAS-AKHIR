import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# IMPLEMENTASI ENCAPSULATION & INHERITANCE
# ==========================================
class Pengguna:
    def __init__(self, username, role, perusahaan=None, telp="-", email="-", alamat="-", pic="-"):
        self.__username = username
        self.__role = role
        self._perusahaan = perusahaan
        self._telp = telp
        self._email = email
        self._alamat = alamat
        self._pic = pic

    @property
    def username(self):
        return self.__username

    @property
    def role(self):
        return self.__role
    
    @property
    def perusahaan(self):
        return self._perusahaan
    
    @property
    def telp(self):
        return self._telp
    
    @property
    def email(self):
        return self._email
    
    @property
    def alamat(self):
        return self._alamat
    
    @property
    def pic(self):
        return self._pic

class Admin(Pengguna):
    def __init__(self, username, perusahaan="admin"):
        super().__init__(username, "admin", perusahaan)
        self.can_crud = True

class Pelanggan(Pengguna):
    def __init__(self, username, nama_perusahaan, telp="-", email="-", alamat="-", pic="-"):
        super().__init__(username, "pelanggan", nama_perusahaan, telp, email, alamat, pic)
        self.can_crud = False

# ==========================================
# DATA MANAGER (BACKEND & DATABASE CSV)
# ==========================================
class DataManager:
    def __init__(self):
        self.users_file = os.path.join(BASE_DIR, 'users.csv')
        self.mesin_file = os.path.join(BASE_DIR, 'mesin.csv')
        self.servis_file = os.path.join(BASE_DIR, 'servis.csv')
        self._init_files()

    def _init_files(self):
        try:
            if not os.path.exists(self.users_file):
                default_admin = pd.DataFrame([{
                    'username': 'admin', 
                    'password': 'admin123', 
                    'role': 'admin', 
                    'perusahaan': 'MAINTORA',
                    'telp': '-', 
                    'email': 'admin@maintora.com', 
                    'alamat': '-', 
                    'pic': '-'
                }])
                default_admin.to_csv(self.users_file, index=False)
            
            if not os.path.exists(self.mesin_file):
                df = pd.DataFrame(columns=['kode_mesin', 'nama_mesin', 'kategori', 'perusahaan', 'status', 'interval_servis_hari', 'lokasi', 'jam_operasi', 'tgl_instalasi'])
                df.to_csv(self.mesin_file, index=False)
            
            if not os.path.exists(self.servis_file):
                df = pd.DataFrame(columns=['kode_mesin', 'jenis_kerusakan', 'teknisi', 'biaya', 'suhu_mesin', 'catatan', 'tanggal_perbaikan', 'tanggal_perbaikan_selanjutnya'])
                df.to_csv(self.servis_file, index=False)
        except Exception as e:
            print(f"Error inisialisasi file: {e}")

    def login(self, username, password):
        try:
            df = pd.read_csv(self.users_file)
            user = df[(df['username'] == username) & (df['password'] == password)]
            if not user.empty:
                role = user.iloc[0]['role']
                perusahaan = user.iloc[0].get('perusahaan', '')
                telp = user.iloc[0].get('telp', '-')
                email = user.iloc[0].get('email', '-')
                alamat = user.iloc[0].get('alamat', '-')
                pic = user.iloc[0].get('pic', '-')
                
                if role == 'admin':
                    return Admin(username, perusahaan)
                else:
                    return Pelanggan(username, perusahaan, telp, email, alamat, pic)
            return None
        except Exception as e:
            print(f"Login error: {e}")
            return None

    # ========== GET DATA DENGAN FILTER USER ==========
    def get_data_mesin(self, user=None):
        """Ambil data mesin - filter jika user adalah pelanggan"""
        try:
            df = pd.read_csv(self.mesin_file, dtype=str)
            df = df.fillna('')
            
            # Filter jika user adalah pelanggan
            if user and hasattr(user, 'role') and user.role == 'pelanggan':
                if user.perusahaan and user.perusahaan != 'MAINTORA':
                    df = df[df['perusahaan'] == user.perusahaan]
            
            return df
        except Exception as e:
            print(f"Error baca mesin: {e}")
            return pd.DataFrame()
    
    def get_data_servis(self, user=None):
        """Ambil data servis - filter berdasarkan mesin milik perusahaan user"""
        try:
            df_servis = pd.read_csv(self.servis_file, dtype=str)
            df_servis = df_servis.fillna('')
            
            # Filter jika user adalah pelanggan
            if user and hasattr(user, 'role') and user.role == 'pelanggan':
                if user.perusahaan and user.perusahaan != 'MAINTORA':
                    df_mesin = self.get_data_mesin(user)
                    mesin_kodes = df_mesin['kode_mesin'].tolist() if not df_mesin.empty else []
                    df_servis = df_servis[df_servis['kode_mesin'].isin(mesin_kodes)]
            
            return df_servis
        except Exception as e:
            print(f"Error baca servis: {e}")
            return pd.DataFrame()

    def get_data_by_perusahaan(self, perusahaan):
        df = self.get_data_mesin()
        if df.empty or perusahaan == 'admin':
            return df
        return df[df['perusahaan'] == perusahaan]

    def get_data_servis_by_perusahaan(self, perusahaan):
        try:
            df_servis = self.get_data_servis()
            if df_servis.empty or perusahaan == 'admin':
                return df_servis
                
            df_mesin = self.get_data_mesin()
            if df_mesin.empty:
                return pd.DataFrame(columns=df_servis.columns)
                
            df_mesin_filtered = df_mesin[df_mesin['perusahaan'] == perusahaan][['kode_mesin']]
            df_filtered = pd.merge(df_servis, df_mesin_filtered, on='kode_mesin', how='inner')
            return df_filtered
        except Exception as e:
            print(f"Error filter servis per perusahaan: {e}")
            return pd.DataFrame()

    # ========== EXPORT SYSTEM ==========
    def export_excel(self, df, filename):
        try:
            export_path = os.path.join(BASE_DIR, f"{filename}.xlsx")
            df.to_excel(export_path, index=False)
            return True
        except Exception as e:
            print(f"Export Excel error: {e}")
            return False

    def export_pdf(self, df, filename):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.cell(200, 10, txt="Laporan MAIN TRACK", ln=True, align='C')
            for i, row in df.iterrows():
                row_text = " | ".join([f"{str(val)}" for val in row.values])
                pdf.cell(200, 8, txt=row_text[:90], ln=True)
            export_path = os.path.join(BASE_DIR, f"{filename}.pdf")
            pdf.output(export_path)
            return True
        except Exception as e:
            print(f"Export PDF error: {e}")
            return False

    # ========== OPERASIONAL DATA MESIN (CRUD) ==========
    def tambah_mesin(self, data):
        try:
            df = pd.read_csv(self.mesin_file)
            if str(data['kode_mesin']) in df['kode_mesin'].astype(str).values:
                return False, "Kode mesin sudah terdaftar!"
            
            new_row = {}
            for col in df.columns:
                if col in data:
                    val = data[col]
                    if col == 'interval_servis_hari':
                        try:
                            new_row[col] = int(float(val)) if val and str(val).strip() else 0
                        except:
                            new_row[col] = 0
                    elif col == 'jam_operasi':
                        try:
                            new_row[col] = str(int(float(val))) if val and str(val).strip() else ''
                        except:
                            new_row[col] = ''
                    else:
                        new_row[col] = str(val) if val else ''
                else:
                    new_row[col] = '' if col not in ['interval_servis_hari'] else 0
            
            new_df = pd.DataFrame([new_row])
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(self.mesin_file, index=False)
            return True, "Data mesin berhasil ditambahkan!"
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"

    def update_mesin(self, kode, data_update):
        try:
            df = pd.read_csv(self.mesin_file)
            df['kode_mesin'] = df['kode_mesin'].astype(str)
            
            if str(kode) not in df['kode_mesin'].values:
                return False, "Data mesin tidak ditemukan!"
            
            for col, val in data_update.items():
                if col not in df.columns:
                    df[col] = ''
                
                if col == 'interval_servis_hari':
                    try:
                        val = int(float(val)) if val and str(val).strip() else 0
                    except:
                        val = 0
                elif col == 'jam_operasi':
                    try:
                        val = str(int(float(val))) if val and str(val).strip() else ''
                    except:
                        val = ''
                else:
                    val = str(val) if val else ''
                
                df.loc[df['kode_mesin'] == str(kode), col] = val
            
            df.to_csv(self.mesin_file, index=False)
            return True, "Data mesin berhasil diperbarui!"
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"

    def hapus_mesin(self, kode):
        try:
            df = pd.read_csv(self.mesin_file)
            df['kode_mesin'] = df['kode_mesin'].astype(str)
            if str(kode) not in df['kode_mesin'].values:
                return False, "Data mesin tidak ditemukan!"
            df = df[df['kode_mesin'] != str(kode)]
            df.to_csv(self.mesin_file, index=False)
            return True, "Data mesin berhasil dihapus!"
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"

    # ========== OPERASIONAL DATA SERVIS ==========
    def tambah_servis(self, data):
        try:
            df = pd.read_csv(self.servis_file)
            new_row = pd.DataFrame([data])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(self.servis_file, index=False)
            return True, "Riwayat servis berhasil ditambahkan!"
        except Exception as e:
            return False, f"Terjadi kesalahan: {e}"