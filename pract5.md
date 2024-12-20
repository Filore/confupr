## Задание 1

```
import dis

def foo(x):
    while x:
        x -= 1
    return x + 1

print(dis.dis(foo))
```

```
 3           0 LOAD_FAST                0 (x)
        >>    2 POP_JUMP_IF_FALSE       16

  4           4 LOAD_FAST                0 (x)
              6 LOAD_CONST               1 (1)
              8 INPLACE_SUBTRACT
             10 STORE_FAST               0 (x)
             12 JUMP_ABSOLUTE            2

  5     >>   16 LOAD_FAST                0 (x)
             18 LOAD_CONST               1 (1)
             20 BINARY_ADD
             22 RETURN_VALUE
```

Опишите по шагам, что делает каждая из следующих команд (приведите эквивалентное выражение на Python):

```
11   0 LOAD_FAST                0 (x)
     2 LOAD_CONST               1 (10)
     4 BINARY_MULTIPLY
     6 LOAD_CONST               2 (42)
     8 BINARY_ADD
    10 RETURN_VALUE
```

0 LOAD_FAST 0 (x) Загружает значение локальной переменной x в стек. Эквивалент: значение x готово для дальнейших операций.

2 LOAD_CONST 1 (10) Загружает константу 10 в стек. Эквивалент: значение 10 помещено в стек.

4 BINARY_MULTIPLY Извлекает два верхних значения из стека (x и 10) и умножает их. Результат помещается обратно в стек. Эквивалент на Python: x * 10

6 LOAD_CONST 2 (42) Загружает константу 42 в стек. Эквивалент: значение 42 добавлено в стек.

8 BINARY_ADD Извлекает два верхних значения из стека (temp_result и 42) и складывает их. Результат помещается обратно в стек. Эквивалент: x * 10 + 42

10 RETURN_VALUE Извлекает верхнее значение из стека и возвращает его как результат выполнения функции. Эквивалент: return x * 10 + 42

## Задание 2

```
  5           0 LOAD_CONST               1 (1)
              2 STORE_FAST               1 (r)

  6     >>    4 LOAD_FAST                0 (n)
              6 LOAD_CONST               1 (1)
              8 COMPARE_OP               4 (>)
             10 POP_JUMP_IF_FALSE       30

  7          12 LOAD_FAST                1 (r)
             14 LOAD_FAST                0 (n)
             16 INPLACE_MULTIPLY
             18 STORE_FAST               1 (r)

  8          20 LOAD_FAST                0 (n)
             22 LOAD_CONST               1 (1)
             24 INPLACE_SUBTRACT
             26 STORE_FAST               0 (n)
             28 JUMP_ABSOLUTE            4

  9     >>   30 LOAD_FAST                1 (r)
             32 RETURN_VALUE
```

LOAD_CONST 1 (1) Загружает константу 1 в стек. Это начальное значение для переменной r.

STORE_FAST 1 (r) Сохраняет значение 1 из стека в локальную переменную r.

LOAD_FAST 0 (n) Загружает значение переменной n в стек.

LOAD_CONST 1 (1) Загружает константу 1 в стек.

COMPARE_OP 4 (>) Сравнивает n и 1 на предмет того, больше ли n единицы.

POP_JUMP_IF_FALSE 30 Если результат сравнения n > 1 — False, то переход к строке 30 (к завершению функции). Иначе выполняется тело цикла.

Тело цикла (строки 12–28): LOAD_FAST 1 (r) Загружает значение r в стек.

LOAD_FAST 0 (n) Загружает значение n в стек.

INPLACE_MULTIPLY Умножает r на n и сохраняет результат в r.

STORE_FAST 1 (r) Обновляет значение переменной r на r * n.

LOAD_FAST 0 (n) Загружает значение n в стек.

LOAD_CONST 1 (1) Загружает константу 1 в стек.

INPLACE_SUBTRACT Уменьшает n на 1.

STORE_FAST 0 (n) Обновляет значение n на n - 1.

JUMP_ABSOLUTE 4 Переходит обратно к началу цикла (в строку 4), чтобы снова проверить условие n > 1.

Завершение функции: LOAD_FAST 1 (r) Загружает значение r в стек (это результат вычисления факториала).

RETURN_VALUE Возвращает значение r как результат выполнения функции.

```
def factorial(n):
    r = 1
    while n > 1:
        r *= n
        n -= 1
    return r
```

## Задание 3

Java
```
package ru.qq;
public class Main {
    public static void main(String[] args) {
        foo(10);
    }

    private static int foo(int x){
        int result = (x * 10) + 42;
        return result;
    }
}
```

C#
```
using System;
namespace Ru.Qq
{
    class Program
    {
        static void Main(string[] args)
        {
            int result = Foo(10);
            Console.WriteLine(result);
        }

        private static int Foo(int x)
        {
            int result = (x * 10) + 42;
            return result;
        }
    }
}
```
