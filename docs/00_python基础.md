# Python 基础

## 类型注解

Python 函数可以在参数和返回值上添加类型注解：

```python
def add(a: int, b: int) -> int:
    return a + b
```

运行时可以通过函数的 `__annotations__` 属性访问这些注解：

```python
print(add.__annotations__)
```

输出：

```python
{
    'a': int,
    'b': int,
    'return': int
}
```

说明：类型注解是运行时可访问的数据。
