import time

from concurrent.futures import ThreadPoolExecutor

def process_items(items):
    """Process a list of items concurrently"""
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda x: x * 2, items))
    return results

# Example usage
if __name__ == "__main__":
    items = list(range(10))
    start_time = time.time()
    results = process_items(items)
    end_time = time.time()
    print(f"Processed {len(results)} items in {end_time - start_time:.2f} seconds") 
