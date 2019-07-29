#encoding=utf8

import pprint
import argparse
import json
import git
Git = git.cmd.Git

def init_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("rev1")
    parser.add_argument("rev2")
    args = parser.parse_args()
    return args

def extract_author(blame_history):
    lines = blame_history.splitlines()
    line1 = lines[0]
    start = line1.find("(")
    stop = line1.find(")")
    ret = []
    for line in lines:
        author = line[start+1:stop].split()[0]
        ret.append(author)
    return ret

def sumup_to_author_filename(all_results):
    manual = []
    result = {}
    result["manual"] = manual
    for filename, changeset in all_results.items():
        if changeset.get("append_new", None):
            manual.append(filename)
            continue
        for author in changeset.values():
            if not result.get(author, None):
                result[author] = {filename:True}
            else:
                result[author][filename] = True
    return result

def main():
    args = init_parser()
    g = Git(".")
    g.init()
    diff_file = g.diff(args.rev1, args.rev2, "--name-only")
    diff_file = diff_file.split()
    all_results = {}
    for filename in diff_file:
        blame_history1 = g.blame(args.rev1, filename)
        author_history1 = extract_author(blame_history1)
        blame_history2 = g.blame(args.rev2, filename)
        author_history2 = extract_author(blame_history2)
        one_file_result = {}
        old_file_length = len(author_history1)
        for i, new_author in enumerate(author_history2, start=0):
            if i >= old_file_length:
                one_file_result["append_new"] = {i, new_author}
                break
            old_author = author_history1[i]
            if new_author != old_author:
                one_file_result[i] = old_author
        all_results[filename] = one_file_result
    author_filenames = sumup_to_author_filename(all_results)
    pprint.pprint(author_filenames)

main()
