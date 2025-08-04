"""Entrypoint"""

from aicb.data_prep.awel_reader import AwelReader


def main():
    """
    main
    """
    reader = AwelReader("data/2023_originalfile_nonicknames.csv")

    conversations = reader.load_conversations()

    if conversations:
        print(f"Loaded {len(conversations)} conversations.")
    else:
        print("fuck you")


if __name__ == "__main__":
    main()
