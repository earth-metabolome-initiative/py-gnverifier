from argparse import ArgumentParser, Namespace
from typing import Any, Optional

import compress_json  # type: ignore[import-untyped]
import pandas as pd

from pygnverifier.data_sources import DataSourceClient
from pygnverifier.exceptions import UnsupportedOutputFormatError
from pygnverifier.verification import VerificationRequestConfiguration, Verifier

COMPRESSIONS: list[str] = ["gz", "xz", ""]
SEPARATORS: dict[str, str] = {
    "csv": ",",
    "tsv": "\t",
    "ssv": " ",
}


def verify(args: Namespace) -> None:
    """
    Verify scientific names using the Verifier API.
    """
    # Create a verification request
    configuration: VerificationRequestConfiguration = VerificationRequestConfiguration(
        email=args.email
    ).set_main_taxon_threshold(args.main_taxon_threshold)

    if args.with_all_matches:
        configuration = configuration.with_all_matches()

    if args.with_capitalization:
        configuration = configuration.with_capitalization()

    if args.with_species_group:
        configuration = configuration.with_species_group()

    if args.with_uninomial_fuzzy_match:
        configuration = configuration.with_uninomial_fuzzy_match()

    if args.with_stats:
        configuration = configuration.with_stats()

    # We iterate all of the arguments in the name space that start with
    # 'include_' and add the data sources to the request configuration.
    for arg_name in args.__dict__:
        if arg_name.startswith("include_") and args.__dict__[arg_name]:
            data_source_name = arg_name.replace("include_", "")
            configuration = configuration.include_data_source(data_source_name)

    # Initialize the verifier and send the request
    verifier = Verifier(configuration)
    response = verifier.verify(args.names)

    if any(args.output.endswith(f".json{compression}") for compression in COMPRESSIONS):
        compress_json.dump(response.to_dict(), args.output)
        return None

    raise UnsupportedOutputFormatError(
        output_format=args.output,
        available_output_formats=[f".json.{compression}" for compression in COMPRESSIONS],
    )


def data_sources(args: Namespace) -> None:
    """
    List all available data sources from the Verifier API in different formats.
    """
    client = DataSourceClient(args.email)
    data_sources: list[dict[str, Any]] = [data_source.to_dict() for data_source in client.iter_data_sources()]

    if any(args.output.endswith(f".json{compression}") for compression in COMPRESSIONS):
        compress_json.dump(data_sources, args.output)
        return None

    separator: Optional[str] = None

    for extension in SEPARATORS:
        for compression in COMPRESSIONS:
            if args.output.endswith(f".{extension}{compression}"):
                separator = SEPARATORS[extension]
                break
        if separator is not None:
            break

    if separator is not None:
        pd.DataFrame(data_sources).to_csv(
            args.output,
            sep=separator,
            index=False,
        )
        return None

    raise UnsupportedOutputFormatError(
        output_format=args.output,
        available_output_formats=list(SEPARATORS.keys()) + [f".json.{compression}" for compression in COMPRESSIONS],
    )


def build_data_sources_parser(parser: ArgumentParser) -> None:
    """Build the parser for the data-sources subcommand."""
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="Specify a file path to save.",
    )
    parser.add_argument(
        "--email",
        "-e",
        type=str,
        required=True,
        help="Email address for the API provided to contact you in case of issues.",
    )
    parser.set_defaults(func=data_sources)


def build_verify_parser(parser: ArgumentParser) -> None:
    """Build the parser for the verify subcommand."""
    parser.add_argument(
        "--names",
        "-n",
        type=list,
        required=True,
        help="List of scientific names to verify.",
    )

    parser.add_argument(
        "--email",
        "-e",
        type=str,
        required=True,
        help="Email address for the API provided to contact you in case of issues.",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="Output format for the verification results.",
    )

    parser.add_argument(
        "--with-all-matches",
        action="store_true",
        required=False,
        help="Include all matches in the verification results.",
    )

    parser.add_argument(
        "--with-capitalization",
        action="store_true",
        required=False,
        help="Include capitalization in the verification results.",
    )

    parser.add_argument(
        "--with-species-group",
        action="store_true",
        required=False,
        help="Include species group in the verification results.",
    )

    parser.add_argument(
        "--with-uninomial-fuzzy-match",
        action="store_true",
        required=False,
        help="Include uninomial fuzzy match in the verification results.",
    )

    parser.add_argument(
        "--with-stats",
        action="store_true",
        required=False,
        help="Include statistics in the verification results.",
    )

    parser.add_argument(
        "--main-taxon-threshold",
        type=float,
        default=0.6,
        required=False,
        help="Main taxon threshold for the verification.",
    )

    client = DataSourceClient(email="tmp@tmp.com")
    for data_source in client.iter_data_sources():
        parser.add_argument(
            f"--include-{data_source.arg_name}",
            action="store_true",
            required=False,
            help=f"Include '{data_source.title}' in the verification. {data_source.description}",
        )
        if data_source.arg_name != data_source.short_arg_name:
            parser.add_argument(
                f"--include-{data_source.short_arg_name}",
                action="store_true",
                required=False,
                help=f"Include '{data_source.title}' in the verification. {data_source.description}",
            )


def main() -> None:
    """Main entry point for the CLI."""
    parser: ArgumentParser = ArgumentParser()
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    build_data_sources_parser(subparsers.add_parser("data-sources", help="List all available data sources."))
    build_verify_parser(subparsers.add_parser("verify", help="Verify scientific names."))

    args = parser.parse_args()

    args.func(args)
