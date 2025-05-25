import streamlit as st
import sqlite3
from uuid import uuid4
from datetime import datetime

DB_PATH = "steam_motor.db"
USER = "admin"
PASS = "admin"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            kode_mtr TEXT PRIMARY KEY,
            tanggal_input TEXT,
            tanggal_cuci TEXT,
            cc INTEGER,
            nama_motor TEXT,
            nama_pelanggan TEXT,
            biaya INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS biaya_bulanan (
            bulan TEXT PRIMARY KEY,
            sabun INTEGER,
            gaji INTEGER,
            air INTEGER,
            listrik INTEGER
        )
    """)
    conn.commit()
    conn.close()

def insert_transaksi(cc, nama_motor, nama_pelanggan, biaya):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    kode = "MTR" + uuid4().hex[:8].upper()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tgl_cuci = datetime.now().strftime("%Y-%m-%d")
    c.execute("""
        INSERT INTO transaksi (kode_mtr, tanggal_input, tanggal_cuci, cc, nama_motor, nama_pelanggan, biaya)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (kode, now, tgl_cuci, cc, nama_motor, nama_pelanggan, biaya))
    conn.commit()
    conn.close()

def insert_biaya_bulanan(bulan, sabun, gaji, air, listrik):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO biaya_bulanan (bulan, sabun, gaji, air, listrik)
        VALUES (?, ?, ?, ?, ?)
    """, (bulan, sabun, gaji, air, listrik))
    conn.commit()
    conn.close()

def get_all_transaksi():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM transaksi ORDER BY tanggal_input DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_laba_rugi(bulan):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT SUM(biaya) FROM transaksi WHERE strftime('%Y-%m', tanggal_input) = ?", (bulan,))
    pemasukan = c.fetchone()[0] or 0
    c.execute("SELECT sabun, gaji, air, listrik FROM biaya_bulanan WHERE bulan = ?", (bulan,))
    row = c.fetchone()
    pengeluaran = sum(row) if row else 0
    conn.close()
    return pemasukan, pengeluaran, pemasukan - pengeluaran

def tentukan_biaya(cc):
    if cc <= 110:
        return 10000
    elif cc <= 125:
        return 12000
    elif cc <= 150:
        return 15000
    elif cc <= 155:
        return 18000
    else:
        return 25000

def menu_input_biaya():
    st.subheader("Input Biaya Bulanan")
    bulan = st.text_input("Bulan (YYYY-MM)", value=datetime.now().strftime("%Y-%m"))
    sabun = st.number_input("Sabun", min_value=0, step=1000)
    gaji = st.number_input("Gaji Karyawan", min_value=0, step=1000)
    air = st.number_input("Air", min_value=0, step=1000)
    listrik = st.number_input("Listrik", min_value=0, step=1000)
    if st.button("Simpan Biaya"):
        insert_biaya_bulanan(bulan, sabun, gaji, air, listrik)
        st.success("Tersimpan")

def menu_laba_rugi():
    st.subheader("Laporan Laba Rugi")
    bulan = st.text_input("Bulan (YYYY-MM)", value=datetime.now().strftime("%Y-%m"))
    pemasukan, pengeluaran, laba = get_laba_rugi(bulan)
    st.write(f"Bulan: {bulan}")
    st.write(f"Pemasukan: Rp{pemasukan:,}")
    st.write(f"Pengeluaran: Rp{pengeluaran:,}")
    st.write(f"Laba Bersih: Rp{laba:,}")

def steam_motor_menu():
    st.subheader("Form Steam Motor")
    cc = st.number_input("CC Motor", min_value=0, step=1)
    nama_motor = st.text_input("Nama Motor")
    nama_pelanggan = st.text_input("Nama Pelanggan")
    auto_biaya = tentukan_biaya(cc)
    biaya = st.number_input("Biaya Steam (Rp)", value=auto_biaya, step=1000)
    if st.button("Simpan Transaksi"):
        if cc and nama_motor and nama_pelanggan and biaya:
            insert_transaksi(cc, nama_motor, nama_pelanggan, biaya)
            st.success("Transaksi disimpan")
        else:
            st.error("Lengkapi semua kolom")
    if st.button("Lihat Riwayat"):
        st.table(get_all_transaksi())
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

def main():
    init_db()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.title("Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u == USER and p == PASS:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Salah")
    else:
        st.sidebar.title("Menu")
        pilihan = st.sidebar.radio("", ["Steam Motor", "Input Biaya", "Laba Rugi"])
        if pilihan == "Steam Motor":
            steam_motor_menu()
        elif pilihan == "Input Biaya":
            menu_input_biaya()
        else:
            menu_laba_rugi()

if __name__ == "__main__":
    main()
