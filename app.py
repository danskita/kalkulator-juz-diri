# File: app.py
import streamlit as st
import datetime
from database_juz import db_juz
from fpdf import FPDF
from hijridate import Gregorian

# Hubungan indeks bulan dengan nama bulan Hijriah standar
BULAN_HIJRIAH = [
    "Muharram", "Safar", "Rabi'ul Awal", "Rabi'ul Akhir", 
    "Jumadil Awal", "Jumadil Akhir", "Rajab", "Sya'ban", 
    "Ramadhan", "Syawal", "Dzulqa'dah", "Dzulhijjah"
]

def konversi_masehi_ke_hijriah(tanggal):
    hijri = Gregorian(tanggal.year, tanggal.month, tanggal.day).to_hijri()
    nama_bulan = BULAN_HIJRIAH[hijri.month - 1]
    return f"{hijri.day:02d} {nama_bulan} {hijri.year} H"

# ==========================================
# 1. PENGATURAN TEMA & CUSTOM CSS (UI/UX)
# ==========================================
st.set_page_config(page_title="Kalkulator Karakter", page_icon="✨", layout="wide")

st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        div[data-testid="stMetricValue"] {
            font-size: 2.2rem;
            color: #007BFF;
            font-weight: 700;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1.1rem;
            color: #555555;
            font-weight: 600;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1rem;
            padding: 0.5rem 1rem;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        }
        hr {
            margin-top: 2em;
            margin-bottom: 2em;
            border-top: 2px dashed #E0E0E0;
        }
        h1, h2, h3 {
            color: #1E293B;
        }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. MESIN KALKULATOR & FUNGSI LOGIKA
