// コラッツ数列のステップ数を計算する関数
// no_mangle: コンパイル後も関数名 "collatz_steps" を維持する
// extern "C": C言語形式の呼び出し規約を使用（Wasmから呼びやすくするため）
#[no_mangle]
pub extern "C" fn collatz_steps(mut n: i32) -> i32 {
    let mut steps = 0;
    while n > 1 {
        if n % 2 == 0 {
            n = n / 2;
        } else {
            n = 3 * n + 1;
        }
        steps += 1;
    }
    steps
}