import argparse

from scrapers import SCRAPERS, FIELDNAMES, OUTPUT_DIR

import csv
from pathlib import Path


def save_csv(properties: list[dict], filename: str) -> Path:
    path = OUTPUT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(properties)
    return path


def main():
    parser = argparse.ArgumentParser(description="Scraper de Imoveis - Sao Carlos")
    parser.add_argument(
        "--exclude", "-e",
        nargs="+",
        choices=list(SCRAPERS.keys()),
        default=[],
        help="Scrapers to exclude (ex: --exclude roca)",
    )
    parser.add_argument(
        "--only", "-o",
        nargs="+",
        choices=list(SCRAPERS.keys()),
        default=[],
        help="Run only these scrapers (ex: --only cardinali)",
    )
    args = parser.parse_args()

    if args.only:
        to_run = {k for k in args.only}
    else:
        to_run = set(SCRAPERS.keys()) - set(args.exclude)

    print("=" * 60)
    print("Scraper de Imoveis - Sao Carlos")
    print(f"  Rodando: {', '.join(sorted(to_run))}")
    print("=" * 60)

    all_properties = []
    step = 0
    total_steps = len(to_run)

    for key, scraper in SCRAPERS.items():
        if key not in to_run:
            continue
        step += 1

        print(f"\n[{step}/{total_steps}] Scraping {scraper.name}...")
        props = scraper.scrape()
        all_properties.extend(props)
        print(f"  Total {scraper.name}: {len(props)} imoveis")

        if props:
            path = scraper.save_csv(props)
            print(f"  Salvo: {path}")

    if all_properties and total_steps > 1:
        path = save_csv(all_properties, "todos_imoveis.csv")
        print(f"\n  Salvo: {path}")

    print(f"\nTotal geral: {len(all_properties)} imoveis")


if __name__ == "__main__":
    main()
