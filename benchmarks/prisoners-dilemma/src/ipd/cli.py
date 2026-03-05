"""CLI for the IPD benchmark."""

import argparse
import logging
import sys

from .benchmark import format_report, run_benchmark, save_results


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ipd-benchmark",
        description="Iterated Prisoner's Dilemma benchmark for Contemplative AI",
    )
    parser.add_argument(
        "-r", "--rounds", type=int, default=20,
        help="Number of rounds per match (default: 20)",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="Save results to JSON file",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    results = run_benchmark(num_rounds=args.rounds)
    report = format_report(results)
    print(report)

    if args.output:
        save_results(results, args.output)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
