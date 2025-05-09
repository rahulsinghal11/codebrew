def find_primes(n):
    """Find all prime numbers up to n"""
    primes = []
    for num in range(2, n + 1):
        is_prime = True
        for i in range(2, num):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

# Example usage
if __name__ == "__main__":
    result = find_primes(50)
    print(f"Prime numbers up to 50: {result}") 