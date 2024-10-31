s = "Hello World"
prefixes = ["Hello", "Hi", "Hey"]
index = next((i for i, prefix in enumerate(prefixes) if s.startswith(prefix)), None)
if index is not None:
    print("字符串以第 {} 个前缀 '{}' 开头".format(index, prefixes[index]))