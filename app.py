# File: app.py
import streamlit as st
import datetime
from database_juz import db_juz
from hijridate import Gregorian
import urllib.parse
from pdf_utils import buat_pdf_tunggal, buat_pdf_pasangan

# Hubungan indeks bulan dengan nama bulan Hijriah standar
BULAN_HIJRIAH = [
    "Muharram", "Safar", "Rabi'ul Awal", "Rabi'ul Akhir", 
    "Jumadil Awal", "Jumadil Akhir", "Rajab", "Sya'ban", 
    "Ramadhan", "Syawal", "Dzulqa'dah", "Dzulhijjah"
]

HARI_INDONESIA = {
    0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis",
    4: "Jumat", 5: "Sabtu", 6: "Minggu"
}

def konversi_masehi_ke_hijriah(tanggal):
    hijri = Gregorian(tanggal.year, tanggal.month, tanggal.day).to_hijri()
    nama_bulan = BULAN_HIJRIAH[hijri.month - 1]
    return f"{hijri.day:02d} {nama_bulan} {hijri.year} H"

st.set_page_config(page_title="Ngaji Diri: Pemetaan Karakter", page_icon="✨", layout="wide")

st.markdown("""
    <style>
        html, body, [class*="css"] { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        div[data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #007BFF; font-weight: 700; }
        div[data-testid="stMetricLabel"] { font-size: 1.0rem !important; color: #555555; font-weight: 600; }
        .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; font-size: 1.1rem; padding: 0.5rem 1rem; transition: all 0.3s; }
        .stButton>button:hover { transform: scale(1.01); box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1); }
        button[data-baseweb="tab"] { font-size: 0.85rem !important; padding: 8px 10px !important; }
        hr { margin-top: 1.5em; margin-bottom: 1.5em; border-top: 2px dashed #E0E0E0; }
        h1, h2, h3 { color: #1E293B; }
        @media (max-width: 600px) {
            .stMetric { margin-bottom: 15px; }
            h1 { font-size: 1.6rem !important; }
            h2 { font-size: 1.3rem !important; }
            div[data-testid="stMetricValue"] { font-size: 1.5rem !important; }
        }
    </style>
""", unsafe_allow_html=True)

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
    if tanggal is None:
        return 0, 0, "", None
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

def hitung_prosentase_kecocokan(val1, val2, juz1, juz2):
    skor = 55 + ((val1 + val2 + juz1 + juz2) % 45)
    if skor >= 85: return skor, "Sangat Harmonis (Satu Frekuensi Jiwa)", "#28a745"
    elif skor >= 70: return skor, "Dinamis (Saling Mengimbangi)", "#17a2b8"
    else: return skor, "Menantang (Butuh Kompromi Luas)", "#ffc107"