# ==========================================
def hitung_hisab_jumal(nama):
    jumal_dict = {
        'kh': 600, 'ts': 500, 'sy': 300, 'sh': 90, 
        'dh': 800, 'th': 9, 'zh': 900, 'gh': 1000, 'dz': 700,
        'a': 1, 'i': 10, 'u': 6, 'e': 10, 'o': 6,
        'c': 3, 'g': 20, 'p': 80, 'v': 80, 'x': 60,
        'b': 2, 'd': 4, 'f': 80, 'h': 5, 'j': 3,
        'k': 20, 'l': 30, 'm': 40, 'n': 50, 'q': 100,
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
    if tanggal is None:
        return 0, 0, "", None
        
    # Konversi Masehi ke Hijriah
    h = Gregorian(tanggal.year, tanggal.month, tanggal.day).to_hijri()
    
    # Tabel Data Konversi Bulan Kelahiran
    konversi_bulan = {
        1: 35, 2: 43, 3: 26, 4: 28, 5: 30, 6: 28,
        7: 30, 8: 32, 9: 35, 10: 24, 11: 29, 12: 17
    }
    
    # Tabel Data Konversi Tanggal dan Tahun Kelahiran
    konversi_tgl_tahun = {
        1: 37, 2: 45, 3: 28, 4: 30, 5: 32, 6: 30, 7: 32, 8: 34, 9: 37, 10: 26,
        11: 31, 12: 19, 13: 41, 14: 30, 15: 34, 16: 21, 17: 27, 18: 16, 19: 44, 20: 26,
        21: 54, 22: 27, 23: 24, 24: 30, 25: 18, 26: 25, 27: 37, 28: 43, 29: 28, 30: 38,
        31: 38
    }
    
    # 1. Konversi Tanggal Lahir (Hijriah)
    nilai_tgl = konversi_tgl_tahun.get(h.day, 0)
    
    # 2. Konversi Bulan Lahir (Hijriah)
    nilai_bln = konversi_bulan.get(h.month, 0)
    
    # 3. Konversi Tahun Lahir (Hijriah: Penjumlahan digit tahun)
    sum_tahun = sum(int(digit) for digit in str(h.year))
    nilai_thn = konversi_tgl_tahun.get(sum_tahun, 0)
    
    # 4. Kalkulasi Total Gabungan
    total_gabungan = nilai_tgl + nilai_bln + nilai_thn
    
    # 5. Pengurangan dengan Angka Pengurang (19)
    total_kurang_19 = total_gabungan - 19
    
    # 6. Menentukan Juz (Sisa bagi 30)
    juz = total_kurang_19 % 30
    juz = 30 if juz == 0 else juz
    
    rincian_str = f"Tgl({h.day}->{nilai_tgl}) + Bln({h.month}->{nilai_bln}) + Thn({sum_tahun}->{nilai_thn}) - 19"
    
    return juz, total_kurang_19, rincian_str, h


def clean_txt(text):
    """Pembersih karakter non-latin agar FPDF tidak error saat cetak"""
    if not isinstance(text, str): return str(text)
    
    # Membersihkan simbol yang berisiko membuat FPDF crash
    replacements = {
        "‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-",
        "✧": "*", "✦": "*", "✨": "", "💎": "", "📅": "", "🌙": "", "⚠️": ""
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
        
    return text.encode('latin-1', 'ignore').decode('latin-1')


# ==========================================
# FUNGSI PEMBUAT PDF (TEMA MISTIS / MANUSKRIP KUNO)
# ==========================================
class MysticalPDF(FPDF):
    def header(self):
        # Garis tepi (Border) mistis ganda
        self.set_draw_color(139, 115, 85) # Warna Coklat Keemasan Kuno (Tembaga)
        self.set_line_width(1)
        self.rect(5, 5, 200, 287) # Garis luar tebal
        self.set_line_width(0.3)
        self.rect(7, 7, 196, 283) # Garis dalam tipis
        
        # Ornamen pojok (Menggunakan ASCII agar tidak error di FPDF)
        self.set_font("Times", 'B', 16)
        self.set_text_color(139, 115, 85)
        self.set_xy(9, 8)
        self.cell(10, 10, "*", align="L")
        self.set_xy(191, 8)
        self.cell(10, 10, "*", align="R")
        
        # Kembalikan kursor ke posisi aman untuk isi teks
        self.set_y(15)

    def footer(self):
        # Ornamen pojok bawah (Menggunakan ASCII)
        self.set_font("Times", 'B', 16)
        self.set_text_color(139, 115, 85)
        self.set_xy(9, 279)
        self.cell(10, 10, "*", align="L")
        self.set_xy(191, 279)
        self.cell(10, 10, "*", align="R")
        
        # Penomoran Halaman Bergaya Kuno
        self.set_y(-15)
        self.set_font("Times", 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"~ Lembar Penyingkapan {self.page_no()} ~", 0, 0, 'C')


def buat_pdf(nama, tgl_lahir_str, tgl_hijriah_str, tgl_rincian_str, total_nama, surat, total_tgl, juz, profil):
    pdf = MysticalPDF() 
    pdf.add_page()
    
    # Header Utama & Judul
    pdf.set_font("Times", 'B', 22)
    pdf.set_text_color(40, 30, 20) # Warna Dark Charcoal / Tinta Kuno
    pdf.cell(0, 10, txt="M A N U S K R I P   N G A J I   D I R I", ln=True, align='C')
    pdf.set_font("Times", 'I', 12)
    pdf.set_text_color(139, 115, 85)
    pdf.cell(0, 6, txt="~ Ekstraksi Resonansi Jiwa & Manifestasi Nasib ~", ln=True, align='C')
    pdf.ln(3)
    
    # Garis Pembatas Mistis (ASCII)
    pdf.set_font("Times", '', 14)
    pdf.cell(0, 5, txt="* * * * *", ln=True, align='C')
    pdf.ln(8)
    
    # 1. Identitas & Model Matematis
    pdf.set_font("Times", 'B', 13)
    pdf.set_text_color(40, 30, 20)
    pdf.cell(0, 8, txt="I. INSKRIPSI IDENTITAS KOSMIK", ln=True)
    pdf.set_font("Times", '', 11)
    pdf.cell(0, 6, txt=f"   Nama Entitas         : {clean_txt(nama).upper()}", ln=True)
    pdf.cell(0, 6, txt=f"   Titik Kehadiran (M)  : {tgl_lahir_str}", ln=True)
    pdf.cell(0, 6, txt=f"   Titik Kehadiran (H)  : {tgl_hijriah_str}", ln=True)
    pdf.ln(4)
    
    # Batiniah
    pdf.set_font("Times", 'B', 11)
    pdf.cell(0, 6, txt="   [+] Dimensi Batiniah (Pola Jiwa)", ln=True)
    pdf.set_font("Times", 'I', 11)
    pdf.cell(0, 6, txt=f"       Vibrasi Numerik Hisab Jumal : {total_nama}", ln=True)
    pdf.cell(0, 6, txt=f"       Resonansi Surah Al-Qur'an   : Ke-{surat} (Portal Niat & Pola Pikir)", ln=True)
    pdf.ln(2)
    
    # Lahiriah
    pdf.set_font("Times", 'B', 11)
    pdf.cell(0, 6, txt="   [+] Dimensi Lahiriah (Manifestasi Tindakan)", ln=True)
    pdf.set_font("Times", 'I', 11)
    pdf.cell(0, 6, txt=f"       Pola Hitung Leluhur    : {tgl_rincian_str}", ln=True)
    pdf.cell(0, 6, txt=f"       Hasil Kalkulasi Akhir  : {total_tgl}", ln=True)
    pdf.cell(0, 6, txt=f"       Resonansi Juz Al-Qur'an: Juz {juz}", ln=True)
    pdf.ln(6)
    
    pdf.set_text_color(139, 115, 85)
    pdf.cell(0, 5, txt="~ * ~", ln=True, align='C')
    pdf.ln(5)
    
    # 2. Detail Karakter
    if profil:
        pdf.set_text_color(40, 30, 20)
        pdf.set_font("Times", 'B', 13)
        pdf.cell(0, 8, txt="II. PEMBACAAN FITRAH & MANIFESTASI KARAKTER", ln=True)
        pdf.ln(2)
        
        pdf.set_font("Times", 'B', 12)
        pdf.cell(0, 6, txt=f"Gelar Kejiwaan : {clean_txt(profil.get('julukan', '-'))}", ln=True)
        pdf.set_font("Times", 'I', 11)
        pdf.set_text_color(120, 90, 40)
        pdf.cell(0, 6, txt=f"Filosofi Huruf   : {clean_txt(profil.get('huruf', '-'))}", ln=True)
        pdf.ln(3)
        
        pdf.set_text_color(40, 30, 20)
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 6, txt="Gambaran Kepribadian:", ln=True)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 5, txt=clean_txt(profil.get('deskripsi_umum', '-')), align='L')
        pdf.ln(3)
        
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 6, txt="Korelasi Energi Surah (Ruhani):", ln=True)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 5, txt=clean_txt(profil.get('detail_surah', '-')), align='L')
        pdf.ln(3)
        
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 6, txt="Anugerah (Potensi & Kelebihan):", ln=True)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 5, txt=clean_txt(profil.get('kelebihan', '-')), align='L')
        pdf.ln(2)
        
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 6, txt="Titik Bayangan (Sisi Lemah & Kekurangan):", ln=True)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 5, txt=clean_txt(profil.get('kekurangan', '-')), align='L')
        pdf.ln(3)
        
        analisa = profil.get('analisa_halaman', {})
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 6, txt="Pola Manifestasi & Strategi Kehidupan:", ln=True)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 5, txt=f"- Taktik Komunikasi : {clean_txt(analisa.get('taktis', '-'))}", align='L')
        pdf.multi_cell(0, 5, txt=f"- Dinamika Emosi    : {clean_txt(analisa.get('negatif_positif', '-'))}", align='L')
        pdf.multi_cell(0, 5, txt=f"- Resolusi Konflik  : {clean_txt(analisa.get('jalan_keluar', '-'))}", align='L')
        pdf.multi_cell(0, 5, txt=f"- Fondasi Karakter  : {clean_txt(analisa.get('dasar', '-'))}", align='L')
        pdf.ln(3)
        
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 6, txt="Simpul Kelemahan Wadag (Fisik & Medis):", ln=True)
        pdf.set_font("Times", '', 11)
        fisik_list = profil.get('kelemahan_fisik', [])
        pdf.multi_cell(0, 5, txt=clean_txt("- Organ Rentan: " + ", ".join(fisik_list)), align='L')
        pdf.multi_cell(0, 5, txt=clean_txt("- Risiko Penyakit Psikosomatis: " + profil.get('risiko_penyakit', '-')), align='L')
        pdf.ln(3)
        
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 6, txt="Jalur Rezeki & Medan Pengabdian (Profesi):", ln=True)
        pdf.set_font("Times", 'I', 11)
        pdf.multi_cell(0, 5, txt=clean_txt(profil.get('jenis_usaha', '-')), align='L')
        
    return pdf.output(dest='S').encode('latin-1')


