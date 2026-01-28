// コラッツ数列のステップ数を計算する関数
function collatzSteps(n) {
  var steps = 0;
  while (n > 1) {
    if (n % 2 === 0) {
      n = n / 2;
    } else {
      n = 3 * n + 1;
    }
    steps++;
  }
  return steps;
}

// メイン処理
var targets = [27, 871, 6171];
console.log("Running Collatz Conjecture...");

for (var i = 0; i < targets.length; i++) {
  var n = targets[i];
  var steps = collatzSteps(n);
  console.log("Number: " + n + " -> Steps: " + steps);
}
