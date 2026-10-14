import hashlib
import os


def calculate_file_hash(file_path, block_size=65536):
    # WHAT: Defines a function to calculate a unique "fingerprint" for a specific file.
    # HOW: It takes a file path and sets a block_size of 64KB (65,536 bytes) as a default.
    # WHY: If we try to read a massive 10GB video file into memory all at once, the computer will crash. Reading it in small chunks makes this script incredibly memory-efficient.

    hasher = hashlib.md5()
    # WHAT: Initializes an MD5 hashing workspace object.
    # HOW: It sets up an empty calculation state ready to process raw data.
    # WHY: MD5 is extremely fast. While not secure enough for passwords, it is perfect and efficient for identifying matching file contents.

    try:
        # WHAT: Starts a defensive error-handling block.
        # HOW: It tells Python: "Try to run the following code, but if a problem happens, don't crash."
        # WHY: In the real world, some files are locked by the system or restricted. We need to handle those gracefully.

        with open(file_path, "rb") as open_file:
            # WHAT: Opens the file safely in Read Binary mode.
            # HOW: The 'with' statement guarantees that the file will automatically close when we are done, preventing memory leaks.
            # WHY: 'rb' reads raw bytes instead of text. This allows the script to work on everything—images, music, PDFs, and spreadsheets alike.

            buf = open_file.read(block_size)
            # WHAT: Reads the first 64KB chunk of the file and stores it in a temporary buffer (buf).
            # HOW: It takes a small bite out of the file instead of swallowing it whole.
            # WHY: This initializes our reading loop to begin streaming the file's contents.

            while len(buf) > 0:
                # WHAT: Creates a loop that keeps running as long as there is data left to read.
                # HOW: 'len(buf) > 0' means "if we actually read some bytes, keep going."
                # WHY: It forces Python to process the file piece by piece until it hits the very end.

                hasher.update(buf)
                # WHAT: Feeds the current 64KB chunk of data into our MD5 calculation workspace.
                # HOW: It continuously updates the mathematical formula with the new bytes.
                # WHY: This allows us to calculate one final fingerprint over a series of small, safe steps.

                buf = open_file.read(block_size)
                # WHAT: Reads the next 64KB chunk of the file.
                # HOW: It advances our position in the file. If it reaches the end, buf becomes empty (len == 0), breaking the loop.
                # WHY: Essential to move forward; otherwise, we'd loop infinitely on the first chunk.

        return hasher.hexdigest()
        # WHAT: Extracts the final hex string fingerprint (e.g., "9e107d9d372bb6826bd81d3542a419d6").
        # HOW: It formats the mathematical hash into a readable string of numbers and letters.
        # WHY: This is the precise, unique identifier we will use to compare files.

    except (OSError, PermissionError, FileNotFoundError):
        # WHAT: Catches common file system errors.
        # HOW: If a file is corrupted, missing, or requires admin privileges, it catches it here.
        # WHY: This ensures our script keeps running smoothly even if it hits a broken or restricted system file.

        return None
        # WHAT: Returns a blank placeholder when a file cannot be read.
        # HOW: Simply outputs 'None' back to the calling function.
        # WHY: Explicitly signals to the calling function that this file should be skipped.


