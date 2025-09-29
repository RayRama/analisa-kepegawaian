# 📊 Analisis Kepegawaian - Treemap Visualization

Aplikasi Streamlit untuk analisis data kepegawaian dengan visualisasi treemap interaktif yang menampilkan hierarki OPD → Eselon → Jabatan → Golongan.

## 🚀 Fitur

- **Upload Data**: Support file CSV dan Excel (.xlsx)
- **Visualisasi Treemap**: 3 jenis treemap untuk analisis yang komprehensif
  - OPD → Eselon
  - OPD → Eselon → Jabatan
  - OPD → Golongan
- **Filter Interaktif**: Filter berdasarkan Eselon, OPD, dan Golongan
- **Audit Data**: Ringkasan distribusi data untuk validasi
- **Export Data**: Download data yang sudah difilter dan tabel pivot
- **Tabel Pivot**: Ringkasan OPD × Golongan

## 📋 Struktur Data CSV yang Diperlukan

File CSV/Excel harus memiliki kolom-kolom berikut:

| Kolom               | Deskripsi             | Contoh                     |
| ------------------- | --------------------- | -------------------------- |
| `peg_nip`           | NIP Pegawai           | 196512011990031001         |
| `peg_nama`          | Nama Pegawai          | Dr. John Doe, S.H., M.H.   |
| `satuan_kerja_nama` | Nama OPD/Satuan Kerja | Dinas Pendidikan           |
| `golongan`          | Golongan Pegawai      | IV/a, III/b, II/c          |
| `jabatan_nama`      | Nama Jabatan          | Kepala Dinas, Sekretaris   |
| `jabatan_jenis`     | Jenis Jabatan         | Struktural, Fungsional     |
| `eselon`            | Eselon Jabatan        | I, II, III, IV, NON-ESELON |

### Contoh Data CSV:

```csv
peg_nip,peg_nama,satuan_kerja_nama,golongan,jabatan_nama,jabatan_jenis,eselon
196512011990031001,Dr. John Doe S.H. M.H.,Dinas Pendidikan,IV/a,Kepala Dinas,Struktural,II
197003151995032002,Dra. Jane Smith M.Pd.,Dinas Kesehatan,III/b,Sekretaris,Struktural,III
198205201998031003,Budi Santoso S.T.,Dinas PU,II/c,Analis Kepegawaian,Fungsional,NON-ESELON
```

## 🛠️ Instalasi

1. **Clone atau download project ini**

2. **Install dependensi:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi:**

   ```bash
   streamlit run app.py
   ```

4. **Buka browser** dan akses `http://localhost:8501`

## 📁 Struktur Project

```
analisa-kepegawaian/
├── app.py                 # Aplikasi Streamlit utama
├── klasifikasi_eselon.py  # Script klasifikasi eselon otomatis
├── requirements.txt       # Dependensi Python
├── README.md             # Dokumentasi ini
└── rekap_with_eselon.csv # Contoh data (opsional)
```

## 🔧 Dependensi

- **streamlit** - Framework web app
- **pandas** - Manipulasi data
- **plotly** - Visualisasi interaktif
- **openpyxl** - Support file Excel
- **numpy** - Operasi numerik

## 📊 Cara Penggunaan

### Opsi 1: Data Sudah Ada Kolom Eselon

1. **Upload Data**: Pilih file CSV/Excel yang berisi data kepegawaian dengan kolom eselon
2. **Validasi Kolom**: Pastikan semua kolom yang diperlukan tersedia
3. **Filter Data**: Gunakan dropdown dan multiselect untuk memfilter data
4. **Analisis Visual**: Lihat 3 jenis treemap untuk analisis yang berbeda
5. **Export Hasil**: Download data yang sudah difilter atau tabel pivot

### Opsi 2: Data Belum Ada Kolom Eselon (Menggunakan Klasifikasi Otomatis)

1. **Siapkan Data**: Pastikan file CSV/Excel memiliki kolom `jabatan_nama` dan `jabatan_jenis`
2. **Jalankan Klasifikasi**:
   ```bash
   python klasifikasi_eselon.py
   ```