# ==========================================
# 3. ANTARMUKA PENGGUNA (UI)
# ==========================================

st.title("📖 Ngaji Diri: Pemetaan Karakter")
st.markdown("""
### Membaca Potensi, Memahami Fitrah
Bukan sebuah ramalan, melainkan ruang untuk **Ngaji Diri**. 
Aplikasi ini hadir sebagai cermin untuk membedah profil batiniah (Nama) dan lahiriah (Tanggal Lahir) Anda melalui pendekatan numerologi tradisional dan pola ayat Al-Qur'an. 

Tujuannya agar kita lebih memahami potensi diri, titik buta (*blind spots*), serta bagaimana cara terbaik untuk berinteraksi dengan dunia di sekitar kita.
""")
st.write("") 

with st.container():
    st.subheader("Masukkan Identitas Anda")
    col1, col2 = st.columns(2)
    with col1:
        nama_input = st.text_input("Nama Lengkap:", placeholder="Ketik nama lengkap Anda di sini...")
    with col2:
        tanggal_input = st.date_input(
            "Tanggal Lahir:", 
            value=datetime.date(1990, 1, 1), 
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
            format="DD/MM/YYYY"
        )
    
    st.write("")
    tombol_analisis = st.button("🔍 Mulai Analisis Karakter", type="primary", use_container_width=True)

