import pandas as pd
import os

# Hapus file lama jika ada
files_to_remove = ['mesin.csv', 'servis.csv', 'users.csv']
for f in files_to_remove:
    if os.path.exists(f):
        os.remove(f)
        print(f"✅ {f} dihapus")

# Buat users.csv
users_data = pd.DataFrame([{
    'username': 'admin', 
    'password': 'admin123', 
    'role': 'admin', 
    'perusahaan': 'MAINTORA',
    'email': 'admin@maintora.com',
    'telepon': '+62 812-3456-7890',
    'departemen': 'Teknik Pemeliharaan',
    'nama_lengkap': 'Admin MAINTORA'
}])
users_data.to_csv('users.csv', index=False)
print("✅ users.csv dibuat")

# Buat mesin.csv dengan data bersih
mesin_data = [
    ['M001', 'Mesin Rotary Packaging', 'Packaging', 'PT Pangan Makmur', 'Aktif', 62, 'Gudang A', '1950', '2022-01-10'],
    ['M002', 'Automatic Labeling Machine', 'Packaging', 'PT Pangan Makmur', 'Aktif', 31, 'Line 2', '2100', '2022-02-15'],
    ['M003', 'Plastic Extrusion Machine', 'Plastic', 'PT Baja Presisi', 'Aktif', 125, 'Workshop', '3200', '2021-06-20'],
    ['M004', 'Main Belt Conveyor', 'Logistics', 'PT Pangan Makmur', 'Aktif', 187, 'Warehouse', '4500', '2020-12-01'],
    ['M005', 'Industrial Ribbon Blender', 'Food & Beverage', 'PT Pangan Makmur', 'Aktif', 62, 'Production', '1800', '2022-08-15'],
    ['M006', 'Liquid Filling Machine', 'Packaging', 'PT Pangan Makmur', 'Aktif', 50, 'Line 1', '1600', '2022-03-10'],
    ['M007', 'Robotic Palletizer', 'Logistics', 'PT Baja Presisi', 'Aktif', 93, 'Loading Bay', '2500', '2021-09-05'],
    ['M008', 'Industrial Steam Boiler', 'Utilities', 'PT Pangan Makmur', 'Aktif', 250, 'Utility Room', '5000', '2019-11-20'],
    ['M009', 'Rotary Screw Air Compressor', 'Utilities', 'PT Baja Presisi', 'Aktif', 125, 'Compressor Room', '3800', '2020-08-12'],
    ['M010', 'Hydraulic Stamping Press', 'Metalworking', 'PT Baja Presisi', 'Aktif', 156, 'Workshop', '2900', '2021-03-18'],
]

mesin_columns = ['kode_mesin', 'nama_mesin', 'kategori', 'perusahaan', 'status', 'interval_servis_hari', 'lokasi', 'jam_operasi', 'tgl_instalasi']
mesin_df = pd.DataFrame(mesin_data, columns=mesin_columns)
mesin_df.to_csv('mesin.csv', index=False)
print(f"✅ mesin.csv dibuat dengan {len(mesin_df)} data")

# Buat servis.csv kosong
servis_df = pd.DataFrame(columns=['kode_mesin', 'jenis_kerusakan', 'teknisi', 'biaya', 'suhu_mesin', 'catatan', 'tanggal_perbaikan', 'tanggal_perbaikan_selanjutnya'])
servis_df.to_csv('servis.csv', index=False)
print("✅ servis.csv dibuat")

print("\n" + "="*50)
print("✅ SEMUA DATA BERHASIL DI RESET!")
print("="*50)
print("\nLogin dengan:")
print("   Username: admin")
print("   Password: admin123")