## Куча

*Куча* — корневое дерево со свойством кучи.
Свойство min кучи: для любой вершины $\forall v$: $key(v) \geqslant key(parent(v))$; значение в каждом узле не меньше значения в родителе.

*Двоичная куча* — полное двоичное дерево (все, кроме последнего, слои заняты) со свойством кучи.
Можно реализовать на массиве.
```
left(v)   = 2v
right(v)  = 2v + 1
parent(v) = v div 2
Индексация с единицы, v = 1..n
```
Высота двоичной кучи = $\log_2(n) \pm 1$ (????????)

### Операции над кучей

* `heapify(v)`: в детях свойство кучи выполняется, в самой вершине, возможно, нет. Надо исправить.
    ```python
    def heapify(v):
        if (left(v)) <= size and key(left(v)) <= key(v):
            m = left(v)
        if right(v) <= size and key(left(m)) <= key(m):
            m = right(v)
        if m != v:
            heap[m], heap[v] = heap[v], heap[m]
            heapify(m)  # свойство кучи в поддереве могло нарушиться
    ```
    $O(\text{heapify}) = O(\log n)$
* `make_heap()`: превращает массив в кучу.
    ```python
    def make_heap():
        # i = n // 2 — первый элемент на предпоследнем уровне дерева
        for i in range(n // 2, 0, -1):
            heapify(i1)
    ```
    $O(\text{make\_heap}) = O(n \log n)$ — наивная оценка.
    $$T(n) = \sum\limits_{h=1}^{log_2 n} \frac{n}{2^h} O(h) = n\cdot O(1) \left(\sum\limits_{h=1}^{log_2 n} \frac{h}{2^h} \right)$$

    $$\sum\limits_{k=0}^{\infty} a^k = \frac 1 {1 - a}$$

    $$\left(\sum\limits_{k=0}^{\infty} a^k = \frac 1 {1 - a}\right)' = \sum\limits_{k=0}^{\infty} \frac{k}{a^{k -1}} = O(1)$$

    Таким образом $O(\text{make\_heap}) = \Theta(n)$
* `extract_min` — удалить минимальный элемент.
    Меняем местами первый (мниальный) и последний элемент, после чего восстановить порядок.
    ```python
    def extract_min():
        min_value = heap[1]
        heap[1] = heap[size]
        size -= 1
        heapify(1)
    ```
    $O(\text{extract\_min}) = O(\log n)$
* `decrease_key` — всплытие элемента
    ```python
    def decrease_key(i):
        while parent(i) > 0:
            if key(parent(i)) > key(i):
                heap[i], heap[parent(i)] = heap[parent(i)], heap[i]
                i = parent(i)
            else:
                break  # все стало хорошо, дальше всплывать не надо
    ```
    $O(\text{decrease\_key}) = O(\log n)$
* `insert` — вставить элемент в кучу.
    ```python
    def insert(x):
        size += 1
        heap[size] = x
        i = size
        decrease_key(i)
    ```
    $O(\text{insert}) = O(\log n)$
    Таким образом сделать кучу процедурой `make_heap` быстрее, чем вставлять элементы по одному.

### K-ичная куча

* `heapify`: $k \log_k n$
* `insert`: $\log_k n$
* `decrease_key`: $\log_k n$
* `extract_min`: $k \log_k n$

### Применение кучи

* *Очередь с приоритетами*
* *Сортировка кучей*

## Линейные сортировки

Нижняя оценка на сортировки **сравнениями**: сортировка $n$ элементов требует $\Omega(n \log n)$ операций. Линейные сортировки работают быстрее, если про них известно что-то еще, кроме операции сравнения.

### Counting sort (сортировка подсчетом)

Если в массиве хранятся простые элементы из небольшого множества (числа от $1$ до $100$, `char`).
$n$ — размер массива, $m$ — максимальное значение элементов в массиве.

Алгоритм: считаем, сколько раз каждый элемент встречается, потом по массиву с подсчитанными элементами восстанавливаем отсортированный массив.

Время: $O(n+m)$, память: $O(m)$. Сортировка стабильная.

Если помимо ключей в массиве интересуют еще и связанные значения, то в вспомогательном массиве храним индексы элементов в отсортированном массиве.

```python
def counting_sort(a, m):
    b = [0 for i in range(m)]
    # подсчет
    for x in a:
        b[a[i]] += 1
    # массив индексов
    c = [0 for i in range(m)]
    for i in range(2, len(b)):
        c[i] = c[i - 1] + b[i - 1]
    # восстановление ответа
    res = [o for i in range(n)]
    for i in range(n):
        res[c[a[i]]] = a[i]
        c[a[i]] += 1
    return res
```

### Radix sort (поразрядная сортировка)

Элементы, которые мы сортируем сами по себе последовательности элементов (строки, длинные числа).

Сначала сортируем по последнему разряду сортировкой подсчетом. Потом по предпоследнему. И так далее. (Сначала единицы, потом десятки, потом сотни...)

Если $n$ — число элементов, а $d$ — число разрядов, то:

Время: $O(n+d)$, память: $O(d)$. Сортировка стабильная.

### Bucket sort

Допустим есть вещественные числа, равномерно распределенные по какому-то отрезку. $n$ чисел, $n$ bucket'ов (разбить исходный отрезок на $n$ частей). Если в один bucket попадает больше одной точки, то сортируем его любой сортировкой (вероятность таких случаев крайне мала). Выписываем все элементы из всех bucket'ов.

Если входные данные хорошие, то работает за $O(n)$.