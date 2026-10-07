"""`tmk-explorer` — generate the examiner explorer's data under `site/data/`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tm_knowledge.explorer import build as build_module


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tmk-explorer",
        description="Generate the data behind the examiner explorer (needs the pinned snapshot).",
    )
    parser.add_argument("--write", action="store_true", help="write into site/data/")
    parser.add_argument("--out", type=Path, help="write somewhere other than site/data/")
    args = parser.parse_args(argv)

    key, endpoint = build_module.from_environment()
    files = build_module.build(key=key, endpoint=endpoint)
    onto = files["ontology.json"]
    counts = onto["counts"]
    print(f"{counts['concepts']['signed']} signed + {counts['concepts']['machine']} machine-written concepts; "
          f"{counts['relations']['signed']} signed + {counts['relations']['machine']} machine-written relationships")
    print(f"{len(files['passages.json']['chunks'])} Manual passages, "
          f"{len(files['passages.json']['legislation'])} provisions and units; "
          f"{len(files['examples.json']['answers'])} prepared answers")
    live = files["live.json"]
    print("live chat: " + ("on, " + ("key published in the page" if "m" in live else "through a proxy")
                           if live["enabled"] else f"off (set {build_module.KEY_ENV} to turn it on)"))
    if args.write:
        for path in build_module.write(files, args.out):
            print(f"wrote {path.relative_to(build_module.REPO_ROOT) if path.is_relative_to(build_module.REPO_ROOT) else path}"
                  f" ({path.stat().st_size // 1024} KB)")
    else:
        print("\n(dry run — nothing written. Pass --write.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
