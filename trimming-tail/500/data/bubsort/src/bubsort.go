package main

import "fmt"

// バブルソート関数
func bubbleSort(arr []int) {
	n := len(arr)
	sorted := false
	for !sorted {
		sorted = true
		for i := 0; i < n-1; i++ {
			if arr[i] > arr[i+1] {
				// スワップ（Go言語特有の書き方）
				arr[i], arr[i+1] = arr[i+1], arr[i]
				sorted = false
			}
		}
	}
}

func main() {
	data := []int{64, 34, 25, 12, 22, 11, 90, 88, 15, 76}
	
	fmt.Println("Original:", data)
	
	bubbleSort(data)
	
	fmt.Println("Sorted:", data)
}