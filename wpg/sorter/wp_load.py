import sys
from word_sorter import WordSorter

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: wp_load.py [db_save_path]")
        exit(1)

    save_path = sys.argv[1]

    word_sorter = WordSorter(save_path)
    word_sorter.load_db()
    word_sorter.run()