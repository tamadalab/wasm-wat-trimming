#include <stdio.h>

// FizzBuzzのロジック
void fizzBuzz(int n) {
    if (n % 15 == 0) {
        printf("FizzBuzz\n");
    } else if (n % 3 == 0) {
        printf("Fizz\n");
    } else if (n % 5 == 0) {
        printf("Buzz\n");
    } else {
        printf("%d\n", n);
    }
}

int main() {
    // 1から30まで実行
    for (int i = 1; i <= 30; i++) {
        fizzBuzz(i);
    }
    return 0;
}