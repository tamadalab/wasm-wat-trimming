package main

import "fmt"

// コラッツ数列のステップ数を計算する関数
func collatzSteps(n int) int {
	steps := 0
	for n > 1 {
		if n%2 == 0 {
			n = n / 2
		} else {
			n = 3*n + 1
		}
		steps++
	}
	return steps
}

func main() {
	// いくつかの数値でシミュレーションを実行
	targets := []int{27, 871, 6171}

	fmt.Println("Running Collatz Conjecture...")

	for _, n := range targets {
		steps := collatzSteps(n)
		fmt.Printf("Number: %d -> Steps: %d\n", n, steps)
	}
}