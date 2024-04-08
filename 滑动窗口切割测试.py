data = "Hello, World!"
MAX_WINDOW_SIZE = 5

parts = [data[i:5] for i in range(0, len(data), MAX_WINDOW_SIZE)]
for part in parts:
    print(part)