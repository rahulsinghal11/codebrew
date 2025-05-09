import time

def process_items(items):
    """Process a list of items sequentially"""
    results = []
    for item in items:
        # Simulate some processing time
        time.sleep(0.1)
        results.append(item * 2)
    return results

# Example usage
if __name__ == "__main__":
    items = list(range(10))
    start_time = time.time()
    results = process_items(items)
    end_time = time.time()
    print(f"Processed {len(results)} items in {end_time - start_time:.2f} seconds") 