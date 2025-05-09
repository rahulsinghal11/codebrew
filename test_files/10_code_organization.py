# Global variables
config = {}
data = []
results = []

def init():
    global config, data, results
    config = {'max_items': 100, 'timeout': 30}
    data = []
    results = []

def load_data(filename):
    global data
    try:
        with open(filename, 'r') as f:
            data = f.readlines()
    except Exception as e:
        print(f"Error loading data: {str(e)}")

def process_data():
    global data, results
    for item in data:
        if len(item.strip()) > 0:
            processed = item.strip().upper()
            results.append(processed)

def save_results(filename):
    global results
    try:
        with open(filename, 'w') as f:
            for result in results:
                f.write(result + '\n')
    except Exception as e:
        print(f"Error saving results: {str(e)}")

def main():
    init()
    load_data('input.txt')
    process_data()
    save_results('output.txt')

if __name__ == "__main__":
    main() 