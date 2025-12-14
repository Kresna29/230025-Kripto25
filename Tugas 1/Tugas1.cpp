#include <iostream>
#include <string>
using namespace std;

// Deklarasi fungsi
int mod26(int x);
int modInverse(int a);
void enkripsi(string plaintext, int key[2][2]);
void dekripsi(string ciphertext, int key[2][2]);

// Main program
int main() 
{
    int key[2][2] = 
    {
        {7, 6},
        {2, 5}
    };

    string plaintext  = "PYTHON";
    string ciphertext = "PUTVUP";

    cout << "=== Hill Cipher 2x2 ===" << endl;
    cout << "Plaintext  : " << plaintext << endl;

    enkripsi(plaintext, key);
    dekripsi(ciphertext, key);

    return 0;
}

// Definisi fungsi

// Fungsi modulo 26 (menangani bilangan negatif)
int mod26(int x) 
{
    return (x % 26 + 26) % 26;
}

// Fungsi mencari invers modulo 26
int modInverse(int a) 
{
    for (int i = 0; i < 26; i++) 
    {
        if ((a * i) % 26 == 1)
            return i;
    }
    return -1;
}

// Fungsi enkripsi Hill Cipher
void enkripsi(string plaintext, int key[2][2]) 
{
    cout << "Ciphertext : ";
    for (int i = 0; i < plaintext.length(); i += 2) 
    {
        int p1 = plaintext[i] - 'A';
        int p2 = plaintext[i + 1] - 'A';

        int c1 = mod26(key[0][0] * p1 + key[0][1] * p2);
        int c2 = mod26(key[1][0] * p1 + key[1][1] * p2);

        cout << char(c1 + 'A') << char(c2 + 'A');
    }
    cout << endl;
}

// Fungsi dekripsi Hill Cipher
void dekripsi(string ciphertext, int key[2][2]) 
{
    int det = mod26(key[0][0] * key[1][1] - key[0][1] * key[1][0]);
    int detInv = modInverse(det);

    if (detInv == -1) 
    {
        cout << "Matriks kunci tidak memiliki invers modulo 26" << endl;
        return;
    }

    int invKey[2][2];
    invKey[0][0] = mod26( key[1][1] * detInv);
    invKey[0][1] = mod26(-key[0][1] * detInv);
    invKey[1][0] = mod26(-key[1][0] * detInv);
    invKey[1][1] = mod26( key[0][0] * detInv);

    cout << "Plaintext  : ";
    for (int i = 0; i < ciphertext.length(); i += 2) 
    {
        int c1 = ciphertext[i] - 'A';
        int c2 = ciphertext[i + 1] - 'A';

        int p1 = mod26(invKey[0][0] * c1 + invKey[0][1] * c2);
        int p2 = mod26(invKey[1][0] * c1 + invKey[1][1] * c2);

        cout << char(p1 + 'A') << char(p2 + 'A');
    }
    cout << endl;
}