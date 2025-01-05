import os
import subprocess
import sys
import time


def get_html_file_name(tenhou_url: str) -> str:
    i = tenhou_url.find("?log=") + 5
    return tenhou_url[i:].replace("&tw=", "_tw") + ".html"


def extract_rating(html_file: str) -> float:
    with open(html_file, "r") as f:
        html_content = f.read()
    pattern = "<dt>rating<dd>"
    i = html_content.find(pattern) + len(pattern)
    j = html_content.find("<", i)
    return float(html_content[i:j])


# usage:
# python3 project/bulk_mortal_review.py [log_files_directory]
# directory structure:
# log_files_directory
# ---file1.txt
# ------https://url1
# ------https://url2
# ---file2.txt
# ------https://url3
# ------https://url4
def main():
    log_files_directory = os.path.expanduser(sys.argv[1])
    print(f"Log files directory: {log_files_directory}")

    review_results_directory = os.path.join(log_files_directory, "review_results")
    print(f"Review results directory: {review_results_directory}")
    if not os.path.exists(review_results_directory):
        os.mkdir(review_results_directory)

    mjai_reviewer_directory = os.path.realpath("../mjai-reviewer")
    print(f"Mjai reviewer directory: {mjai_reviewer_directory}")
    if not os.path.exists(mjai_reviewer_directory):
        raise Exception("Mjai reviewer directory doesn't exist")
    mjai_reviewer_release_dir = os.path.join(mjai_reviewer_directory, "target", "release")
    mjai_reviewer_exec = os.path.join(mjai_reviewer_release_dir, "mjai-reviewer")
    print(f"Mjai reviewer exec: {mjai_reviewer_exec}")
    if not os.path.exists(mjai_reviewer_exec):
        raise Exception("Mjai reviewer exec doesn't exist")

    log_files = sorted(f for f in os.listdir(log_files_directory) if f.endswith(".txt"))
    print(f"Found {len(log_files)} log files")
    for log_file in log_files:
        log_file_path = os.path.join(log_files_directory, log_file)
        urls = []
        with open(log_file_path, "r") as f:
            for line in f:
                line = line.strip()
                if len(line) > 0 and "&tw=" in line:
                    urls.append(line)
        print(f"Found {len(urls)} urls in file {log_file}")
        review_subdir = os.path.join(review_results_directory, log_file.replace(".txt", ""))
        if not os.path.exists(review_subdir):
            os.mkdir(review_subdir)
        for i, url in enumerate(urls):
            output_file = os.path.join(review_subdir, get_html_file_name(tenhou_url=url))
            print(f"Analyzing url {url} ({i + 1} / {len(urls)})...", flush=True)
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                print(f"Url {i + 1} / {len(urls)} already exists")
            else:
                t1 = time.time()
                try:
                    code = subprocess.call(
                        args=[
                            mjai_reviewer_exec,
                            "-e", "mortal",
                            "--show-rating",
                            "-u", url.replace("/3/", "/0/"),
                            "--no-open",
                            "-o", output_file
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        cwd=mjai_reviewer_release_dir,
                    )
                except Exception as e:
                    print(f"Couldn't parse url {i + 1} / {len(urls)}. Exception: {e}")
                    continue
                if code != 0:
                    print(f"Couldn't parse url {i + 1} / {len(urls)}. Code: {code}")
                    continue
                t2 = time.time()
                print(f"Review of url {i + 1} / {len(urls)} completed in {t2 - t1:.3f} sec")
            rating = extract_rating(html_file=output_file)
            print(f"Url {i + 1} / {len(urls)} rating = {rating}, output file {output_file}", flush=True)


if __name__ == "__main__":
    main()
