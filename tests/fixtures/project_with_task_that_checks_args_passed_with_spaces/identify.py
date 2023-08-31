import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-name")
    parser.add_argument("--age")
    args = parser.parse_args()
    print(f"name: {args.full_name} age: {args.age}")
