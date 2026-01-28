package main

import (
	"fmt"
	"strconv"
)

// FizzBuzzのロジック
func fizzBuzz(n int) string {
	if n%15 == 0 {
		return "FizzBuzz"
	} else if n%3 == 0 {
		return "Fizz"
	} else if n%5 == 0 {
		return "Buzz"
	}
	return strconv.Itoa(n)
}

func main() {
	// 1から30まで実行
	for i := 1; i <= 30; i++ {
		result := fizzBuzz(i)
		fmt.Println(result)
	}
}