def find_duplicate_files(target_folder):
    # WHAT: Defines the main function that crawls through a folder to look for duplicates.
    # HOW: It accepts a starting folder path as its input parameter.
    # WHY: It encapsulates the search logic so it can be reused across different folders.

    hash_map = {}
    # WHAT: Creates an empty dictionary to store file fingerprints.
    # HOW: Key-value pairs will look like: { "FILE_HASH": "FIRST_FILE_PATH" }.
    # WHY: Dictionaries use hash tables under the hood. Looking up a key in a dictionary is instantaneous (O(1) time complexity), making this script incredibly fast even for thousands of files.

    duplicates = []
    # WHAT: Creates an empty list to store the pairs of duplicates we find.
    # HOW: It will hold pairs like (duplicate_path, original_path).
    # WHY: To keep an organized record of all matches so we can display them at the end.

    for root, dirs, files in os.walk(target_folder):
        # WHAT: Recursively loops through every folder, subfolder, and file inside the target location.
        # HOW: 'os.walk' acts like a tree explorer, constantly diving deeper into subfolders.
        # WHY: Users rarely keep duplicates in the exact same folder; they are usually hidden deep in sub-directories.

        for filename in files:
            # WHAT: Loops through every individual file found in the current directory layer.
            # HOW: It handles files one by one.
            # WHY: We must evaluate every single file individually to ensure nothing is missed.

            full_path = os.path.join(root, filename)
            # WHAT: Glues the folder path (root) and the file name (filename) together.
            # HOW: 'os.path.join' automatically handles system slashes ('/' for Mac/Linux, '\' for Windows).
            # WHY: To read a file, Python needs its complete, absolute address on the hard drive.

            file_hash = calculate_file_hash(full_path)
            # WHAT: Calls our helper function to generate the unique fingerprint for this specific file.
            # HOW: It passes the full path we just built into 'calculate_file_hash'.
            # WHY: We need this fingerprint to see if we've encountered this exact content before.

            if file_hash is None:
                # WHAT: Checks if the hashing function returned an error (None).
                # HOW: It evaluates if the variable equals our error placeholder.
                # WHY: Identifies unreadable files so we can bypass them without breaking the loop.

                continue
                # WHAT: Skips the rest of the loop and moves directly to the next file.
                # HOW: The 'continue' keyword stops execution here and jumps straight to the next file in line.
                # WHY: Prevents the script from crashing over unreadable or system-locked files.

            if file_hash in hash_map:
                # WHAT: THE "AHA!" MOMENT: Checks if this exact fingerprint already exists in our dictionary.
                # HOW: It looks up the 'file_hash' key in 'hash_map'.
                # WHY: If the hash is already in the dictionary, it means we have already processed another file with the exact same content. This file is a duplicate.

                duplicates.append((full_path, hash_map[file_hash]))
                # WHAT: Logs the duplicate.
                # HOW: It appends a tuple containing the current duplicate's path and the original file's path (stored in hash_map[file_hash]).
                # WHY: It tracks exactly where the duplicate is and what it is a copy of.

            else:
                # WHAT: Handles the scenario where the file fingerprint is completely new.
                # HOW: Executes only if the hash key was not found in the dictionary.
                # WHY: Tells the script what to do with a unique file it has never seen before.

                hash_map[file_hash] = full_path
                # WHAT: If the hash is unique, save it to the dictionary.
                # HOW: Sets the 'file_hash' as the key and the 'full_path' as the value.
                # WHY: This marks the file as the "original copy" so that future duplicates can be checked against it.

    return duplicates
    # WHAT: Hands back the final list of duplicates when the folder scan finishes.
    # HOW: Exits the function and passes the 'duplicates' list back to the code that called it.
    # WHY: To let the user or UI see the results of the scan.


if __name__ == "__main__":
    # WHAT: A standard Python guardrail clause.
    # HOW: It ensures the code below only runs if this script is executed directly (not when imported into another script).
    # WHY: Best practice in Python engineering to keep code modular and clean.

    folder_to_scan = "./my_test_folder"
    # WHAT: Defines the target directory path that you want to check for duplicates.
    # HOW: Sets a string variable pointing to a local folder named 'my_test_folder'.
    # WHY: Provides an easily adjustable configuration point before kicking off the program.

    print(f"Scanning {folder_to_scan} for duplicate files...")
    # WHAT: Prints a status update message to the console screen.
    # HOW: Uses an f-string to inject our folder path variable directly into the text.
    # WHY: Provides immediate visual feedback to the user that the program has successfully started.

    results = find_duplicate_files(folder_to_scan)
    # WHAT: Runs the main search engine function and saves its output.
    # HOW: Calls 'find_duplicate_files', passes the path, and captures the returned list inside 'results'.
    # WHY: This triggers the entire workflow we just built across the file system.

    if results:
        # WHAT: Evaluates whether any duplicate files were actually discovered.
        # HOW: In Python, a list containing items evaluates to True; an empty list evaluates to False.
        # WHY: Allows the script to split paths and choose between showing a summary or an alternate message.

        print(f"\nFound {len(results)} duplicate(s):")
        # WHAT: Displays the total headcount of duplicate files found on the screen.
        # HOW: Uses the 'len()' function to count the total number of items stored in the results list.
        # WHY: Provides a quick summary of the scan results before listing the file paths.

        for duplicate_path, original_path in results:
            # WHAT: Loops through every duplicate pair found by the search function.
            # HOW: Unpacks each pair into the duplicate file path and the matching original path.
            # WHY: Makes it possible to show the user exactly which files have matching content.

            print(f"\nDuplicate: {duplicate_path}")
            # WHAT: Displays the path of the duplicate file.
            # HOW: Inserts the duplicate path into the status message.
            # WHY: Shows the user which file is an extra copy.

            print(f"  Matches: {original_path}")
            # WHAT: Displays the path of the matching original file.
            # HOW: Inserts the original path into the status message.
            # WHY: Lets the user compare the duplicate with the file it matches.

    else:
        # WHAT: Handles the case where the scan did not find any duplicate files.
        # HOW: Runs when the results list is empty.
        # WHY: Gives the user a clear result instead of leaving the program silent.

        print("\nNo duplicate files found.")
        # WHAT: Displays a message when no duplicates were discovered.
        # HOW: Prints a clear message to the console.
        # WHY: Confirms that the scan completed and found no matching files.
