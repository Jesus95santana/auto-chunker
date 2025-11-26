import argparse
import subprocess
import os
import sys
import shutil

# -------------------------------------------------
# ABSOLUTE PATH TO YOUR AUTO-CHUNKER DIRECTORY
# -------------------------------------------------
SCRIPT_DIR = "/home/santana/Python/auto-chunker"

# -------------------------------------------------
# Always store chunks & summaries inside auto-chunker
# -------------------------------------------------
CHUNKS_DIR = os.path.join(SCRIPT_DIR, "chunks")
SUMMARIES_DIR = os.path.join(SCRIPT_DIR, "summaries")


# ----------------------------
# Utility: run a shell command
# ----------------------------
def run_command(cmd_list, description):
    print(f"\n=== {description} ===")
    print(" ".join(cmd_list))
    try:
        subprocess.run(cmd_list, check=True)
    except subprocess.CalledProcessError:
        print(f"\nERROR during: {description}")
        sys.exit(1)


# ----------------------------
# MAIN PIPELINE
# ----------------------------
def main():
    parser = argparse.ArgumentParser(description="Full pipeline: chunk → summarize → merge")

    parser.add_argument("input_file", help="The large .md or .txt file to process")
    parser.add_argument("--chunk_words", type=int, default=1800)
    parser.add_argument("--chunk_chars", type=int)
    parser.add_argument("--summary_model", default="gpt-4.1-mini")
    parser.add_argument("--merge_model", default="gpt-5.1")
    parser.add_argument("--final_output", default=None, help="Final SOP output file (defaults to <input>_SOP.md)")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    # ------------------------------------
    # Auto-generate SOP output file name
    # ------------------------------------
    if args.final_output is None:
        base = os.path.splitext(os.path.basename(args.input_file))[0]
        args.final_output = f"{base}_SOP.md"

    # Use the python interpreter that launched this script
    python_exec = sys.executable

    # ------------------------------------
    # Clean old chunks & summaries
    # ------------------------------------
    if os.path.exists(CHUNKS_DIR):
        shutil.rmtree(CHUNKS_DIR)

    if os.path.exists(SUMMARIES_DIR):
        shutil.rmtree(SUMMARIES_DIR)

    # ------------------------------------
    # Step 1 — Chunking
    # ------------------------------------
    chunker_path = os.path.join(SCRIPT_DIR, "chunker.py")

    chunker_cmd = [python_exec, chunker_path, args.input_file, "--out", CHUNKS_DIR]

    if args.chunk_chars:
        chunker_cmd.extend(["--chars", str(args.chunk_chars)])
    else:
        chunker_cmd.extend(["--words", str(args.chunk_words)])

    if args.verbose:
        chunker_cmd.append("--verbose")

    run_command(chunker_cmd, "Chunking")

    # ------------------------------------
    # Step 2 — Summaries
    # ------------------------------------
    summarizer_path = os.path.join(SCRIPT_DIR, "summarizer.py")

    summarizer_cmd = [python_exec, summarizer_path, "--chunks", CHUNKS_DIR, "--out", SUMMARIES_DIR, "--model", args.summary_model]

    if args.verbose:
        summarizer_cmd.append("--verbose")

    run_command(summarizer_cmd, "Summarizing chunks")

    # ------------------------------------
    # Step 3 — Merge
    # ------------------------------------
    merger_path = os.path.join(SCRIPT_DIR, "merger.py")

    merger_cmd = [python_exec, merger_path, "--summaries", SUMMARIES_DIR, "--model", args.merge_model, "--out", args.final_output]

    if args.verbose:
        merger_cmd.append("--verbose")

    run_command(merger_cmd, "Merging summaries into final SOP")

    print("\n🎉 Pipeline complete!")
    print(f"Final SOP saved to: {args.final_output}")


if __name__ == "__main__":
    main()
