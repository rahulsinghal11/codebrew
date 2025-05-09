def count_word_frequency(text):
    """Count frequency of each word in text"""
    words = text.split()
    frequency = {}
    for word in words:
        frequency[word] = frequency.get(word, 0) + 1
            
    return frequency

# Example usage
if __name__ == "__main__":
    sample_text = "the quick brown fox jumps over the lazy dog the fox is quick"
    result = count_word_frequency(sample_text)
    print("Word frequencies:", result) 
