#include <stdio.h>
#include <ctype.h>
#include <stdbool.h>

// 単語数を数える関数
int countWords(const char *text) {
    int count = 0;
    bool inWord = false;

    for (const char *p = text; *p; p++) {
        // 空白文字かどうかを判定
        if (isspace(*p)) {
            inWord = false;
        } else if (!inWord) {
            // 空白から文字に変わった瞬間をカウント
            inWord = true;
            count++;
        }
    }
    return count;
}

int main() {
    const char *text = "WebAssembly is a binary instruction format for a stack-based virtual machine";
    
    printf("Text: %s\n", text);
    
    int count = countWords(text);
    printf("Word Count: %d\n", count);

    return 0;
}