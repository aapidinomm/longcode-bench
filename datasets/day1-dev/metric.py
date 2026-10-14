# /// script
# dependencies = []
# ///

import argparse
import json
from pathlib import Path


def main(input_path: Path, output_path: Path) -> None:
    rewards = []
    for line in input_path.read_text().splitlines():
        record = json.loads(line)
        rewards.append(0.0 if record is None else float(record.get("reward", 0.0)))

    mean = sum(rewards) / len(rewards) if rewards else 0.0
    output_path.write_text(json.dumps({"mean_reward": mean}) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-path", type=Path, required=True)
    parser.add_argument("-o", "--output-path", type=Path, required=True)
    args = parser.parse_args()
    main(args.input_path, args.output_path)

