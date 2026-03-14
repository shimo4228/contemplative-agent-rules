"""CLI for the IPD benchmark."""

import argparse
import logging
from pathlib import Path

from .benchmark import (
    format_paper_report,
    format_report,
    run_benchmark,
    run_paper_benchmark,
    save_paper_results,
    save_results,
)
from .llm_player import PromptVariant


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ipd-benchmark",
        description="Iterated Prisoner's Dilemma benchmark for Contemplative AI",
    )
    parser.add_argument(
        "-r", "--rounds", type=int, default=None,
        help="Number of rounds per match (default: 20 for original, 10 for paper)",
    )
    parser.add_argument(
        "-n", "--simulations", type=int, default=50,
        help="Number of simulations per condition (paper protocol only, default: 50)",
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
    parser.add_argument(
        "--protocol", type=str, default="original",
        choices=["original", "paper"],
        help="Benchmark protocol: original (default) or paper (Appendix E)",
    )
    parser.add_argument(
        "--prompt-file", type=str, default=None,
        help="Path to custom contemplative prompt file (used as 'custom' variant)",
    )

    args = parser.parse_args()

    if args.rounds is not None and not 1 <= args.rounds <= 1000:
        parser.error("--rounds must be between 1 and 1000")
    if not 1 <= args.simulations <= 500:
        parser.error("--simulations must be between 1 and 500")

    # Load custom prompt if provided
    custom_prompt_text = None
    if args.prompt_file:
        prompt_path = Path(args.prompt_file)
        if not prompt_path.exists():
            parser.error(f"Prompt file not found: {args.prompt_file}")
        custom_prompt_text = prompt_path.read_text(encoding="utf-8")
        # Auto-select custom variant if not explicitly specified
        if args.variants is None:
            args.variants = ["baseline", "custom"]

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    variants = None
    if args.variants:
        variants = [PromptVariant(v) for v in args.variants]

    if args.protocol == "paper":
        from .benchmark import compute_paper_statistics

        num_rounds = args.rounds if args.rounds is not None else 10
        result = run_paper_benchmark(
            num_simulations=args.simulations,
            num_rounds=num_rounds,
            backend=args.backend,
            variants=variants,
            custom_prompt_text=custom_prompt_text,
        )
        stats = compute_paper_statistics(result)
        report = format_paper_report(result, stats)
        print(report)

        if args.output:
            save_paper_results(result, stats, args.output)
            print(f"\nResults saved to {args.output}")
    else:
        num_rounds = args.rounds if args.rounds is not None else 20
        results = run_benchmark(
            num_rounds=num_rounds,
            backend=args.backend,
            variants=variants,
            custom_prompt_text=custom_prompt_text,
        )
        report = format_report(results)
        print(report)

        if args.output:
            save_results(results, args.output)
            print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
