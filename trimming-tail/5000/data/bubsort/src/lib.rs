// Rustの標準的な機能を使わない（no_std）設定にするとさらに小さくなりますが、
// 今回は比較のため標準ライブラリ有りで記述します。

#[no_mangle] // 関数名をマングリング（変更）せず、Wasmからそのまま呼べるようにする
pub extern "C" fn bubble_sort(ptr: *mut i32, len: usize) {
    // 生ポインタからスライスを安全に生成
    let arr = unsafe { std::slice::from_raw_parts_mut(ptr, len) };
    let n = arr.len();

    // バブルソートの実装
    for i in 0..n {
        for j in 0..n - 1 - i {
            if arr[j] > arr[j + 1] {
                arr.swap(j, j + 1);
            }
        }
    }
}