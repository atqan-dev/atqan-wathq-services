# change file name that have _converted suffix to original file name
# and replace original file if same name exists
from pathlib import Path
from typing import Iterable


def _split_name_and_suffix(path: Path) -> tuple[str, str]:
    suffix = ''.join(path.suffixes)
    if suffix:
        name_without_suffix = path.name[: -len(suffix)]
    else:
        name_without_suffix = path.name
    return name_without_suffix, suffix


def revert_converted_file(file_path: str, *, debug: bool = True, dry_run: bool = False) -> bool:
    # file example: example_converted.avif => example.avif
    def log(message: str) -> None:
        if debug:
            print(message)

    path = Path(file_path)
    log(f"[START] {path}")

    if not path.exists():
        log(f"[SKIP] File not found: {path}")
        return False

    if not path.is_file():
        log(f"[SKIP] Not a file: {path}")
        return False

    name_without_suffix, suffix = _split_name_and_suffix(path)
    if not name_without_suffix.endswith('_converted'):
        log(f"[SKIP] Missing '_converted' suffix before extension: {path.name}")
        return False

    original_name = f"{name_without_suffix[:-len('_converted')]}{suffix}"
    original_file_path = path.with_name(original_name)
    log(f"[INFO] Target original: {original_file_path}")

    if original_file_path.exists():
        if original_file_path.is_dir():
            log(f"[ERROR] Target exists and is a directory: {original_file_path}")
            return False
        log(f"[INFO] Removing existing original: {original_file_path}")
        if not dry_run:
            original_file_path.unlink()

    log(f"[INFO] Renaming: {path.name} -> {original_file_path.name}")
    if not dry_run:
        path.replace(original_file_path)

    log(f"[DONE] {original_file_path}")
    return True
    
    
# Example usage:
# revert_converted_file('example_converted.txt')
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Revert *_converted files to original names, overwriting originals if present."
    )
    parser.add_argument("files", nargs="*", help="Paths to *_converted files")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without changing files")
    parser.add_argument("--quiet", action="store_true", help="Suppress debug output")
    args = parser.parse_args()

    if not args.files:
        parser.print_usage()
        raise SystemExit(1)

    success = 0
    failure = 0
    for file in args.files:
        if revert_converted_file(file, debug=not args.quiet, dry_run=args.dry_run):
            success += 1
        else:
            failure += 1

    if not args.quiet:
        print(f"[SUMMARY] Success: {success}, Failed: {failure}")
# Example usage:
# revert_converted_file('example_converted.txt')
# Example usage:
# revert_converted_file('example_converted.txt')