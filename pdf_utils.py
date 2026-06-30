# File: pdf_utils.py
import datetime
from fpdf import FPDF

# Definisi pendukung
HARI_INDONESIA = {
    0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis",
    4: "Jumat", 5: "Sabtu", 6: "Minggu"
}

def clean_txt(text):
    if not isinstance(text, str): return str(text)
    replacements = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", "✧": "*", "✦": "*"}
    for k, v in replacements.items(): text = text.replace(k, v)
    return text.encode('latin-1', 'ignore').decode('latin-1')

class MysticalPDF(FPDF):
    def header(self):
        self.set_draw_color(139, 115, 85)
        self.set_line_width(1)
        self.rect(5, 5, 200, 287)
        self.set_line_width(0.3)
        self.rect(7, 7, 196, 283)
        self.set_font("Times", 'B', 16)
        self.set_text_color(139, 115, 85)
        self.set_xy(9, 8)
        self.cell(10, 10, "*", align="L")
        self.set_xy(191, 8)
        self.cell(10, 10, "*", align="R")
        self.set_y(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"~ Lembar Penyingkapan {self.page_no()} ~", 0, 0, 'C')

# ==========================================
# 1. PDF UNTUK TUNGGAL (SENDIRI)
# ==========================================
def buat_pdf_tunggal(nama, tgl_lahir_str, tgl_hijriah_str, tgl_rincian_str, total_nama, surat, total_tgl, juz, profil):
    pdf = MysticalPDF() 
    pdf.add_page()
    
    pdf.set_font("Times", 'B', 22)
    pdf.set_text_color(40, 30, 20)
    pdf.cell(0, 10, txt="M A N U S K R I P   N G A J I   D I R I", ln=True, align='C')
    pdf.set_font("Times", 'I', 12)
    pdf.set_text_color(139, 115, 85)
    pdf.cell(0, 6, txt="~ Ekstraksi Resonansi Jiwa & Manifestasi Nasib ~", ln=True, align='C')
    pdf.ln(3)
    pdf.set_font("Times", '', 14)
    pdf.cell(0, 5, txt="* * * * *", ln=True, align='C')
    pdf.ln(8)
    
    pdf.set_font("Times", 'B', 13)
    pdf.set_text_color(40, 30, 20)
    pdf.cell(0, 8, txt="I. INSKRIPSI IDENTITAS KOSMIK", ln=True)
    pdf.set_font("Times", '', 11)
    pdf.cell(0, 6, txt=f"   Nama Entitas         : {clean_txt(nama).upper()}", ln=True)
    pdf.cell(0, 6, txt=f"   Titik Kehadiran (M)  : {tgl_lahir_str}", ln=True)
    pdf.cell(0, 6, txt=f"   Titik Kehadiran (H)  : {tgl_hijriah_str}", ln=True)
    pdf.ln(4)
    
    pdf.set_font("Times", 'B', 11)
    pdf.cell(0, 6, txt="   [+] Dimensi Batiniah (Pola Jiwa)", ln=True)
    pdf.set_font("Times", 'I', 11)
    pdf.cell(0, 6, txt=f"       Vibrasi Numerik Hisab Jumal: {total_nama}", ln=True)
    pdf.cell(0, 6, txt=f"       Resonansi Surah Al-Qur'an: Ke-{surat} (Portal Niat & Pola Pikir)", ln=True)
    pdf.ln(2)
    
    pdf.set_font("Times", 'B', 11)
    pdf.cell(0, 6, txt="   [+] Dimensi Lahiriah (Manifestasi Tindakan)", ln=True)
    pdf.set_font("Times", 'I', 11)
    pdf.cell(0, 6, txt=f"       Pola Hitung Leluhur: {tgl_rincian_str}", ln=True)
    pdf.cell(0, 6, txt=f"       Hasil Kalkulasi Akhir: {total_tgl}", ln=True)
    pdf.cell(0, 6, txt=f"       Resonansi Juz Al-Qur'an: Juz {juz}", ln=True)
    pdf.ln(6)
    
    pdf.set_text_color(139, 115, 85)
    pdf.cell(0, 5, txt="~ * ~", ln=True, align='C')
    pdf.ln(5)
    
    if profil:
        pdf.set_text_color(40, 30, 20)
        pdf.set_font("Times", 'B', 13)
        pdf.cell(0, 8, txt="II. PEMBACAAN FITRAH & MANIFESTASI KARAKTER", ln=True)
        pdf.ln(2)
        pdf.set_font("Times", 'B', 12)
        pdf.cell(0, 6, txt=f"Gelar Kejiwaan: {clean_txt(profil.get('julukan', '-'))}", ln=True)
        pdf.set_font("Times", 'I', 11)
        pdf.set_text_color(120, 90, 40)
        pdf.cell(0, 6, txt=f"Filosofi Huruf: {clean_txt(profil.get('huruf', '-'))}", ln=True)
        pdf.ln(3)
        
        pdf.set_text_color(40, 30, 20)
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 6, txt="Gambaran Kepribadian:", ln=True)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 5, txt=clean_txt(profil.get('deskripsi_umum', '-')), align='L')
        pdf.ln(3)
        
        analisa = profil.get('analisa_halaman', {})
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 6, txt="Pola Manifestasi & Strategi Kehidupan:", ln=True)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 5, txt=f"- Taktik Komunikasi: {clean_txt(analisa.get('taktis', '-'))}", align='L')
        pdf.multi_cell(0, 5, txt=f"- Resolusi Konflik: {clean_txt(analisa.get('jalan_keluar', '-'))}", align='L')
        pdf.ln(3)

        try:
            dt_obj = datetime.datetime.strptime(tgl_lahir_str, "%d/%m/%Y")
            hari_nama = HARI_INDONESIA.get(dt_obj.weekday(), "hari lahir")
        except:
            hari_nama = "hari lahir"

        pdf.set_text_color(139, 115, 85)
        pdf.cell(0, 5, txt="~ * ~", ln=True, align='C')
        pdf.ln(3)
        pdf.set_text_color(40, 30, 20)
        pdf.set_font("Times", 'B', 13)
        pdf.cell(0, 8, txt="III. AMALAN RUHANI (SOLUSI LANGIT)", ln=True)
        pdf.set_font("Times", 'I', 11)
        pdf.multi_cell(0, 5, txt=clean_txt(f"Untuk membuka pintu keberkahan batiniah dan menjemput jalan keluar dari permasalahan hidup, amalkanlah: Bacalah JUZ {juz} Anda minimal satu minggu sekali secara istiqamah, tepat pada hari kelahiran Anda (Hari {hari_nama})."), align='L')
        
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 2. PDF UNTUK PASANGAN (SANGAT LENGKAP & DETAIL)
# ==========================================
def buat_pdf_pasangan(nama1, nama2, tgl1_str, tgl2_str, h_str1, h_str2, juz1, juz2, profil1, profil2, prosentase, status_relasi):
    pdf = MysticalPDF()
    pdf.add_page()
    
    # --- HEADER RELASI ---
    pdf.set_font("Times", 'B', 22)
    pdf.set_text_color(40, 30, 20)
    pdf.cell(0, 10, txt="M A N U S K R I P   R E L A S I", ln=True, align='C')
    pdf.set_font("Times", 'I', 12)
    pdf.set_text_color(139, 115, 85)
    pdf.cell(0, 6, txt="~ Ekstraksi Keselarasan Jiwa, Fitrah, & Solusi Pasangan ~", ln=True, align='C')
    pdf.ln(3)
    pdf.set_font("Times", '', 14)
    pdf.cell(0, 5, txt="* * * * *", ln=True, align='C')
    pdf.ln(6)
    
    # --- I. IDENTITAS PASANGAN ---
    pdf.set_font("Times", 'B', 13)
    pdf.set_text_color(40, 30, 20)
    pdf.cell(0, 8, txt="I. INSKRIPSI IDENTITAS KOSMIK PASANGAN", ln=True)
    pdf.set_font("Times", 'B', 11)
    pdf.cell(0, 6, txt=f"   [+] Pihak Pertama : {clean_txt(nama1).upper()}", ln=True)
    pdf.set_font("Times", '', 11)
    pdf.cell(0, 6, txt=f"       Lahir: {tgl1_str} / {h_str1} (Resonansi Juz {juz1})", ln=True)
    pdf.ln(2)
    pdf.set_font("Times", 'B', 11)
    pdf.cell(0, 6, txt=f"   [+] Pihak Kedua   : {clean_txt(nama2).upper()}", ln=True)
    pdf.set_font("Times", '', 11)
    pdf.cell(0, 6, txt=f"       Lahir: {tgl2_str} / {h_str2} (Resonansi Juz {juz2})", ln=True)
    pdf.ln(4)
    
    pdf.set_text_color(139, 115, 85)
    pdf.cell(0, 5, txt="~ * ~", ln=True, align='C')
    pdf.ln(4)
    
    # --- II. PROFIL LENGKAP PIHAK 1 ---
    pdf.set_text_color(40, 30, 20)
    pdf.set_font("Times", 'B', 13)
    pdf.cell(0, 8, txt=f"II. PEMBACAAN FITRAH: {clean_txt(nama1).upper()}", ln=True)
    if profil1:
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 6, txt=f"Karakter Dasar: {clean_txt(profil1.get('julukan', '-'))}", ln=True)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 5, txt=f"Gambaran Kepribadian:\n{clean_txt(profil1.get('deskripsi_umum', '-'))}", align='L')
        pdf.ln(1)
        pdf.multi_cell(0, 5, txt=f"Kelebihan (Potensi): {clean_txt(profil1.get('kelebihan', '-'))}", align='L')
        pdf.ln(1)
        pdf.multi_cell(0, 5, txt=f"Titik Bayangan (Kekurangan): {clean_txt(profil1.get('kekurangan', '-'))}", align='L')
    else:
        pdf.set_font("Times", 'I', 11)
        pdf.cell(0, 6, txt="Data profil sedang dikonfigurasi.", ln=True)
    pdf.ln(4)

    # --- III. PROFIL LENGKAP PIHAK 2 ---
    pdf.set_font("Times", 'B', 13)
    pdf.cell(0, 8, txt=f"III. PEMBACAAN FITRAH: {clean_txt(nama2).upper()}", ln=True)
    if profil2:
        pdf.set_font("Times", 'B', 11)
        pdf.cell(0, 6, txt=f"Karakter Dasar: {clean_txt(profil2.get('julukan', '-'))}", ln=True)
        pdf.set_font("Times", '', 11)
        pdf.multi_cell(0, 5, txt=f"Gambaran Kepribadian:\n{clean_txt(profil2.get('deskripsi_umum', '-'))}", align='L')
        pdf.ln(1)
        pdf.multi_cell(0, 5, txt=f"Kelebihan (Potensi): {clean_txt(profil2.get('kelebihan', '-'))}", align='L')
        pdf.ln(1)
        pdf.multi_cell(0, 5, txt=f"Titik Bayangan (Kekurangan): {clean_txt(profil2.get('kekurangan', '-'))}", align='L')
    else:
        pdf.set_font("Times", 'I', 11)
        pdf.cell(0, 6, txt="Data profil sedang dikonfigurasi.", ln=True)
    
    # === HALAMAN 2: DINAMIKA & SOLUSI ===
    pdf.add_page()
    pdf.set_font("Times", 'B', 22)
    pdf.set_text_color(40, 30, 20)
    pdf.cell(0, 10, txt="D I N A M I K A   &   S O L U S I", ln=True, align='C')
    pdf.ln(8)

    # --- IV. TINGKAT KESELARASAN ---
    pdf.set_text_color(40, 30, 20)
    pdf.set_font("Times", 'B', 13)
    pdf.cell(0, 8, txt="IV. TINGKAT KESELARASAN HUBUNGAN", ln=True)
    pdf.set_font("Times", 'B', 16)
    pdf.set_text_color(0, 100, 200)
    pdf.cell(0, 10, txt=f"Skor Kecocokan Energi: {prosentase}%", ln=True)
    pdf.set_font("Times", 'B', 11)
    pdf.set_text_color(40, 30, 20)
    pdf.cell(0, 6, txt=f"Status Relasi: {clean_txt(status_relasi)}", ln=True)
    pdf.ln(4)

    # --- V. RESEP KEHARMONISAN & SOLUSI TINGKAH LAKU ---
    pdf.set_font("Times", 'B', 13)
    pdf.cell(0, 8, txt="V. RESEP KEHARMONISAN & PENYELESAIAN KONFLIK", ln=True)
    pdf.set_font("Times", '', 11)
    pdf.multi_cell(0, 5, txt="Gesekan dalam hubungan umumnya dipicu oleh benturan karakter bawaan. Penyelarasan hubungan tingkat tinggi dapat dicapai apabila masing-masing pihak menurunkan ego dan mengamalkan instruksi berikut:", align='L')
    pdf.ln(3)
    
    pdf.set_font("Times", 'B', 11)
    pdf.cell(0, 6, txt=f"A. Instruksi Resolusi Konflik untuk {clean_txt(nama1.split()[0])}:", ln=True)
    pdf.set_font("Times", 'I', 11)
    solusi1 = profil1.get('analisa_halaman', {}).get('jalan_keluar', '-') if profil1 else '-'
    pdf.multi_cell(0, 5, txt=f"\"{clean_txt(solusi1)}\"", align='L')
    pdf.ln(3)
    
    pdf.set_font("Times", 'B', 11)
    pdf.cell(0, 6, txt=f"B. Instruksi Resolusi Konflik untuk {clean_txt(nama2.split()[0])}:", ln=True)
    pdf.set_font("Times", 'I', 11)
    solusi2 = profil2.get('analisa_halaman', {}).get('jalan_keluar', '-') if profil2 else '-'
    pdf.multi_cell(0, 5, txt=f"\"{clean_txt(solusi2)}\"", align='L')
    pdf.ln(6)

    # --- VI. SOLUSI LANGIT (AMALAN RUHANI PASANGAN) ---
    try:
        dt_obj1 = datetime.datetime.strptime(tgl1_str, "%d/%m/%Y")
        hari_nama1 = HARI_INDONESIA.get(dt_obj1.weekday(), "hari lahir")
        dt_obj2 = datetime.datetime.strptime(tgl2_str, "%d/%m/%Y")
        hari_nama2 = HARI_INDONESIA.get(dt_obj2.weekday(), "hari lahir")
    except:
        hari_nama1 = "hari lahir"
        hari_nama2 = "hari lahir"

    pdf.set_text_color(139, 115, 85)
    pdf.cell(0, 5, txt="~ * ~", ln=True, align='C')
    pdf.ln(4)

    pdf.set_text_color(40, 30, 20)
    pdf.set_font("Times", 'B', 13)
    pdf.cell(0, 8, txt="VI. AMALAN RUHANI (SOLUSI LANGIT PASANGAN)", ln=True)
    pdf.set_font("Times", '', 11)
    
    teks_langit1 = f"1. Bagi {clean_txt(nama1.split()[0])}:\nSangat disarankan untuk mengamalkan pembacaan JUZ {juz1} minimal satu minggu sekali, tepat pada hari {hari_nama1}. Ini berfungsi untuk meredam ego, membuka jalan rezeki, dan melembutkan aura diri di mata pasangan."
    teks_langit2 = f"2. Bagi {clean_txt(nama2.split()[0])}:\nAmalkanlah pembacaan JUZ {juz2} secara istiqamah minimal satu minggu sekali, tepat pada hari {hari_nama2}. Energi dari lantunan juz ini akan menjadi benteng pelindung rumah tangga/relasi dari energi negatif."
    teks_penutup = "Jadikan amalan ini sebagai ikhtiar batin bersama untuk menembus hijab permasalahan hidup, menekan potensi konflik, dan menyatukan frekuensi jiwa di bawah naungan rida-Nya."
    
    pdf.multi_cell(0, 5, txt=teks_langit1, align='L')
    pdf.ln(2)
    pdf.multi_cell(0, 5, txt=teks_langit2, align='L')
    pdf.ln(3)
    
    pdf.set_font("Times", 'B', 11)
    pdf.multi_cell(0, 5, txt=teks_penutup, align='L')

    return pdf.output(dest='S').encode('latin-1')