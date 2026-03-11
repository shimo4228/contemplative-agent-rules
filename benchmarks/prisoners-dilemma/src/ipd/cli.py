"""CLI for the IPD benchmark."""

import argparse
import logging

from .benchmark import format_report, run_benchmark, save_results
from .llm_player import PromptVariant


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
    parser.add_argument(
        "--backend", type=str, default="ollama",
        choices=["ollama", "openai"],
        help="LLM backend: ollama (default) or openai",
    )
    parser.add_argument(
        "--variants", type=str, nargs="+",
        default=None,
        choices=["baseline", "custom", "paper_faithful"],
        help="Prompt variants to benchmark (default: baseline custom)",
    )

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    variants = None
    if args.variants:
        variants = [PromptVariant(v) for v in args.variants]

    results = run_benchmark(
        num_rounds=args.rounds,
        backend=args.backend,
        variants=variants,
    )
    report = format_report(results)
    print(report)

    if args.output:
        save_results(results, args.output)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