def render_profil_lahiriah_ui(nama, val_nama, nilai_surat, tanggal, tgl_hijriah_str, total_kalkulasi, tgl_rincian_str, nilai_juz, profil):
    st.markdown(f"**📅 Penanggalan Masehi:** {tanggal.strftime('%d/%m/%Y')} &nbsp;&nbsp;|&nbsp;&nbsp; **🌙 Penanggalan Hijriah:** {tgl_hijriah_str}")
    st.write("")
    col_met1, col_met2, col_juz = st.columns(3)
    col_met1.metric(label="Hisab Nama (Surah)", value=f"Ke-{nilai_surat}", delta=f"Total: {val_nama}", delta_color="off")
    col_met2.metric(label="Hasil Kalkulasi Tgl", value=total_kalkulasi, delta=tgl_rincian_str, delta_color="off")
    col_juz.metric(label="Resonansi Tindakan", value=f"Juz {nilai_juz}")
    
    if profil:
        st.subheader(f"💎 Karakter Utama: \"{profil.get('julukan', '-')}\"")
        with st.expander("📖 Rangkuman Karakteristik & Filosofi", expanded=True):
            st.write(f"**Filosofi Huruf:** {profil.get('huruf', '-')}")
            st.write(f"**Gambaran Kepribadian:** {profil.get('deskripsi_umum', '-')}")
            st.write(f"**Resonansi Teks:** {profil.get('detail_surah', '-')}")
        
        st.write("")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["✨ Potensi", "⚠️ Kelemahan", "🧭 Strategi", "🩺 Medis", "💼 Karir"])
        
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
            for fisik in profil.get('kelemahan_fisik', []): st.write(f"• {fisik}")
            st.write("---")
            st.write(f"**Potensi Penyakit Psikosomatis:**\n{profil.get('risiko_penyakit', '-')}")
        with tab5:
            st.info(f"**Sektor Profesi & Bisnis yang Selaras:**\n\n{profil.get('jenis_usaha', '-')}")
            
        hari_lahir_user = HARI_INDONESIA.get(tanggal.weekday(), "hari lahir")
        st.write("")
        st.markdown(f"""
        <div style="background-color: #fff9db; padding: 20px; border-radius: 10px; border-left: 5px solid #fab005; margin-top: 10px; margin-bottom: 10px;">
            <h5 style="margin-top: 0; color: #d9480f; font-weight: 700;">🌌 Solusi Langit (Amalan Ruhani Diri)</h5>
            <p style="margin-bottom: 0; color: #2b2b2b;">
                Untuk menjemput keberkahan batin dan membuka jalan keluar atas permasalahan hidup, amalkan resep ini secara istiqamah: 
                <br><b>👉 Bacalah JUZ {nilai_juz} Anda minimal satu minggu sekali, tepat pada hari lahir Anda (Hari {hari_lahir_user}).</b>
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Teks analisis untuk Juz {nilai_juz} saat ini sedang dikonfigurasi ke dalam sistem.")

st.markdown("### Membaca Potensi, Memahami Fitrah")
st.markdown("Aplikasi cermin untuk membedah profil batiniah (Nama) dan lahiriah (Tanggal Lahir) Anda, serta **kalkulasi kecocokan pasangan**.")
st.write("") 

with st.container():
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        st.subheader("👤 Identitas Diri (Utama)")
        nama_input = st.text_input("Nama Lengkap Anda:", placeholder="Ketik nama lengkap...")
        tanggal_input = st.date_input(
            "Tanggal Lahir Anda:", 
            value=datetime.date(1980, 1, 7), 
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
            format="DD/MM/YYYY"
        )
    with col_input2:
        st.subheader("💞 Identitas Pasangan (Opsional)")
        nama_pasangan = st.text_input("Nama Lengkap Pasangan:", placeholder="Kosongkan jika hanya menganalisis diri sendiri...")
        tanggal_pasangan = st.date_input(
            "Tanggal Lahir Pasangan:", 
            value=datetime.date(1985, 1, 1), 
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
            format="DD/MM/YYYY"
        )
    
    st.write("")
    tombol_analisis = st.button("🔍 Mulai Analisis Karakter", type="primary", use_container_width=True)

st.divider()

if tombol_analisis:
    st.session_state['analisis_berjalan'] = True

if st.session_state.get('analisis_berjalan', False):
    if nama_input and tanggal_input:
        val_nama, nilai_surat = hitung_hisab_jumal(nama_input)
        nilai_juz, total_kalkulasi, tgl_rincian_str, h_date = hitung_juz_hijriah(tanggal_input)
        nama_bulan_h = BULAN_HIJRIAH[h_date.month - 1]
        tgl_hijriah_str = f"{h_date.day:02d} {nama_bulan_h} {h_date.year} H"
        profil = db_juz.get(nilai_juz)
        
        analisis_pasangan_aktif = bool(nama_pasangan.strip())
        
        if analisis_pasangan_aktif:
            val_nama_p, nilai_surat_p = hitung_hisab_jumal(nama_pasangan)
            nilai_juz_p, total_kalkulasi_p, tgl_rincian_str_p, h_date_p = hitung_juz_hijriah(tanggal_pasangan)
            nama_bulan_hp = BULAN_HIJRIAH[h_date_p.month - 1]
            tgl_hijriah_str_p = f"{h_date_p.day:02d} {nama_bulan_hp} {h_date_p.year} H"
            profil_p = db_juz.get(nilai_juz_p)
            
            st.success(f"🎉 Pemetaan karakter relasi berhasil disusun!")
            
            tab_u, tab_p, tab_relasi = st.tabs([f"👤 {nama_input.split()[0].upper()}", f"💞 {nama_pasangan.split()[0].upper()}", "💑 KESELARASAN RELASI"])
            
            with tab_u:
                render_profil_lahiriah_ui(nama_input, val_nama, nilai_surat, tanggal_input, tgl_hijriah_str, total_kalkulasi, tgl_rincian_str, nilai_juz, profil)
            with tab_p:
                render_profil_lahiriah_ui(nama_pasangan, val_nama_p, nilai_surat_p, tanggal_pasangan, tgl_hijriah_str_p, total_kalkulasi_p, tgl_rincian_str_p, nilai_juz_p, profil_p)
            with tab_relasi:
                st.header("💑 Analisis Keselarasan & Kompatibilitas Asmara")
                prosentase, deskripsi_status, warna_hex = hitung_prosentase_kecocokan(val_nama, val_nama_p, nilai_juz, nilai_juz_p)
                st.markdown(f"""
                <div style="text-align: center; padding: 25px; background-color: #f8f9fa; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
                    <h3 style="margin: 0; color: #4a5568; font-size: 1.2rem;">Tingkat Keselarasan Energi Hubungan</h3>
                    <h1 style="margin: 10px 0; font-size: 3.8rem; color: #007BFF; font-weight: 800;">{prosentase}%</h1>
                    <h4 style="margin: 0; color: {warna_hex}; font-weight: 700;">{deskripsi_status}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                if profil and profil_p:
                    col_kiri, col_kanan = st.columns(2)
                    with col_kiri:
                        st.info(f"**Karakter Dasar {nama_input.split()[0]}:**\n\n*\"{profil.get('julukan', '-')}\"*")
                    with col_kanan:
                        st.success(f"**Karakter Dasar {nama_pasangan.split()[0]}:**\n\n*\"{profil_p.get('julukan', '-')}\"*")
                        
                    st.divider()
                    st.subheader("⚡ Potensi Gesekan & Titik Konflik Relasi")
                    st.markdown(f"- **Sisi Buta Anda:** {profil.get('kekurangan', '-')}")
                    st.markdown(f"- **Sisi Buta Pasangan:** {profil_p.get('kekurangan', '-')}")
                    
                    st.divider()
                    st.subheader("🗝️ Solusi & Jalan Keluar (Resep Keharmonisan)")
                    st.write(f"**1. Nasihat untuk Anda ({nama_input.split()[0]}):**")
                    st.write(f"> *{profil.get('analisa_halaman', {}).get('jalan_keluar', '-')}*")
                    st.write(f"**2. Nasihat untuk Pasangan ({nama_pasangan.split()[0]}):**")
                    st.write(f"> *{profil_p.get('analisa_halaman', {}).get('jalan_keluar', '-')}*")
                    
        else:
            st.success(f"🎉 Pemetaan profil berhasil disusun untuk: **{nama_input.upper()}**")
            render_profil_lahiriah_ui(nama_input, val_nama, nilai_surat, tanggal_input, tgl_hijriah_str, total_kalkulasi, tgl_rincian_str, nilai_juz, profil)
            
            st.divider()
            st.header("⚖️ Sintesis Kepribadian")
            st.markdown(f"""
            <div style="background-color: #f1f8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #007BFF;">
                <p style="margin-top: 0;"><b>💡 Panduan Sintesis Diri:</b></p>
                <p>Niat dan pola pikir Anda berpusat pada frekuensi <b>Surat ke-{nilai_surat}</b>. Namun dalam eksekusi di dunia nyata, Anda menggunakan gaya <b>Juz {nilai_juz}</b>.</p>
                <ul>
                    <li><b>Jika Selaras:</b> Pikiran dan perbuatan berjalan berdampingan (integritas tinggi).</li>
                    <li><b>Jika Bertolak Belakang:</b> Lingkungan melihat Anda sebagai sosok dengan gaya <b>Juz {nilai_juz}</b>, padahal jauh di lubuk hati, Anda mendambakan pendekatan <b>Surat {nilai_surat}</b>.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        st.divider()
        st.header("📥 Unduh Laporan Manuskrip PDF")
        
        NOMOR_DANA = "0821-1755-0298" 
        NOMOR_WHATSAPP = "6282295165231" 
        KODE_AKSES_PDF = "BERKAH2026"
        
        st.markdown(f"""
        <div style="background-color: #f8f9fa; border: 2px solid #007BFF; border-radius: 10px; padding: 20px; text-align: center; margin-top: 20px; margin-bottom: 20px;">
            <h4 style="margin-top:0; color:#007BFF;">Dukung Pengembangan Aplikasi</h4>
            <p style="margin-bottom:5px;">Untuk mengunduh hasil pemetaan karakter dalam bentuk PDF eksklusif, silakan berikan dukungan seikhlasnya melalui DANA.</p>
            <h2 style="margin:10px 0; color:#28a745;">DANA: {NOMOR_DANA}</h2>
            <p style="font-size:0.9rem; color:#666;">Setelah transfer, kirimkan bukti pembayaran untuk mendapatkan <b>Kode Akses</b> pengunduhan.</p>
        </div>
        """, unsafe_allow_html=True)
        
        pesan_wa = urllib.parse.quote(f"Halo Admin, saya sudah transfer donasi untuk aplikasi Ngaji Diri atas nama {nama_input}. Mohon berikan Kode Akses PDF.")
        link_wa = f"https://wa.me/{NOMOR_WHATSAPP}?text={pesan_wa}"
        
        st.link_button("📲 Kirim Bukti Transfer via WhatsApp", link_wa, use_container_width=True)
        st.write("")
        
        kunci_input = st.text_input("🔑 Masukkan Kode Akses PDF di sini:", placeholder="Contoh: BERKAH2026")
        
        if kunci_input:
            if kunci_input.upper() == KODE_AKSES_PDF.upper():
                if analisis_pasangan_aktif:
                    st.success("Kode Akses Valid! Silakan unduh Manuskrip Relasi Pasangan (PDF) di bawah ini.")
                    pdf_data = buat_pdf_pasangan(
                        nama_input, nama_pasangan, 
                        tanggal_input.strftime("%d/%m/%Y"), tanggal_pasangan.strftime("%d/%m/%Y"), 
                        tgl_hijriah_str, tgl_hijriah_str_p, 
                        nilai_juz, nilai_juz_p, profil, profil_p, 
                        prosentase, deskripsi_status
                    )
                    file_pdf_name = f"Ngaji_Relasi_{nama_input.replace(' ', '_')}.pdf"
                else:
                    st.success("Kode Akses Valid! Silakan unduh Manuskrip Diri Utama (PDF) di bawah ini.")
                    pdf_data = buat_pdf_tunggal(
                        nama_input, tanggal_input.strftime("%d/%m/%Y"), tgl_hijriah_str, 
                        tgl_rincian_str, val_nama, nilai_surat, total_kalkulasi, nilai_juz, profil
                    )
                    file_pdf_name = f"Ngaji_Diri_{nama_input.replace(' ', '_')}.pdf"
                    
                st.download_button(
                    label="📄 Unduh Manuskrip (PDF)",
                    data=pdf_data,
                    file_name=file_pdf_name,
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("Kode Akses tidak valid. Silakan hubungi Admin via WhatsApp.")

    else:
        st.warning("⚠️ Mohon isi Nama Lengkap dan pilih Tanggal Lahir Anda (Identitas Utama) terlebih dahulu.")

# SIMPAN (Ctrl+S)