3. **Edit Konfigurasi**: Sesuaikan nama file di `klasifikasi_eselon.py`:
   ```python
   PATH_XLSX = "nama_file_anda.xlsx"  # atau
   PATH_CSV = "nama_file_anda.csv"
   ```
4. **Hasil**: File `rekap_with_eselon.csv` akan dibuat dengan kolom eselon yang sudah diklasifikasi
5. **Gunakan di App**: Upload file hasil ke aplikasi Streamlit untuk analisis

## 🤖 Klasifikasi Eselon Otomatis

Script `klasifikasi_eselon.py` membantu mengklasifikasi eselon jabatan secara otomatis berdasarkan nama jabatan dan jenis jabatan.

### Fitur Klasifikasi:

- **Eselon II**: Kepala Dinas, Kepala Badan, Sekda, Inspektur, Direktur, Staf Ahli
- **Eselon III**: Kepala Bidang, Camat, Kabag, Sekretaris Dinas/Badan
- **Eselon IV**: Kepala Seksi, Kasubag, Kasubbid, Lurah, Kaur
- **Non-Eselon**: Jabatan Fungsional dan jabatan lainnya

### Cara Kerja:

1. Membaca file Excel/CSV dengan kolom `jabatan_nama` dan `jabatan_jenis`
2. Menganalisis nama jabatan menggunakan pattern matching
3. Mengklasifikasi berdasarkan kata kunci jabatan struktural
4. Menandai jabatan fungsional sebagai Non-Eselon
5. Menghasilkan file CSV dengan kolom `eselon` dan `eselon_reason`

### Output:

- File `rekap_with_eselon.csv` dengan kolom tambahan:
  - `eselon`: Hasil klasifikasi (I, II, III, IV, III/IV, Non-Eselon)
  - `eselon_reason`: Alasan klasifikasi (match:keyword, fungsional, ambiguous_structural, dll)

## 📈 Jenis Analisis

### 1. Treemap OPD → Eselon

Menampilkan distribusi pegawai berdasarkan OPD dan eselon jabatan.

### 2. Treemap OPD → Eselon → Jabatan

Analisis detail dengan hierarki lengkap sampai level jabatan.

### 3. Treemap OPD → Golongan

Distribusi pegawai berdasarkan OPD dan golongan pangkat.

### 4. Tabel Pivot OPD × Golongan

Ringkasan dalam format tabel untuk analisis kuantitatif.

## ⚠️ Catatan Penting

- **Format Data**: Pastikan data CSV menggunakan encoding UTF-8
- **Kolom Wajib**: Semua kolom yang disebutkan di atas harus ada dalam file
- **Data Kosong**: Aplikasi akan menangani data kosong dengan label "Tidak Diketahui"
- **Ukuran File**: Untuk performa optimal, gunakan file dengan maksimal 50,000 baris
- **Klasifikasi Eselon**: Jika data belum ada kolom eselon, gunakan `klasifikasi_eselon.py` terlebih dahulu
- **Validasi Hasil**: Periksa hasil klasifikasi eselon sebelum menggunakan di aplikasi utama

## 🐛 Troubleshooting

**Error "Kolom tidak ditemukan":**

- Pastikan nama kolom sesuai dengan yang disebutkan di dokumentasi
- Periksa apakah ada spasi ekstra di nama kolom

**File tidak bisa dibuka:**

- Pastikan file dalam format CSV atau Excel (.xlsx)
- Periksa encoding file (gunakan UTF-8)

**Aplikasi lambat:**

- Kurangi ukuran data dengan filter yang lebih spesifik
- Pertimbangkan untuk membagi data menjadi file yang lebih kecil

**Klasifikasi eselon tidak akurat:**

- Periksa format nama jabatan dalam data (pastikan konsisten)
- Sesuaikan ruleset di `klasifikasi_eselon.py` sesuai kebutuhan
- Validasi hasil klasifikasi secara manual untuk data sample

**Error saat menjalankan klasifikasi eselon:**

- Pastikan file Excel/CSV ada di direktori yang sama
- Periksa nama kolom `jabatan_nama` dan `jabatan_jenis` di file
- Pastikan Python dan pandas sudah terinstall

---

**Dibuat dengan ❤️ untuk analisis data kepegawaian yang lebih efektif**
