import sys
from word_sorter import WordSorter

if __name__ == "__main__":
    arg_length = len(sys.argv)
    if arg_length != 3 and arg_length != 4:
        print("Usage: wp_new.py [file_path] [db_save_path] [max_word_length]")
        exit(1)

    file_path = sys.argv[1]
    save_path = sys.argv[2]
    max_count = 100

    if arg_length == 4:
        max_count = int(sys.argv[3])

    word_sorter = WordSorter(save_path)
    word_sorter.load_text(file_path, max_count)
    word_sorter.run()
