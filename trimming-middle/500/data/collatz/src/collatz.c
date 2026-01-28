#include <stdio.h>

// コラッツ数列のステップ数を計算する関数
int collatzSteps(int n) {
    int steps = 0;
    while (n > 1) {
        if (n % 2 == 0) {
            n = n / 2;
        } else {
            n = 3 * n + 1;
        }
        steps++;
    }
    return steps;
}

int main() {
    // いくつかの数値でシミュレーションを実行
    int targets[] = {27, 871, 6171};
    int len = sizeof(targets) / sizeof(targets[0]);

    printf("Running Collatz Conjecture...\n");

    for (int i = 0; i < len; i++) {
        int n = targets[i];
        int steps = collatzSteps(n);
        printf("Number: %d -> Steps: %d\n", n, steps);
    }

    return 0;
}