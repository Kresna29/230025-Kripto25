#include <iostream>
#include <vector>
using namespace std;

// Deklarasi Fungsi
long long modExp(long long base, long long exp, long long mod);
pair<long long, long long> elgamalEncrypt(
    long long m, long long p, long long g, long long y, long long k);
long long elgamalDecrypt(long long c, long long a, long long x, long long p);

// Main Program
int main()
{
    long long p = 37, g = 3, x = 2, k = 15;
    long long y = modExp(g, x, p);

    string plaintext = "EZKRIPTOGRAFI";
    vector<pair<long long, long long>> ciphertext;

    cout << "Ciphertext (a, c):" << endl;
    for (char ch : plaintext)
    {
        long long m = ch - 'A';
        auto enc = elgamalEncrypt(m, p, g, y, k);
        ciphertext.push_back(enc);
        cout << "(" << enc.first << ", " << enc.second << ") ";
    }

    cout << "\nDecryption Result: ";
    for (auto c : ciphertext)
    {
        long long m = elgamalDecrypt(c.second, c.first, x, p);
        cout << char(m + 'A');
    }

    return 0;
}

// Definisi Fungsi

long long modExp(long long base, long long exp, long long mod)
{
    long long result = 1;
    while (exp > 0)
    {
        if (exp % 2 == 1)
            result = (result * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return result;
}

pair<long long, long long> elgamalEncrypt(
    long long m, long long p, long long g, long long y, long long k)
{
    long long a = modExp(g, k, p);
    long long b = modExp(y, k, p);
    long long c = (m * b) % p;
    return make_pair(a, c);
}

long long elgamalDecrypt(long long c, long long a, long long x, long long p)
{
    long long ax = modExp(a, x, p);
    long long inv = modExp(ax, p - 2, p); // invers modulo
    return (c * inv) % p;
}
