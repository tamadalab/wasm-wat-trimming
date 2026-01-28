// AssemblyScript用のバブルソート実装
// 配列の要素は32ビット整数(i32)として扱います

export function bubbleSort(arr: i32[]): i32[] {
  let len = arr.length;
  let swapped: boolean;

  for (let i = 0; i < len - 1; i++) {
    swapped = false;
    for (let j = 0; j < len - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        // 要素の入れ替え
        let temp = arr[j];
        arr[j] = arr[j + 1];
        arr[j + 1] = temp;
        swapped = true;
      }
    }
    if (!swapped) break;
  }
  return arr;
}

// 実行用コード（コンパイル時にコードを含めるため）
const data: i32[] = [64, 34, 25, 12, 22, 11, 90, 88, 15, 76];
bubbleSort(data);
