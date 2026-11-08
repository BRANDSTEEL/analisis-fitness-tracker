import sqlite3
import random
from datetime import datetime, timedelta
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. SETUP DATABASE & GENERATE 2000 BARIS DATA
# ==========================================
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS pengguna (
        id_pengguna INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_pengguna TEXT,
        gender TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS log_aktivitas (
        id_log INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pengguna INTEGER,
        tanggal TEXT,
        jenis_aktivitas TEXT,
        langkah_harian INTEGER,
        kalori_terbakar REAL,
        durasi_tidur_jam REAL,
        detak_jantung_rata REAL,
        FOREIGN KEY(id_pengguna) REFERENCES pengguna(id_pengguna)
    )
''')

users = [
    ("Maya", "Wanita"), ("Eko", "Pria"), ("Ahmad", "Pria"), ("Rina", "Wanita"), ("Joko", "Pria"),
    ("Dewi", "Wanita"), ("Andi", "Pria"), ("Siti", "Wanita"), ("Budi", "Pria"), ("Dixon", "Pria")
]
cursor.executemany("INSERT OR IGNORE INTO pengguna (nama_pengguna, gender) VALUES (?, ?)", users)
conn.commit()

# Cek apakah log_aktivitas sudah ada 2000 baris
cursor.execute("SELECT COUNT(*) FROM log_aktivitas;")
count = cursor.fetchone()[0]

if count < 2000:
    cursor.execute("DELETE FROM log_aktivitas;")
    conn.commit()
    
    aktivitas_list = [
        ("Lari (Running)", 5000, 12000, 300, 600, 6.0, 8.0, 120, 160),
        ("Bersepeda (Cycling)", 4000, 15000, 250, 500, 6.0, 8.0, 110, 150),
        ("Berenang (Swimming)", 2000, 6000, 200, 450, 6.0, 8.0, 115, 155),
        ("Latihan Beban (Gym)", 3000, 8000, 180, 400, 6.0, 8.0, 105, 145),
        ("Jalan Santai (Walking)", 6000, 10000, 150, 300, 6.0, 8.0, 90, 130)
    ]

    start_date = datetime(2025, 1, 1)
    data_to_insert = []

    for _ in range(2000):
        user_id = random.randint(1, 10)
        random_days = random.randint(0, 364)
        tanggal = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        akt = random.choice(aktivitas_list)
        jenis_aktivitas = akt[0]
        langkah = random.randint(akt[1], akt[2])
        kalori = round(random.uniform(akt[3], akt[4]), 2)
        durasi_tidur = round(random.uniform(akt[5], akt[6]), 1)
        detak_jantung = round(random.uniform(akt[7], akt[8]), 1)
        
        data_to_insert.append((user_id, tanggal, jenis_aktivitas, langkah, kalori, durasi_tidur, detak_jantung))

    cursor.executemany('''
        INSERT INTO log_aktivitas (id_pengguna, tanggal, jenis_aktivitas, langkah_harian, kalori_terbakar, durasi_tidur_jam, detak_jantung_rata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', data_to_insert)
    conn.commit()

# Ambil data ke pandas DataFrame
df_log = pd.read_sql("SELECT * FROM log_aktivitas", conn)
df_pengguna = pd.read_sql("SELECT * FROM pengguna", conn)
conn.close()

df = pd.merge(df_log, df_pengguna, on='id_pengguna')


# ==========================================
# 2. GENERATE GAMBAR GRAFIK (MATPLOTLIB)
# ==========================================
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

# Grafik 1: Rata-rata Kalori per Aktivitas
plt.figure(figsize=(10, 6))
df1 = df.groupby('jenis_aktivitas')['kalori_terbakar'].mean().sort_values(ascending=False).reset_index()
sns.barplot(data=df1, x='jenis_aktivitas', y='kalori_terbakar', palette='viridis', errorbar=None)
plt.title('Rata-rata Kalori Terbakar Berdasarkan Jenis Aktivitas', fontsize=14, fontweight='bold')
plt.xlabel('Jenis Aktivitas', fontsize=12)
plt.ylabel('Rata-rata Kalori (kcal)', fontsize=12)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig('chart1_kalori_aktivitas.png', dpi=300)
plt.close()

# Grafik 2: Hubungan Langkah & Kalori
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='langkah_harian', y='kalori_terbakar', hue='jenis_aktivitas', palette='deep', alpha=0.7)
plt.title('Hubungan antara Langkah Harian dan Kalori Terbakar', fontsize=14, fontweight='bold')
plt.xlabel('Langkah Harian', fontsize=12)
plt.ylabel('Kalori Terbakar (kcal)', fontsize=12)
plt.legend(title='Jenis Aktivitas', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('chart2_langkah_kalori.png', dpi=300)
plt.close()

# Grafik 3: Tidur & Detak Jantung per Pengguna
user_summary = df.groupby('nama_pengguna')[['durasi_tidur_jam', 'detak_jantung_rata']].mean().reset_index()
fig, ax1 = plt.subplots(figsize=(12, 6))
color = 'tab:blue'
ax1.set_xlabel('Nama Pengguna', fontsize=12)
ax1.set_ylabel('Rata-rata Durasi Tidur (Jam)', color=color, fontsize=12)
sns.barplot(data=user_summary, x='nama_pengguna', y='durasi_tidur_jam', ax=ax1, color='lightblue', alpha=0.8)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('Rata-rata Detak Jantung (bpm)', color=color, fontsize=12)
sns.lineplot(data=user_summary, x='nama_pengguna', y='detak_jantung_rata', ax=ax2, color='red', marker='o', linewidth=2.5)
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Rata-rata Durasi Tidur dan Detak Jantung per Pengguna', fontsize=14, fontweight='bold')
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig('chart3_tidur_detak_jantung.png', dpi=300)
plt.close()


# ==========================================
# 3. GENERATE EXCEL BERSIH (HANYA TABEL 3 SHEET)
# ==========================================
wb = openpyxl.Workbook()
wb.remove(wb.active)

font_title = Font(name='Segoe UI', size=14, bold=True, color='1F4E79')
font_header = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
fill_header = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
fill_zebra = PatternFill(start_color='F2F5F9', end_color='F2F5F9', fill_type='solid')
font_body = Font(name='Segoe UI', size=10)
thin_border = Border(left=Side(style='thin', color='D9D9D9'), right=Side(style='thin', color='D9D9D9'), top=Side(style='thin', color='D9D9D9'), bottom=Side(style='thin', color='D9D9D9'))

# Sheet 1: Kalori per Aktivitas
ws1 = wb.create_sheet(title="Kalori per Aktivitas")
ws1.views.sheetView[0].showGridLines = True
df_s1 = df.groupby('jenis_aktivitas').agg(
    total_sesi=('id_log', 'count'),
    total_kalori=('kalori_terbakar', 'sum'),
    rata_kalori=('kalori_terbakar', 'mean'),
    max_kalori=('kalori_terbakar', 'max')
).reset_index().sort_values(by='rata_kalori', ascending=False)

ws1['A1'] = "RINGKASAN KALORI TERBAKAR BERDASARKAN JENIS AKTIVITAS"
ws1['A1'].font = font_title
headers1 = ["Jenis Aktivitas", "Total Sesi", "Total Kalori (kcal)", "Rata-rata Kalori (kcal)", "Maksimum Kalori (kcal)"]
ws1.append([])
ws1.append(headers1)
for col_num, header in enumerate(headers1, 1):
    cell = ws1.cell(row=3, column=col_num)
    cell.font, cell.fill, cell.alignment, cell.border = font_header, fill_header, Alignment(horizontal='center', vertical='center'), thin_border
for r_idx, row in df_s1.reset_index(drop=True).iterrows():
    r_num = 4 + r_idx
    ws1.cell(row=r_num, column=1, value=row['jenis_aktivitas']).alignment = Alignment(horizontal='left')
    ws1.cell(row=r_num, column=2, value=int(row['total_sesi'])).number_format = '#,##0'
    ws1.cell(row=r_num, column=3, value=float(row['total_kalori'])).number_format = '#,##0.0'
    ws1.cell(row=r_num, column=4, value=float(row['rata_kalori'])).number_format = '#,##0.0'
    ws1.cell(row=r_num, column=5, value=float(row['max_kalori'])).number_format = '#,##0.0'
    for c_num in range(1, 6):
        c = ws1.cell(row=r_num, column=c_num)
        c.font, c.border = font_body, thin_border
        if r_idx % 2 == 1: c.fill = fill_zebra

# Sheet 2: Langkah & Kalori
ws2 = wb.create_sheet(title="Langkah & Kalori")
ws2.views.sheetView[0].showGridLines = True
df['kategori_langkah'] = pd.cut(df['langkah_harian'], bins=[0, 5000, 10000, 15000, 20000], labels=['< 5.000 (Rendah)', '5.001 - 10.000 (Sedang)', '10.001 - 15.000 (Tinggi)', '> 15.000 (Sangat Tinggi)'])
df_s2 = df.groupby('kategori_langkah', observed=False).agg(
    jumlah_catatan=('id_log', 'count'),
    rata_langkah=('langkah_harian', 'mean'),
    rata_kalori=('kalori_terbakar', 'mean'),
    min_kalori=('kalori_terbakar', 'min'),
    max_kalori=('kalori_terbakar', 'max')
).reset_index()

ws2['A1'] = "HUBUNGAN LANGKAH HARIAN DAN KALORI TERBAKAR"
ws2['A1'].font = font_title
headers2 = ["Kategori Langkah", "Jumlah Catatan", "Rata-rata Langkah", "Rata-rata Kalori (kcal)", "Min Kalori (kcal)", "Max Kalori (kcal)"]
ws2.append([])
ws2.append(headers2)
for col_num, header in enumerate(headers2, 1):
    cell = ws2.cell(row=3, column=col_num)
    cell.font, cell.fill, cell.alignment, cell.border = font_header, fill_header, Alignment(horizontal='center', vertical='center'), thin_border
for r_idx, row in df_s2.reset_index(drop=True).iterrows():
    r_num = 4 + r_idx
    ws2.cell(row=r_num, column=1, value=str(row['kategori_langkah'])).alignment = Alignment(horizontal='left')
    ws2.cell(row=r_num, column=2, value=int(row['jumlah_catatan'])).number_format = '#,##0'
    ws2.cell(row=r_num, column=3, value=float(row['rata_langkah'])).number_format = '#,##0'
    ws2.cell(row=r_num, column=4, value=float(row['rata_kalori'])).number_format = '#,##0.0'
    ws2.cell(row=r_num, column=5, value=float(row['min_kalori'])).number_format = '#,##0.0'
    ws2.cell(row=r_num, column=6, value=float(row['max_kalori'])).number_format = '#,##0.0'
    for c_num in range(1, 7):
        c = ws2.cell(row=r_num, column=c_num)
        c.font, c.border = font_body, thin_border
        if r_idx % 2 == 1: c.fill = fill_zebra

# Sheet 3: Tidur & Detak Jantung
ws3 = wb.create_sheet(title="Tidur & Detak Jantung")
ws3.views.sheetView[0].showGridLines = True
df_s3 = df.groupby(['nama_pengguna', 'gender']).agg(
    total_aktivitas=('id_log', 'count'),
    rata_tidur=('durasi_tidur_jam', 'mean'),
    rata_detak_jantung=('detak_jantung_rata', 'mean'),
    max_detak_jantung=('detak_jantung_rata', 'max')
).reset_index()

ws3['A1'] = "RATA-RATA DURASI TIDUR DAN DETAK JANTUNG PER PENGGUNA"
ws3['A1'].font = font_title
headers3 = ["Nama Pengguna", "Gender", "Total Aktivitas", "Rata-rata Tidur (Jam)", "Rata-rata Detak Jantung (bpm)", "Max Detak Jantung (bpm)"]
ws3.append([])
ws3.append(headers3)
for col_num, header in enumerate(headers3, 1):
    cell = ws3.cell(row=3, column=col_num)
    cell.font, cell.fill, cell.alignment, cell.border = font_header, fill_header, Alignment(horizontal='center', vertical='center'), thin_border
for r_idx, row in df_s3.reset_index(drop=True).iterrows():
    r_num = 4 + r_idx
    ws3.cell(row=r_num, column=1, value=row['nama_pengguna']).alignment = Alignment(horizontal='left')
    ws3.cell(row=r_num, column=2, value=row['gender']).alignment = Alignment(horizontal='center')
    ws3.cell(row=r_num, column=3, value=int(row['total_aktivitas'])).number_format = '#,##0'
    ws3.cell(row=r_num, column=4, value=float(row['rata_tidur'])).number_format = '#,##0.0'
    ws3.cell(row=r_num, column=5, value=float(row['rata_detak_jantung'])).number_format = '#,##0.0'
    ws3.cell(row=r_num, column=6, value=float(row['max_detak_jantung'])).number_format = '#,##0.0'
    for c_num in range(1, 7):
        c = ws3.cell(row=r_num, column=c_num)
        c.font, c.border = font_body, thin_border
        if r_idx % 2 == 1: c.fill = fill_zebra

# Auto-fit kolom
for ws in [ws1, ws2, ws3]:
    for col in ws.columns:
        max_len = max([len(str(cell.value or '')) for cell in col if cell.row >= 3] + [0])
        ws.column_dimensions[col[0].column_letter].width = max(max_len + 4, 16)

wb.save("Analisis_Fitness_Tracker_2000_Baris_Bersih.xlsx")
print("Sukses! Database, gambar grafik, dan file Excel bersih berhasil dibuat.")