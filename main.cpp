/*#include <iostream>
#include <cctype>
using namespace std;

int main() {
    string s;
    cin >> s;

    int vowels = 0, consonants = 0;
    for(char c : s) {
        c = tolower(c);
        if(c == 'a'  c == 'e'  c == 'i'  c == 'o'  c == 'u') {
            vowels++;
        } else if(isalpha(c)) {
            consonants++;
        }
    }

    cout << vowels << " " << consonants << endl;
    return 0;
}
#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    string s;
    cin >> s;
    reverse(s.begin(), s.end());
    cout << s << endl;
    return 0;
}
#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    string s;
    cin >> s;
    string original = s;
    reverse(s.begin(), s.end());

    if(original == s) {
        cout << "Yes" << endl;
    } else {
        cout << "No" << endl;
    }

    return 0;
}
#include <iostream>
#include <map>
using namespace std;

int main() {
    string s;
    cin >> s;

    map<char, int> freq;
    for(char c : s) {
        freq[c]++;
    }

    char max_char;
    int max_count = 0;
    for(auto pair : freq) {
        if(pair.second > max_count) {
            max_count = pair.second;
            max_char = pair.first;
        }
    }

    cout << max_char << endl;
    return 0;
}
#include <iostream>
#include <unordered_set>
using namespace std;

int main() {
    string s;
    cin >> s;

    unordered_set<char> seen;
    string result;

    for(char c : s) {
        if(seen.find(c) == seen.end()) {
            seen.insert(c);
            result += c;
        }
    }

    cout << result << endl;
    return 0;
}
#include <iostream>
#include <sstream>
#include <vector>
using namespace std;

int main() {
    string line;
    getline(cin, line);

    istringstream iss(line);
    string word;
    string longest_word;
    int max_length = 0;

    while(iss >> word) {
        if(word.length() > max_length) {
            max_length = word.length();
            longest_word = word;
        }
    }

    cout << longest_word << endl;
    return 0;
}
#include <iostream>
#include <algorithm>
using namespace std;

int main() {
    string s1, s2;
    cin >> s1 >> s2;

    if(s1.length() != s2.length()) {
        cout << "No" << endl;
        return 0;
    }

    sort(s1.begin(), s1.end());
    sort(s2.begin(), s2.end());

    if(s1 == s2) {
        cout << "Yes" << endl;
    } else {
        cout << "No" << endl;
    }

    return 0;
}*/