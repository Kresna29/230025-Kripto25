# Steganografi LSB (C++)

## Deskripsi Program
Program ini mengimplementasikan **Steganografi menggunakan metode Least Significant Bit (LSB)** untuk **menyisipkan (encode)** dan **mengambil kembali (decode)** pesan teks ke dalam file gambar atau file biner.

Metode LSB bekerja dengan cara **mengganti bit paling tidak signifikan (LSB)** dari setiap byte data file dengan bit pesan, sehingga perubahan yang terjadi tidak terlihat secara visual.

- **Encode:** Menyisipkan pesan teks ke dalam file cover dan menghasilkan file stego.
- **Decode:** Mengambil kembali pesan tersembunyi dari file stego.

Program bekerja dalam **mode file biner**, sehingga dapat digunakan pada file gambar seperti **BMP atau PNG** (disarankan).

---

## Alur Program
1. Program menampilkan **menu utama** (Encode, Decode, Keluar).
2. Jika user memilih **Encode**:
   - User memasukkan nama file cover dan pesan teks.
   - Program membaca file cover dalam mode biner.
   - Panjang pesan disimpan dalam **header 32 bit**.
   - Pesan diubah menjadi bit dan digabung dengan header.
   - Bit pesan disisipkan ke **LSB setiap byte file**.
   - File hasil disimpan dengan nama **`namafile_stego`** dan **ekstensi yang sama dengan file asli**.
3. Jika user memilih **Decode**:
   - Program membaca file stego dalam mode biner.
   - 32 bit pertama dibaca sebagai header untuk mengetahui panjang pesan.
   - Bit pesan diambil sesuai panjang header.
   - Bit dikonversi kembali menjadi teks asli.
4. Pesan hasil decode ditampilkan di console.

## Cara Menjalankan
1. Compile program:
   ```bash
   g++ LSB.cpp -o LSB
   ```
2. Jalankan program:
   ```bash
   ./LSB
   ```

## Output
![Hasil Running Program](Hasil_Running1.png)
![Hasil Running Program](Hasil_Running2.png)