st.divider()

if tombol_analisis:
    if nama_input and tanggal_input:
        
        # Eksekusi Mesin Hitung Nama
        val_nama, nilai_surat = hitung_hisab_jumal(nama_input)
        
        # Konversi Tanggal ke Hijriah & Kalkulasi
        nilai_juz, total_kalkulasi, tgl_rincian_str, h_date = hitung_juz_hijriah(tanggal_input)
        nama_bulan_h = BULAN_HIJRIAH[h_date.month - 1]
        tgl_hijriah_str = f"{h_date.day:02d} {nama_bulan_h} {h_date.year} H"
        
        if nilai_juz == 0:
            st.error("⚠️ Format tanggal lahir tidak valid. Silakan pilih ulang tanggal dari kalender.")
        else:
            st.success(f"🎉 Pemetaan profil berhasil disusun untuk: **{nama_input.upper()}**")
            
            # Tampilan Informasi Tanggal Lengkap
            st.markdown(f"**📅 Tanggal Lahir (Masehi):** {tanggal_input.strftime('%d/%m/%Y')} &nbsp;&nbsp;|&nbsp;&nbsp; **🌙 Tanggal Lahir (Hijriah):** {tgl_hijriah_str}")
            st.write("")
            
            # --- BAGIAN 1: Batiniah ---
            st.header("🌌 Dimensi Batiniah (Karakter Jiwa)")
            st.markdown("Cerminan dari pola pikir terdalam, niat rahasia, dan hasrat yang seringkali tidak terlihat oleh orang lain.")
            
            col_met1, col_met2, col_met3 = st.columns(3)
            col_met1.metric(label="Total Numerik Nama", value=val_nama)
            col_met2.metric(label="Resonansi Surah", value=f"Ke-{nilai_surat}")
            col_met3.metric(label="Kecerdasan Intuitif", value="Aktif")
            
            st.info(f"**Surat ke-{nilai_surat}** menuntun frekuensi batin Anda. *(Segera hadir: Penjelasan detail untuk 114 Surah Al-Qur'an)*.")
            st.divider()

            # --- BAGIAN 2: Lahiriah ---
            st.header("🌍 Dimensi Lahiriah (Karakter Tindakan)")
            st.markdown("Menggambarkan cara Anda bersosialisasi, bekerja, bereaksi terhadap tekanan, dan memecahkan masalah di dunia nyata berdasarkan penanggalan Hijriah.")
            
            col_juz1, col_juz2 = st.columns(2)
            col_juz1.metric(label="Hasil Kalkulasi", value=total_kalkulasi, delta=tgl_rincian_str, delta_color="off")
            col_juz2.metric(label="Resonansi Juz", value=f"Juz {nilai_juz}")
            
            profil = db_juz.get(nilai_juz)
            
            if profil:
                st.subheader(f"💎 Karakter Utama: \"{profil.get('julukan', '-')}\"")
                
                with st.expander("📖 Rangkuman Karakteristik & Filosofi", expanded=True):
                    st.write(f"**Filosofi Huruf:** {profil.get('huruf', '-')}")
                    st.write(f"**Gambaran Kepribadian:** {profil.get('deskripsi_umum', '-')}")
                    st.write(f"**Resonansi Teks:** {profil.get('detail_surah', '-')}")
                
                st.write("")
                
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "✨ Potensi & Kelebihan", 
                    "⚠️ Titik Buta (Kekurangan)", 
                    "🧭 Strategi Diri", 
                    "🩺 Profil Medis", 
                    "💼 Rekomendasi Karir"
                ])
                
                with tab1:
                    st.success(f"**Kekuatan Alami:**\n\n{profil.get('kelebihan', '-')}")
                with tab2:
                    st.warning(f"**Hal yang Perlu Diwaspadai:**\n\n{profil.get('kekurangan', '-')}")
                with tab3:
                    analisa = profil.get('analisa_halaman', {})
                    st.markdown("**Gaya Pendekatan Masalah:**")
                    st.write(f"- **Taktik Komunikasi:** {analisa.get('taktis', '-')}")
                    st.write(f"- **Dinamika Emosi:** {analisa.get('negatif_positif', '-')}")
                    st.write(f"- **Resolusi Konflik:** {analisa.get('jalan_keluar', '-')}")
                    st.write(f"- **Fondasi Karakter:** {analisa.get('dasar', '-')}")
                with tab4:
                    st.error("**Titik Lemah Fisik & Organ Rentan:**")
                    for fisik in profil.get('kelemahan_fisik', []):
                        st.write(f"• { fisik }")
                    st.write("---")
                    st.write(f"**Potensi Penyakit Psikosomatis:**\n{profil.get('risiko_penyakit', '-')}")
                with tab5:
                    st.info(f"**Sektor Profesi & Bisnis yang Selaras:**\n\n{profil.get('jenis_usaha', '-')}")
            else:
                st.info(f"Teks analisis untuk Juz {nilai_juz} saat ini sedang dikonfigurasi ke dalam sistem.")

            st.divider()

            # --- BAGIAN 3: Unduh PDF ---
            tgl_str = tanggal_input.strftime("%d/%m/%Y")
            pdf_data = buat_pdf(nama_input, tgl_str, tgl_hijriah_str, tgl_rincian_str, val_nama, nilai_surat, total_kalkulasi, nilai_juz, profil)
            
            st.download_button(
                label="📥 Unduh Hasil Ngaji Diri Beserta Rinciannya (PDF)",
                data=pdf_data,
                file_name=f"Ngaji_Diri_{nama_input.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.write("")

            # --- BAGIAN 4: Sintesis ---
            st.header("⚖️ Sintesis Kepribadian")
            st.markdown(f"Dinamika perpaduan antara batin (**Surah ke-{nilai_surat}**) dan tindakan lahiriah (**Juz {nilai_juz}**):")
            
            st.markdown(f"""
            <div style="background-color: #f1f8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #007BFF;">
                <p style="margin-top: 0;"><b>💡 Panduan Sintesis Diri:</b></p>
                <p>Niat, ambisi, dan cara Anda memproses informasi di dalam pikiran berpusat pada frekuensi <b>Surat ke-{nilai_surat}</b>. Namun, dalam eksekusi di dunia nyata—cara Anda bekerja dan bersosialisasi—Anda menggunakan gaya dan pendekatan <b>Juz {nilai_juz}</b>.</p>
                <ul>
                    <li><b>Jika Selaras:</b> Anda adalah pribadi yang sangat fokus. Apa yang Anda pikirkan dan perbuat berjalan berdampingan (integritas tinggi).</li>
                    <li><b>Jika Bertolak Belakang:</b> Anda mungkin sering mengalami pergolakan batin. Lingkungan melihat Anda sebagai sosok dengan gaya <b>Juz {nilai_juz}</b>, padahal jauh di lubuk hati, Anda mendambakan harmoni pendekatan <b>Surat {nilai_surat}</b>.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("⚠️ Mohon isi Nama Lengkap dan pilih Tanggal Lahir Anda terlebih dahulu.")