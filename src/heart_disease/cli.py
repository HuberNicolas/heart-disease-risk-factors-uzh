"""Command line interface: `heart-disease run` and `heart-disease info`."""

import argparse
from pathlib import Path

import pandas as pd

from .data import FeatureSet, Location, load_location, select_features


def _locations(values: list[str] | None) -> list[Location]:
    return [Location(v) for v in values] if values else list(Location)


def cmd_run(args: argparse.Namespace) -> None:
    from .pipeline import Settings, run, write_overview

    settings = Settings(
        seed=args.seed,
        top_k=args.top_k,
        feature_set=FeatureSet.original() if args.original_features else FeatureSet(),
        embeddings=not args.skip_embeddings,
    )
    all_metrics = []
    for location in _locations(args.location):
        print(f"Analysing {location.label} …", flush=True)
        metrics = run(location, args.output, settings)
        print(metrics.drop(columns="location").to_string(index=False, float_format="%.2f"), end="\n\n")
        all_metrics.append(metrics)
    overview = write_overview(pd.concat(all_metrics), args.output)
    print(f"Results written to {args.output}/ (overview: {overview})")


def cmd_info(args: argparse.Namespace) -> None:
    feature_set = FeatureSet.original() if args.original_features else FeatureSet()
    rows = []
    for location in _locations(args.location):
        df = load_location(location)
        X, y = select_features(df, feature_set)
        counts = y.value_counts().reindex(range(5), fill_value=0)
        rows.append({"location": location.label, "patients": len(df), "features": X.shape[1], **counts.to_dict()})
    print(pd.DataFrame(rows).to_string(index=False))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="heart-disease", description=__doc__)
    sub = parser.add_subparsers(required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "-l", "--location", action="append", choices=[loc.value for loc in Location],
        help="location to analyse (repeatable; default: all four)",
    )  # fmt: skip
    common.add_argument(
        "--original-features", action="store_true",
        help="use the feature set of 2021, including patient ID, dates and the angiography results",
    )  # fmt: skip

    run = sub.add_parser("run", parents=[common], help="run the analysis and write figures and metrics")
    run.add_argument("-o", "--output", type=Path, default=Path("results"), help="output folder (default: results)")
    run.add_argument("--seed", type=int, default=0, help="random seed (default: 0)")
    run.add_argument("--top-k", type=int, default=25, help="number of features to select (default: 25)")
    run.add_argument("--skip-embeddings", action="store_true", help="skip t-SNE, UMAP and the autoencoder")
    run.set_defaults(func=cmd_run)

    info = sub.add_parser("info", parents=[common], help="show patients, features and class distribution")
    info.set_defaults(func=cmd_info)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
