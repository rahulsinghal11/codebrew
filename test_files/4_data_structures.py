class SimpleCache:
    def __init__(self):
        self.cache = []
        self.max_size = 100
        
    def add(self, key, value):
        # Check if key exists
        for item in self.cache:
            if item[0] == key:
                self.cache.remove(item)
                break
                
        # Add new item
        self.cache.append((key, value))
        
        # Remove oldest if cache is full
        if len(self.cache) > self.max_size:
            self.cache.pop(0)
            
    def get(self, key):
        for k, v in self.cache:
            if k == key:
                return v
        return None

# Example usage
if __name__ == "__main__":
    cache = SimpleCache()
    for i in range(10):
        cache.add(f"key{i}", f"value{i}")
    print("Value for key5:", cache.get("key5")) 