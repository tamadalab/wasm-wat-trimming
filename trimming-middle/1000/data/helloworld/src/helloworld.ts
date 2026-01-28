// AssemblyScriptのHello World
// コンパイルされると、ホスト環境（ブラウザやNode.js）の console.log を呼び出すインポート関数になります

export function main(): void {
  console.log("Hello, World!");
}

// 読み込み時に実行されるようにトップレベルで呼び出し
main();
