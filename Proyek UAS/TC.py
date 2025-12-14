"""
Transpotition Cipher (Columnar) — Streamlit App
"""

import streamlit as st
import json
import math
import random
import base64
import hashlib
import hmac
from typing import List

# ----------------------------
# Konfigurasi dasar Streamlit
# ----------------------------
st.set_page_config(page_title="Transpotition Cipher (Columnar)", layout="wide")

# ------------------------------
# Inject CSS (dark theme + card)
# ------------------------------
st.markdown(
    """
    <style>
    /* Tema gelap modern */
    .stApp, .block-container 
    {
        background-color: #0e1117;
        color: #e6eef6;
    }
    .card 
    {
        background-color: #121418;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.6);
        margin-bottom: 18px;
    }
    .card h2, .card h3 { color: #e6eef6; }
    .stButton>button, .stDownloadButton>button 
    {
        background-color: #2b3642;
        color: #fff;
        border-radius: 8px;
        padding: 8px 12px;
    }
    .stTextInput>div>div>input, .stNumberInput>div>input, textarea 
    {
        background-color: #0f1519 !important;
        color: #e6eef6 !important;
        border-radius: 8px;
        border: 1px solid #22272b;
    }
    .stMarkdown, .stText, .stExpanderHeader { color: #c9d6e3; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------
# Konstanta / Config
# ------------------
MAGIC = "TENC1"
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB limit (ubah sesuai kebutuhan)

# -----------------------------
# Utility: parsing kunci numerik
# -----------------------------
def parse_kunci_numerik(kunci: str) -> List[int]:
    """
    Mengubah string seperti "3-1-4-2" menjadi list indeks 0-based [2,0,3,1].
    Validasi: angka harus 1..N tanpa duplikasi.
    """
    s = kunci.replace(" ", "")
    if not s:
        raise ValueError("Kunci kosong")
    parts = s.split("-")
    try:
        angka = [int(x) for x in parts]
    except Exception:
        raise ValueError("Format salah — gunakan contoh: 3-1-4-2")
    n = len(angka)
    if sorted(angka) != list(range(1, n + 1)):
        raise ValueError("Kunci harus berisi angka 1..N tanpa duplikasi")
    # convert to 0-based indices indicating read order per column
    # Example: input "3-1-4-2" -> angka=[3,1,4,2] -> return [2,0,3,1]
    return [a - 1 for a in angka]


# -------------------------------------
# Utility: inverse mapping (precompute)
# -------------------------------------
def inverse_mapping_from_key_indices(key_indices: List[int]) -> List[int]:
    """
    Dari key_indices (col_index -> read_pos) ke col_order (read_pos -> col_index)
    sehingga col_order[read_pos] = column index.
    """
    cols = len(key_indices)
    col_order = [0] * cols
    for col_idx, read_pos in enumerate(key_indices):
        if read_pos < 0 or read_pos >= cols:
            raise ValueError("Invalid key_indices value")
        col_order[read_pos] = col_idx
    return col_order


# --------------------------------------
# Fungsi enkripsi/dekripsi (byte-level)
# --------------------------------------

# Columnar Transposition - Enkripsi
def enkripsi_bytes_columnar(data: bytes, key_indices: List[int]) -> bytes:
    cols = len(key_indices)
    if cols == 0:
        raise ValueError("Panjang kunci harus >= 1")
    rows = math.ceil(len(data) / cols)
    padded_len = rows * cols
    
    # Padding null bytes
    padded = bytearray(data) + bytearray(padded_len - len(data))
    
    # Buat matrix baris
    matrix = [padded[i * cols: (i + 1) * cols] for i in range(rows)]
    
    # Tentukan urutan baca kolom berdasarkan kunci
    col_order = inverse_mapping_from_key_indices(key_indices)
    
    out = bytearray()
    for read_pos in range(cols):
        col_idx = col_order[read_pos]
        for r in range(rows):
            out.append(matrix[r][col_idx])
    return bytes(out)

# Columnar Transposition - Dekripsi
def dekripsi_bytes_columnar(ct: bytes, key_indices: List[int], original_length: int) -> bytes:
    cols = len(key_indices)
    if cols == 0:
        raise ValueError("Panjang kunci harus >= 1")
    if len(ct) % cols != 0:
        raise ValueError("Panjang ciphertext tidak kompatibel dengan panjang kunci")
    rows = len(ct) // cols
    
    # Siapkan matrix kosong
    matrix = [bytearray(cols) for _ in range(rows)]
    
    # Tentukan urutan kolom
    col_order = inverse_mapping_from_key_indices(key_indices)
    
    idx = 0
    for read_pos in range(cols):
        col_idx = col_order[read_pos]
        for r in range(rows):
            matrix[r][col_idx] = ct[idx]
            idx += 1
    
    # Baca matrix baris-per-baris
    out = bytearray()
    for r in range(rows):
        out.extend(matrix[r])
    
    return bytes(out[:original_length])


# ----------------------
# HMAC helper (opsional)
# ----------------------
def compute_hmac(secret: bytes, data: bytes) -> str:
    """Return hex digest of HMAC-SHA256"""
    return hmac.new(secret, data, hashlib.sha256).hexdigest()


# -------------
# Wrapper JSON
# -------------
def buat_wrapper(cipher_bytes: bytes, nama_file_asli: str, panjang_asli: int, passphrase: str = None) -> bytes:
    """
    Simpan cipher sebagai base64 untuk menghemat ruang dibanding hex.
    Jika passphrase disediakan, simpan HMAC (hex) agar integritas bisa diverifikasi di dekripsi.
    """
    cipher_b64 = base64.b64encode(cipher_bytes).decode()
    wrapper = {
        "magic": MAGIC,
        "filename": nama_file_asli,
        "original_length": panjang_asli,
        "cipher_b64": cipher_b64,
    }
    if passphrase:
        secret = hashlib.sha256(passphrase.encode()).digest()
        wrapper["hmac"] = compute_hmac(secret, cipher_bytes)
    return json.dumps(wrapper).encode()


def parse_wrapper(data: bytes):
    """Parse JSON wrapper robustly; raise ValueError jika invalid."""
    try:
        obj = json.loads(data.decode())
    except Exception:
        raise ValueError("File .tenc rusak atau bukan JSON valid")
    if obj.get("magic") != MAGIC:
        raise ValueError("Bukan file .tenc yang valid")
    if "cipher_b64" not in obj or "filename" not in obj or "original_length" not in obj:
        raise ValueError("File .tenc tidak lengkap atau korup")
    return obj


# ----------------------
# UI: Card-based layout
# ----------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.header("Transpotition Cipher (Columnar)")
st.markdown("</div>", unsafe_allow_html=True)

# Generator Key + Input Manual (satu card)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Generator Kunci Otomatis")
col_a, col_b = st.columns([1, 2])
with col_a:
    panjang_kunci = st.number_input("Panjang kunci (jumlah kolom)", min_value=2, max_value=40, value=4, step=1)
    if st.button("Generate Kunci Random"):
        angka = list(range(1, panjang_kunci + 1))
        random.shuffle(angka)
        kunci_random = "-".join(str(x) for x in angka)
        # langsung isi kunci_input agar user tidak perlu copy-paste
        st.session_state["kunci_input"] = kunci_random
        st.success(f"Kunci random dibuat dan dimasukkan ke input: {kunci_random}")
with col_b:
    st.write("Klik Generate untuk membuat kunci valid acak. Atau masukkan kunci manual di bagian Input Kunci.")
st.markdown("</div>", unsafe_allow_html=True)

# Input manual + validasi realtime (card)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Input Kunci Manual (format: 3-1-4-2)")
# pre-fill from session_state if exists
initial = st.session_state.get("kunci_input", "")
kunci_input = st.text_input("Masukkan kunci numerik (contoh: 3-1-4-2)", value=initial, key="kunci_input_field")
# Validasi realtime
key_idx = None
if kunci_input:
    try:
        key_idx = parse_kunci_numerik(kunci_input)
        st.success("Kunci valid. Indeks internal: " + str(key_idx))
    except Exception as e:
        st.error("Kunci tidak valid: " + str(e))
else:
    st.info("Belum ada kunci. Masukkan kunci numerik atau gunakan generator.")
st.markdown("</div>", unsafe_allow_html=True)

# Enkripsi card
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Enkripsi")
with st.expander("Petunjuk Enkripsi"):
    st.write(
        "Masukkan kunci numerik yang valid. Pilih teks atau unggah file. File terenkripsi akan diunduh sebagai .tenc. "
        "Opsional: masukkan passphrase untuk menambahkan HMAC (integritas)."
    )
kunci_for_encrypt = kunci_input  # gunakan input yang sama
plain_text = st.text_area("Plaintext (opsional — akan di-encode UTF-8)", height=120)
up_file = st.file_uploader("Atau unggah file untuk dienkripsi (opsional)", type=None, key="up_enc")
encrypt_passphrase = st.text_input("Passphrase untuk HMAC (opsional - hanya untuk integritas)", type="password")

if st.button("Enkripsi Sekarang"):
    try:
        if not kunci_for_encrypt:
            st.error("Masukkan kunci numerik terlebih dahulu.")
        else:
            key_idx = parse_kunci_numerik(kunci_for_encrypt)
            if up_file is not None:
                data = up_file.read()
                nama_file = up_file.name
                if len(data) > MAX_UPLOAD_BYTES:
                    st.error(f"File terlalu besar (> {MAX_UPLOAD_BYTES // (1024*1024)} MB). Kurangi ukuran file.")
                    raise ValueError("File terlalu besar")
            else:
                data = plain_text.encode("utf-8")
                nama_file = "plaintext.txt"
            cipher_bytes = enkripsi_bytes_columnar(data, key_idx)
            wrapper = buat_wrapper(cipher_bytes, nama_file, len(data), passphrase=encrypt_passphrase if encrypt_passphrase else None)
            st.download_button("Unduh file terenkripsi (.tenc)", data=wrapper, file_name=(nama_file + ".tenc"))
            # preview kecil (untuk teks) — 64 byte pertama base64
            preview_len = min(64, len(cipher_bytes))
            st.info(f"Preview ciphertext (first {preview_len} bytes base64): {base64.b64encode(cipher_bytes[:preview_len]).decode()}")
            st.success("Enkripsi selesai — unduh .tenc hasil enkripsi.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat enkripsi: {e}")
st.markdown("</div>", unsafe_allow_html=True)

# Dekripsi card
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Dekripsi")
with st.expander("Petunjuk Dekripsi"):
    st.write("Unggah file .tenc dan masukkan kunci numerik yang sama. Jika file dibuat dengan passphrase HMAC, masukkan passphrase yang sama.")
kunci_for_decrypt = st.text_input("Kunci untuk Dekripsi (format: 3-1-4-2)", value=kunci_input, key="kunci_dec_field")
cipher_upload = st.file_uploader("Unggah file .tenc untuk didekripsi", type=["tenc"], key="cipher")
decrypt_passphrase = st.text_input("Passphrase untuk verifikasi HMAC (jika ada)", type="password", key="pass_dec")

if st.button("Dekripsi Sekarang"):
    try:
        if cipher_upload is None:
            st.error("Unggah file .tenc terlebih dahulu.")
        elif not kunci_for_decrypt:
            st.error("Masukkan kunci dekripsi.")
        else:
            key_idx = parse_kunci_numerik(kunci_for_decrypt)
            raw = cipher_upload.read()
            # parse wrapper
            obj = parse_wrapper(raw)
            nama_file = obj["filename"]
            panjang_asli = obj["original_length"]
            cipher_b64 = obj["cipher_b64"]
            try:
                cipher_bytes = base64.b64decode(cipher_b64)
            except Exception:
                raise ValueError("Cipher base64 rusak")
            # jika ada HMAC di wrapper, verifikasi jika user memasukkan passphrase
            if "hmac" in obj:
                if decrypt_passphrase:
                    secret = hashlib.sha256(decrypt_passphrase.encode()).digest()
                    expected = obj["hmac"]
                    actual = compute_hmac(secret, cipher_bytes)
                    if not hmac.compare_digest(expected, actual):
                        st.error("HMAC mismatch — kemungkinan passphrase salah atau file dimodifikasi.")
                        raise ValueError("Integritas gagal (HMAC mismatch)")
                else:
                    st.warning("File ini memiliki HMAC integritas. Pertimbangkan memasukkan passphrase untuk verifikasi.")
            # dekripsi
            pt = dekripsi_bytes_columnar(cipher_bytes, key_idx, panjang_asli)
            st.download_button("Unduh file terdekripsi", data=pt, file_name=("decrypted_" + nama_file))
            # jika bisa decode ke utf-8, tampilkan
            try:
                teks = pt.decode("utf-8")
                st.text_area("Isi file terdekripsi (UTF-8)", value=teks, height=200)
            except Exception:
                st.warning("File terdekripsi bersifat biner atau bukan UTF-8; file telah diunduh.")
            st.success("Dekripsi selesai.")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat dekripsi: {e}")
st.markdown("</div>", unsafe_allow_html=True)

# Footer card: Notes
st.markdown('<div class="card">', unsafe_allow_html=True)
st.header("Notes:")
st.markdown(
"""
- Kunci numerik harus valid dan mencakup angka 1..N (tanpa duplikasi), contoh: `3-1-4-2`.
- Aplikasi mengenkripsi semua **byte**, termasuk header file sehingga file terenkripsi tidak bisa dibuka sampai didekripsi.
- File `.tenc` adalah JSON yang menyimpan ciphertext (base64) dan metadata; base64 dipilih agar ukuran lebih ekonomis daripada hex.
- Jika memilih passphrase saat enkripsi, HMAC SHA256 akan disertakan; passphrase diperlukan untuk verifikasi integritas.
- Padding menggunakan null bytes (0x00); panjang asli disimpan agar bisa dikembalikan persis.
- Batas unggahan standar: 50 MB.
- Metode ini hanya untuk keperluan edukasi/tugas. Bukan untuk keamanan in real life.
"""
)
st.markdown("</div>", unsafe_allow_html=True)
