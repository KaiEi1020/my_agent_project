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

---

## 三元表达式

Python 的条件表达式

```python
combined = old_dict.copy() if old_dict else {}
```

格式：

```python
A if 条件 else B
```

相当于：

```python
if 条件:
    A
else:
    B
```

---

## `if not x` 语法

### 含义

```python
if not x:
```

等价于：

```python
if bool(x) == False:
```

判断的是 `x` 是否为 **falsy**。

### Falsy 值

以下值在 `bool()` 中为 `False`：

| 值 | 说明 |
|---|---|
| `False` | 布尔假值 |
| `None` | 空值 |
| `0` / `0.0` / `0j` | 数字零 |
| `""` | 空字符串 |
| `[]` | 空列表 |
| `()` | 空元组 |
| `{}` | 空字典 |
| `set()` | 空集合 |

---

## 异步编程核心语法

### async def

定义一个异步函数，返回的是一个**协程（Coroutine）**对象，不会立即执行：

```python
async def main():
    print("hello")

main()          # <coroutine object main at 0x...>
await main()    # 正确：在另一个 async 函数内调用
asyncio.run(main())  # 正确：作为程序入口运行
```

等价于 JavaScript：

```javascript
async function main() {
  console.log("hello")
}
```

### await

暂停当前协程，等待另一个异步操作完成后再继续：

```python
data = await fetch_data()
print(data)
```

等价于 JavaScript：

```javascript
const data = await fetchData()
console.log(data)
```

### async with

异步上下文管理器，自动管理资源的**进入**和**释放**，类似 `try/finally`：

```python
async with database.connect() as conn:
    await conn.query(...)
```

等价于：

```python
conn = await database.connect().__aenter__()
try:
    await conn.query(...)
finally:
    await database.connect().__aexit__()
```

等价于 JavaScript：

```javascript
const conn = await database.connect()
try {
  await conn.query(...)
} finally {
  await conn.close()
}
```

### as (read, write)

Python 的**元组解构（Tuple Unpacking）**，把 `async with` 返回的元组自动拆开：

```python
async with stdio_client(server_params) as (read, write):
    ...
```

等价于：

```python
async with stdio_client(server_params) as streams:
    read, write = streams
```

等价于 JavaScript：

```javascript
const [read, write] = await stdioClient(...)
```

### 完整拆解示例

```python
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = await session.list_tools()
```

展开后：

```python
async def main():
    client = stdio_client(server_params)
    read, write = await client.__aenter__()
    try:
        sess = ClientSession(read, write)
        session = await sess.__aenter__()
        try:
            await session.initialize()
            mcp_tools = await session.list_tools()
        finally:
            await sess.__aexit__(None, None, None)
    finally:
        await client.__aexit__(None, None, None)
```

### 语法对照表

| Python | JavaScript | 作用 |
|--------|-----------|------|
| `async def` | `async function` | 定义异步函数 |
| `await` | `await` | 等待异步操作完成 |
| `async with` | `try/finally + 自动释放` | 异步资源管理 |
| `as (a, b)` | `const [a, b] = ...` | 元组解构赋值 |
