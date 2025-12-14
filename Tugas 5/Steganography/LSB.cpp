#include <iostream>
#include <vector>
#include <fstream>
#include <string>

using namespace std;

// DEKLARASI FUNGSI

vector<int> bytesToBits(const vector<unsigned char>& data);
vector<unsigned char> bitsToBytes(const vector<int>& bits);
vector<int> intTo32Bits(int n);
int bits32ToInt(const vector<int>& bits);

void encode(const string& gambarFile, const string& outputFile, const string& message);
void decode(const string& stegoFile);

// MAIN PROGRAM

int main()
{
    int pilihan;
    string gambar, stego, pesan;

    do
    {
        cout << "\n=== STEGANOGRAFI LSB (C++) ===" << endl;
        cout << "1. Encode" << endl;
        cout << "2. Decode" << endl;
        cout << "3. Keluar" << endl;
        cout << "Pilih menu: ";
        cin >> pilihan;
        cin.ignore();

        if (pilihan == 1)
        {
            cout << "Nama file gambar: ";
            getline(cin, gambar);

            cout << "Masukkan pesan: ";
            getline(cin, pesan);

            // Membuat nama output: namafile_stego.ext
            string output;
            size_t pos = gambar.find_last_of('.');

            if (pos != string::npos)
            {
                output = gambar.substr(0, pos) + "_stego" + gambar.substr(pos);
            }
            else
            {
                output = gambar + "_stego.bin";
            }

            encode(gambar, output, pesan);
        }
        else if (pilihan == 2)
        {
            cout << "Nama file stego: ";
            getline(cin, stego);
            decode(stego);
        }
    }
    while (pilihan != 3);

    return 0;
}

// DEFINISI FUNGSI

vector<int> bytesToBits(const vector<unsigned char>& data)
{
    vector<int> bits;
    for (unsigned char b : data)
    {
        for (int i = 7; i >= 0; i--)
        {
            bits.push_back((b >> i) & 1);
        }
    }
    return bits;
}

vector<unsigned char> bitsToBytes(const vector<int>& bits)
{
    vector<unsigned char> bytes;
    for (size_t i = 0; i < bits.size(); i += 8)
    {
        unsigned char value = 0;
        for (int j = 0; j < 8; j++)
        {
            value = (value << 1) | bits[i + j];
        }
        bytes.push_back(value);
    }
    return bytes;
}

vector<int> intTo32Bits(int n)
{
    vector<int> bits;
    for (int i = 31; i >= 0; i--)
    {
        bits.push_back((n >> i) & 1);
    }
    return bits;
}

int bits32ToInt(const vector<int>& bits)
{
    int value = 0;
    for (int bit : bits)
    {
        value = (value << 1) | bit;
    }
    return value;
}

void encode(const string& gambarFile, const string& outputFile, const string& message)
{
    ifstream in(gambarFile, ios::binary);
    if (!in)
    {
        cout << "File gambar tidak ditemukan!" << endl;
        return;
    }

    vector<unsigned char> imageData((istreambuf_iterator<char>(in)), istreambuf_iterator<char>());
    in.close();

    vector<unsigned char> msgBytes(message.begin(), message.end());
    vector<int> headerBits = intTo32Bits(msgBytes.size());
    vector<int> msgBits = bytesToBits(msgBytes);

    vector<int> allBits = headerBits;
    allBits.insert(allBits.end(), msgBits.begin(), msgBits.end());

    if (allBits.size() > imageData.size())
    {
        cout << "Pesan terlalu besar untuk file ini!" << endl;
        return;
    }

    for (size_t i = 0; i < allBits.size(); i++)
    {
        imageData[i] = (imageData[i] & 0xFE) | allBits[i];
    }

    ofstream out(outputFile, ios::binary);
    out.write(reinterpret_cast<char*>(imageData.data()), imageData.size());
    out.close();

    cout << "Encode berhasil! File stego: " << outputFile << endl;
}

void decode(const string& stegoFile)
{
    ifstream in(stegoFile, ios::binary);
    if (!in)
    {
        cout << "File stego tidak ditemukan!" << endl;
        return;
    }

    vector<unsigned char> imageData((istreambuf_iterator<char>(in)), istreambuf_iterator<char>());
    in.close();

    vector<int> headerBits;
    for (int i = 0; i < 32; i++)
    {
        headerBits.push_back(imageData[i] & 1);
    }

    int msgLength = bits32ToInt(headerBits);

    vector<int> msgBits;
    for (int i = 32; i < 32 + msgLength * 8; i++)
    {
        msgBits.push_back(imageData[i] & 1);
    }

    vector<unsigned char> msgBytes = bitsToBytes(msgBits);
    string message(msgBytes.begin(), msgBytes.end());

    cout << "Pesan tersembunyi: " << message << endl;
}