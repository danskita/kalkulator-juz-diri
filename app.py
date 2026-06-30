# File: app.py
import streamlit as st
import datetime
from database_juz import db_juz
from hijri_converter import Gregorian
from pdf_utils import buat_pdf_tunggal, buat_pdf_pasangan

# Hubungan indeks bulan dengan nama bulan Hijriah standar
BULAN_HIJRIAH = [
    "Muharram", "Safar", "Rabi'ul Awal", "Rabi'ul Akhir", 
    "Jumadil Awal", "Jumadil Akhir", "Rajab", "Sya'ban", 
    "Ramadhan", "Syawal", "Dzulqa'dah", "Dzulhijjah"
]

# ==========================================
# PENGATURAN TEMA & CUSTOM CSS
# ==========================================
st.set_page_config(page_title="Kalkulator Karakter", page_icon="✨", layout="wide")

st.markdown("""
    <style>
        html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
        div[data-testid="stMetricValue"] { font-size: 2.2rem; color: #007BFF; font-weight: 700; }
        div[data-testid="stMetricLabel"] { font-size: 1.1rem; color: #555555; font-weight: 600; }
        .stButton>button { border-radius: 8px; font-weight: bold; padding: 0.5rem 1rem; transition: 0.3s; }
        .stButton>button:hover { transform: scale(1.02); }
        hr { border-top: 2px dashed #E0E0E0; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# FUNGSI LOGIKA PERHITUNGAN
# ==========================================
def hitung_hisab_jumal(nama):
    jumal_dict = {
        'kh': 600, 'ts': 500, 'sy': 300, 'sh': 90, 'dh': 800, 'th': 9, 'zh': 900, 'gh': 1000, 'dz': 700,
        'a': 1, 'i': 10, 'u': 6, 'e': 10, 'o': 6, 'c': 3, 'g': 20, 'p': 80, 'v': 80, 'x': 60,
        'b': 2, 'd': 4, 'f': 80, 'h': 5, 'j': 3, 'k': 20, 'l': 30, 'm': 40, 'n': 50, 'q': 100,
        'r': 200, 's': 60, 't': 400, 'w': 6, 'y': 10, 'z': 7
    }
    nama = nama.lower().replace(" ", "")
    total_nilai = 0
    i = 0
    while i < len(nama):
        if i + 1 < len(nama) and nama[i:i+2] in jumal_dict:
            total_nilai += jumal_dict[nama[i:i+2]]
            i += 2
        elif nama[i] in jumal_dict:
            total_nilai += jumal_dict[nama[i]]
            i += 1
        else:
            i += 1
    surat = 114 if total_nilai % 114 == 0 else total_nilai % 114
    return total_nilai, surat

def hitung_juz_hijriah(tanggal):
    if tanggal is None: return 0, 0, "", None
    h = Gregorian(tanggal.year, tanggal.month, tanggal.day).to_hijri()
    
    konversi_bulan = {1: 35, 2: 43, 3: 26, 4: 28, 5: 30, 6: 28, 7: 30, 8: 32, 9: 35, 10: 24, 11: 29, 12: 17}
    konversi_tgl_tahun = {
        1: 37, 2: 45, 3: 28, 4: 30, 5: 32, 6: 30, 7: 32, 8: 34, 9: 37, 10: 26,
        11: 31, 12: 19, 13: 41, 14: 30, 15: 34, 16: 21, 17: 27, 18: 16, 19: 44, 20: 26,
        21: 54, 22: 27, 23: 24, 24: 30, 25: 18, 26: 25, 27: 37, 28: 43, 29: 28, 30: 38, 31: 38
    }
    
    nilai_tgl = konversi_tgl_tahun.get(h.day, 0)
    nilai_bln = konversi_bulan.get(h.month, 0)
    sum_tahun = sum(int(digit) for digit in str(h.year))
    nilai_thn = konversi_tgl_tahun.get(sum_tahun, 0)
    
    total_gabungan = nilai_tgl + nilai_bln + nilai_thn
    total_kurang_19 = total_gabungan - 19
    juz = total_kurang_19 % 30
    juz = 30 if juz == 0 else juz
    
    rincian_str = f"Tgl({h.day}->{nilai_tgl}) + Bln({h.month}->{nilai_bln}) + Thn({sum_tahun}->{nilai_thn}) - 19"
    return juz, total_kurang_19, rincian_str, h

def hitung_kompatibilitas(juz1, juz2):
    """Algoritma sederhana untuk menentukan skor kecocokan berdasarkan kedekatan juz"""
    selisih = abs(juz1 - juz2)
    skor = 100 - (selisih * 2) 
    
    if skor >= 85: status = "Sangat Harmonis & Saling Melengkapi"
    elif skor >= 70: status = "Harmonis dengan Sedikit Penyesuaian"
    elif skor >= 55: status = "Dinamis & Butuh Banyak Kompromi"
    else: status = "Penuh Ujian & Butuh Kesabaran Ekstra"
    
    return skor, status

# ==========================================
# ANTARMUKA PENGGUNA (UI)
# ==========================================
st.title("📖 Ngaji Diri: Pemetaan Karakter")
st.markdown("Membaca Potensi, Memahami Fitrah melalui pendekatan numerologi tradisional dan pola ayat Al-Qur'an.")
st.write("") 

# Membuat dua Tab utama
tab_personal, tab_pasangan = st.tabs(["👤 Analisis Personal", "💞 Analisis Pasangan"])

# ------------------------------------------
# TAB 1: ANALISIS PERSONAL
# ------------------------------------------
with tab_personal:
    st.subheader("Identitas Personal")
    col1, col2 = st.columns(2)
    with col1: nama_input = st.text_input("Nama Lengkap:", key="nama_single")
    with col2: tgl_input = st.date_input("Tanggal Lahir:", value=datetime.date(1990, 1, 1), min_value=datetime.date(1900, 1, 1), key="tgl_single")
    
    if st.button("🔍 Mulai Analisis Personal", type="primary", use_container_width=True):
        if nama_input:
            val_nama, nilai_surat = hitung_hisab_jumal(nama_input)
            nilai_juz, total_kalkulasi, tgl_rincian_str, h_date = hitung_juz_hijriah(tgl_input)
            tgl_hijriah_str = f"{h_date.day:02d} {BULAN_HIJRIAH[h_date.month - 1]} {h_date.year} H"
            profil = db_juz.get(nilai_juz)
            
            st.success(f"Pemetaan berhasil untuk: **{nama_input.upper()}**")
            col_met1, col_met2, col_met3 = st.columns(3)
            col_met1.metric("Resonansi Juz", f"Juz {nilai_juz}")
            col_met2.metric("Resonansi Surah", f"Ke-{nilai_surat}")
            col_met3.metric("Skor Batiniah", val_nama)
            
            if profil:
                st.info(f"**Julukan Karakter:** {profil.get('julukan', '-')}")
                tgl_str = tgl_input.strftime("%d/%m/%Y")
                pdf_data = buat_pdf_tunggal(nama_input, tgl_str, tgl_hijriah_str, tgl_rincian_str, val_nama, nilai_surat, total_kalkulasi, nilai_juz, profil)
                
                st.download_button(
                    label="📥 Unduh Manuskrip Personal (PDF)",
                    data=pdf_data,
                    file_name=f"Ngaji_Diri_{nama_input.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.warning("Mohon isi Nama Lengkap terlebih dahulu.")

# ------------------------------------------
# TAB 2: ANALISIS PASANGAN
# ------------------------------------------
with tab_pasangan:
    st.subheader("Identitas Relasi / Pasangan")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Pihak Pertama (Anda)**")
        nama1 = st.text_input("Nama Lengkap Pihak 1:", key="nama_p1")
        tgl1 = st.date_input("Tgl Lahir Pihak 1:", value=datetime.date(1990, 1, 1), min_value=datetime.date(1900, 1, 1), key="tgl_p1")
        
    with col_b:
        st.markdown("**Pihak Kedua (Pasangan/Partner)**")
        nama2 = st.text_input("Nama Lengkap Pihak 2:", key="nama_p2")
        tgl2 = st.date_input("Tgl Lahir Pihak 2:", value=datetime.date(1992, 1, 1), min_value=datetime.date(1900, 1, 1), key="tgl_p2")
        
    if st.button("💞 Analisis Relasi & Keselarasan", type="primary", use_container_width=True):
        if nama1 and nama2:
            # Hitung Pihak 1
            val_nama1, surat1 = hitung_hisab_jumal(nama1)
            juz1, tot1, rinci1, h_date1 = hitung_juz_hijriah(tgl1)
            h_str1 = f"{h_date1.day:02d} {BULAN_HIJRIAH[h_date1.month - 1]} {h_date1.year} H"
            profil1 = db_juz.get(juz1)
            
            # Hitung Pihak 2
            val_nama2, surat2 = hitung_hisab_jumal(nama2)
            juz2, tot2, rinci2, h_date2 = hitung_juz_hijriah(tgl2)
            h_str2 = f"{h_date2.day:02d} {BULAN_HIJRIAH[h_date2.month - 1]} {h_date2.year} H"
            profil2 = db_juz.get(juz2)
            
            # Kalkulasi Kecocokan
            skor, status = hitung_kompatibilitas(juz1, juz2)
            
            st.success(f"Analisis Relasi Selesai: **{nama1.upper()} & {nama2.upper()}**")
            
            # Tampilan Singkat di Layar
            st.markdown(f"### 💖 Skor Keselarasan: {skor}%")
            st.info(f"**Status Relasi:** {status}")
            
            # Eksekusi Pembuatan PDF Pasangan dari pdf_utils.py
            tgl1_str = tgl1.strftime("%d/%m/%Y")
            tgl2_str = tgl2.strftime("%d/%m/%Y")
            
            pdf_pasangan = buat_pdf_pasangan(
                nama1, nama2, 
                tgl1_str, tgl2_str, 
                h_str1, h_str2, 
                juz1, juz2, 
                profil1, profil2, 
                skor, status
            )
            
            st.write("Cetak dokumen di bawah ini untuk melihat penjabaran lengkap karakter berdua, potensi gesekan, dan solusi langitnya.")
            st.download_button(
                label="📥 Unduh Manuskrip Relasi / Pasangan (PDF)",
                data=pdf_pasangan,
                file_name=f"Relasi_{nama1.replace(' ','')}_dan_{nama2.replace(' ','')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.warning("Mohon lengkapi nama kedua belah pihak.")