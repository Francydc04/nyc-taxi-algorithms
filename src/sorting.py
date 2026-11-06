"""Six classic sorting algorithms, implemented from scratch.

Every function returns a new list sorted in *descending* order and leaves the
input untouched, so they can be benchmarked on the same data one after another.
"""

from typing import List


def bubble_sort(values: List[float]) -> List[float]:
    data = list(values)
    n = len(data)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if data[j] < data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                swapped = True
        if not swapped:  # already sorted: stop early (best case O(n))
            break
    return data


def selection_sort(values: List[float]) -> List[float]:
    data = list(values)
    n = len(data)
    for i in range(n - 1):
        largest = i
        for j in range(i + 1, n):
            if data[j] > data[largest]:
                largest = j
        data[i], data[largest] = data[largest], data[i]
    return data


def insertion_sort(values: List[float]) -> List[float]:
    data = list(values)
    for i in range(1, len(data)):
        key = data[i]
        j = i - 1
        while j >= 0 and data[j] < key:
            data[j + 1] = data[j]
            j -= 1
        data[j + 1] = key
    return data


def merge_sort(values: List[float]) -> List[float]:
    if len(values) <= 1:
        return list(values)
    mid = len(values) // 2
    left, right = merge_sort(values[:mid]), merge_sort(values[mid:])
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] >= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def quick_sort(values: List[float]) -> List[float]:
    if len(values) <= 1:
        return list(values)
    pivot = values[len(values) // 2]
    bigger = [x for x in values if x > pivot]
    equal = [x for x in values if x == pivot]  # three-way split handles the many duplicate fares/passenger counts
    smaller = [x for x in values if x < pivot]
    return quick_sort(bigger) + equal + quick_sort(smaller)


def heap_sort(values: List[float]) -> List[float]:
    data = list(values)

    def sift_down(n: int, i: int) -> None:  # iterative, so no recursion limit on large inputs
        while True:
            smallest, left, right = i, 2 * i + 1, 2 * i + 2
            if left < n and data[left] < data[smallest]:
                smallest = left
            if right < n and data[right] < data[smallest]:
                smallest = right
            if smallest == i:
                return
            data[i], data[smallest] = data[smallest], data[i]
            i = smallest

    n = len(data)
    for i in range(n // 2 - 1, -1, -1):  # build a min-heap
        sift_down(n, i)
    for end in range(n - 1, 0, -1):  # move the current minimum to the back
        data[0], data[end] = data[end], data[0]
        sift_down(end, 0)
    return data


ALGORITHMS = {
    "Bubble sort": bubble_sort,
    "Selection sort": selection_sort,
    "Insertion sort": insertion_sort,
    "Merge sort": merge_sort,
    "Quick sort": quick_sort,
    "Heap sort": heap_sort,
}
QUADRATIC = {"Bubble sort", "Selection sort", "Insertion sort"}
