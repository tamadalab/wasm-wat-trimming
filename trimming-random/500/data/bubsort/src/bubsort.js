// バブルソートの実装
function bubbleSort(arr) {
  var len = arr.length;
  var swapped;

  for (var i = 0; i < len - 1; i++) {
    swapped = false;
    for (var j = 0; j < len - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        // 要素の入れ替え
        var temp = arr[j];
        arr[j] = arr[j + 1];
        arr[j + 1] = temp;
        swapped = true;
      }
    }
    // 一度も交換が行われなければソート完了
    if (!swapped) break;
  }
  return arr;
}

// メイン処理
var data = [64, 34, 25, 12, 22, 11, 90, 88, 15, 76];
// Javyなどの環境では console.log が標準出力に出ない場合がありますが、
// 構造解析用コードとしてはロジックが存在することが重要です。
bubbleSort(data);
