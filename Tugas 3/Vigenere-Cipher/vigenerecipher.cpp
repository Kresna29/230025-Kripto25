#include <iostream>
#include <string>
using namespace std;

// Deklarasi Fungsi
string vigenereEncrypt(string plaintext, string key);
string vigenereDecrypt(string ciphertext, string key);

// Main Program
int main()
{
    string plaintext = "ASPRAKGANTENG";
    string key = "BAYU";

    string cipher = vigenereEncrypt(plaintext, key);
    cout << "Ciphertext : " << cipher << endl;
    cout << "Plaintext  : " << vigenereDecrypt(cipher, key) << endl;

    return 0;
}

// Definisi Fungsi

// Enkripsi Vigenere
string vigenereEncrypt(string plaintext, string key)
{
    string cipher = "";
    int j = 0;

    for (int i = 0; i < plaintext.length(); i++)
    {
        char p = toupper(plaintext[i]);
        if (p >= 'A' && p <= 'Z')
        {
            int P = p - 'A';
            int K = toupper(key[j % key.length()]) - 'A';
            int C = (P + K) % 26;
            cipher += char(C + 'A');
            j++;
        }
    }
    return cipher;
}

// Dekripsi Vigenere
string vigenereDecrypt(string ciphertext, string key)
{
    string plain = "";
    int j = 0;

    for (int i = 0; i < ciphertext.length(); i++)
    {
        char c = toupper(ciphertext[i]);
        if (c >= 'A' && c <= 'Z')
        {
            int C = c - 'A';
            int K = toupper(key[j % key.length()]) - 'A';
            int P = (C - K + 26) % 26;
            plain += char(P + 'A');
            j++;
        }
    }
    return plain;
}
