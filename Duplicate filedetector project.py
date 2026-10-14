import hashlib
import os


def calculate_file_hash(file_path, block_size=65536):
    hasher = hashlib.md5()

    try:
        with open(file_path, "rb") as open_file:
            buf = open_file.read(block_size)

            while len(buf) > 0:
                hasher.update(buf)
                buf = open_file.read(block_size)

        return hasher.hexdigest()

    except (OSError, PermissionError, FileNotFoundError):
        return None


def find_duplicate_files(target_folder):
    hash_map = {}
    duplicates = []

    for root, dirs, files in os.walk(target_folder):
        for filename in files:
            full_path = os.path.join(root, filename)
            file_hash = calculate_file_hash(full_path)

            if file_hash is None:
                continue

            if file_hash in hash_map:
                duplicates.append((full_path, hash_map[file_hash]))
            else:
                hash_map[file_hash] = full_path

    return duplicates


if __name__ == "__main__":
    folder_to_scan = "./my_test_folder"

    print(f"Scanning {folder_to_scan} for duplicate files...")

    results = find_duplicate_files(folder_to_scan)

    if results:
        print(f"\nFound {len(results)} duplicate(s):")

        for duplicate_path, original_path in results:
            print(f"\nDuplicate: {duplicate_path}")
            print(f"  Matches: {original_path}")

    else:
        print("\nNo duplicate files found.")
