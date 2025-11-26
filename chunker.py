import os
import argparse
import textwrap


# ----------------------------
# Utility: load file
# ----------------------------
def read_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ----------------------------
# Utility: save a single chunk
# ----------------------------
def save_chunk(chunk_text, output_dir, index):
    os.makedirs(output_dir, exist_ok=True)
    chunk_name = f"chunk_{index:02d}.md"
    chunk_path = os.path.join(output_dir, chunk_name)

    with open(chunk_path, "w", encoding="utf-8") as f:
        f.write(chunk_text)

    return chunk_path


# ----------------------------
# CHUNKING METHOD 1:
#   Simple character-based chunking
# ----------------------------
def chunk_by_chars(text, char_limit):
    return [text[i : i + char_limit] for i in range(0, len(text), char_limit)]


# ----------------------------
# CHUNKING METHOD 2:
#   Word-aware chunking to avoid mid-sentence cuts (recommended)
# ----------------------------
def chunk_by_words(text, max_words):
    words = text.split()
    chunks = []
    current = []

    for word in words:
        current.append(word)
        if len(current) >= max_words:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return chunks


# ----------------------------
# MAIN: handles CLI + processing
# ----------------------------
def main():
    parser = argparse.ArgumentParser(description="Chunk a large text/markdown file.")
    parser.add_argument("input_file", help="Path to the .md or .txt file")
    parser.add_argument("--out", default="chunks", help="Output directory")
    parser.add_argument("--chars", type=int, default=None, help="Max characters per chunk")
    parser.add_argument("--words", type=int, default=None, help="Max words per chunk (better)")
    parser.add_argument("--verbose", action="store_true", help="Show progress")

    args = parser.parse_args()

    # Load input
    text = read_file(args.input_file)

    # Choose chunking strategy
    if args.words:
        chunks = chunk_by_words(text, args.words)
        method = f"{args.words} words per chunk"
    elif args.chars:
        chunks = chunk_by_chars(text, args.chars)
        method = f"{args.chars} chars per chunk"
    else:
        raise ValueError("You must provide either --chars or --words.")

    # Save chunks
    for idx, chunk in enumerate(chunks, start=1):
        path = save_chunk(chunk, args.out, idx)
        if args.verbose:
            print(f"Saved {path}")

    print(f"\nDone! Created {len(chunks)} chunks using {method} in '{args.out}'")


if __name__ == "__main__":
    main()
