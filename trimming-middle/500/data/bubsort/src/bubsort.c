#include <stdio.h>

// バブルソート関数
void bubbleSort(int arr[], int n) {
    int i, j, temp;
    for (i = 0; i < n - 1; i++) {
        for (j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                // 要素の入れ替え
                temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

// 実行用メイン関数
int main() {
    int arr[] = {64, 34, 25, 12, 22, 11, 90, 88, 15, 76};
    int n = sizeof(arr) / sizeof(arr[0]);

    // ソート実行
    bubbleSort(arr, n);

    // 結果出力（これをしないと最適化で処理ごと消える可能性があるため）
    printf("Sorted array: \n");
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");

    return 0;
}
