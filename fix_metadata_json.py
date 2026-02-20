import json
import os


def _fix_strings(value):
    if isinstance(value, str):
        return value.replace("Calm1", "Calm")
    if isinstance(value, list):
        return [_fix_strings(item) for item in value]
    if isinstance(value, dict):
        return {k: _fix_strings(v) for k, v in value.items()}
    return value


def fix_metadata_dir(root_dir):
    fixed_count = 0
    for name in os.listdir(root_dir):
        if not name.endswith(".json"):
            continue
        path = os.path.join(root_dir, name)
        if not os.path.isfile(path):
            continue

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        fixed = _fix_strings(data)

        if fixed != data:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(fixed, f, ensure_ascii=False, indent=4)
            fixed_count += 1

    return fixed_count


if __name__ == "__main__":
    target_dir = "/home/muhammed-emin-eser/desk/apps/yt-bulk/metadata_output"
    count = fix_metadata_dir(target_dir)
    print(f"Fixed files: {count}")
