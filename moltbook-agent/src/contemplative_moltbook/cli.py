"""CLI entry point for the Contemplative Moltbook Agent."""

import argparse
import logging
import sys

from .agent import Agent, AutonomyLevel


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="contemplative-moltbook",
        description="Contemplative AI agent for Moltbook",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )

    # Autonomy level flags (mutually exclusive)
    autonomy_group = parser.add_mutually_exclusive_group()
    autonomy_group.add_argument(
        "--approve",
        action="store_const",
        const=AutonomyLevel.APPROVE,
        dest="autonomy",
        help="Approval mode: confirm every post (default)",
    )
    autonomy_group.add_argument(
        "--guarded",
        action="store_const",
        const=AutonomyLevel.GUARDED,
        dest="autonomy",
        help="Guarded mode: auto-post if content passes filters",
    )
    autonomy_group.add_argument(
        "--auto",
        action="store_const",
        const=AutonomyLevel.AUTO,
        dest="autonomy",
        help="Auto mode: fully autonomous (use after trust established)",
    )
    parser.set_defaults(autonomy=AutonomyLevel.APPROVE)

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # register
    subparsers.add_parser("register", help="Register a new agent on Moltbook")

    # status
    subparsers.add_parser("status", help="Check agent status")

    # introduce
    subparsers.add_parser("introduce", help="Post introduction template")

    # run
    run_parser = subparsers.add_parser("run", help="Run autonomous session")
    run_parser.add_argument(
        "--session",
        type=int,
        default=60,
        help="Session duration in minutes (default: 60)",
    )

    # solve
    solve_parser = subparsers.add_parser(
        "solve", help="Test verification solver"
    )
    solve_parser.add_argument("text", help="Obfuscated challenge text")

    args = parser.parse_args()
    _setup_logging(args.verbose)

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    agent = Agent(autonomy=args.autonomy)

    if args.command == "register":
        result = agent.do_register()
        print(f"Registration result: {result}")

    elif args.command == "status":
        result = agent.do_status()
        print(f"Agent status: {result}")

    elif args.command == "introduce":
        agent.do_introduce()

    elif args.command == "run":
        agent.run_session(duration_minutes=args.session)

    elif args.command == "solve":
        agent.do_solve(args.text)


if __name__ == "__main__":
    main()
