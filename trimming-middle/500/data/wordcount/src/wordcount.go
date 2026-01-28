package main

import (
	"fmt"
	"strings"
)

// 単語数を数える関数
func countWords(text string) int {
	// 空白で分割してスライスにする
	words := strings.Fields(text)
	return len(words)
}

func main() {
	text := "WebAssembly is a binary instruction format for a stack-based virtual machine"
	
	fmt.Println("Text:", text)
	
	count := countWords(text)
	fmt.Printf("Word Count: %d\n", count)
}