import bisect
import itertools
import json
import logging
import multiprocessing
import os
import sys
from time import perf_counter, sleep

import click
import humanize
from rich.console import Console
from rich.markup import escape
from rich.progress import Progress, track
from rich.table import Table
from rich.tree import Tree

from modelkit import ModelLibrary
from modelkit.api import create_modelkit_app
from modelkit.assets.cli import assets_cli
from modelkit.core.errors import ModelsNotFound
from modelkit.core.library import download_assets
from modelkit.core.model_configuration import list_assets
from modelkit.utils.serialization import safe_np_dump


@click.group()
def modelkit_cli():
    pass


modelkit_cli.add_command(assets_cli)


def _configure_from_cli_arguments(models, required_models, settings):
    models = list(models) or None
    required_models = list(required_models) or None
    if not (models or os.environ.get("MODELKIT_DEFAULT_PACKAGE")):
        raise ModelsNotFound(
            "Please add `your_package` as argument or set the "
            "`MODELKIT_DEFAULT_PACKAGE=your_package` env variable."
        )

    service = ModelLibrary(
        models=models,
        required_models=required_models,
        settings=settings,
    )
    return service


@modelkit_cli.command()
@click.argument("models", type=str, nargs=-1, required=False)
@click.option("--required-models", "-r", multiple=True)
def memory(models, required_models):
    """
    Show memory consumption of modelkit models.
    """
    pass


@modelkit_cli.command("list-assets")
@click.argument("models", type=str, nargs=-1, required=False)
@click.option("--required-models", "-r", multiple=True)
def list_assets_cli(models, required_models):
    """
    List necessary assets.

    List the assets necessary to run a given set of models.
    """
    pass


def add_dependencies_to_graph(g, model, configurations):
    pass


@modelkit_cli.command()
@click.argument("models", type=str, nargs=-1, required=False)
@click.option("--required-models", "-r", multiple=True)
def dependencies_graph(models, required_models):
    pass


@modelkit_cli.command()
@click.argument("models", type=str, nargs=-1, required=False)
@click.option("--required-models", "-r", multiple=True)
def describe(models, required_models):
    """
    Describe a library.

    Show settings, models and assets for a given library.
    """
    service = _configure_from_cli_arguments(models, required_models, {})
    service.describe()


@modelkit_cli.command()
@click.argument("model")
@click.argument("example")
@click.argument("models", type=str, nargs=-1, required=False)
@click.option("--n", "-n", default=100)
def time(model, example, models, n):
    """
    Benchmark a model on an example.

    Time n iterations of a model's call on an example.
    """
    service = _configure_from_cli_arguments(models, [model], {"lazy_loading": True})

    console = Console()

    t0 = perf_counter()
    model = service.get(model)
    console.print(
        f"{f'Loaded model `{model.configuration_key}` in':50} "
        f"... {f'{perf_counter()-t0:.2f} s':>10}"
    )

    example_deserialized = json.loads(example)
    console.print(f"Calling `predict` {n} times on example:")
    console.print(f"{json.dumps(example_deserialized, indent = 2)}")

    times = []
    for _ in track(range(n)):
        t0 = perf_counter()
        model(example_deserialized)
        times.append(perf_counter() - t0)

    console.print(
        f"Finished in {sum(times):.1f} s, "
        f"approximately {sum(times)/n*1e3:.2f} ms per call"
    )

    t0 = perf_counter()
    model([example_deserialized] * n)
    batch_time = perf_counter() - t0
    console.print(
        f"Finished batching in {batch_time:.1f} s, approximately"
        f" {batch_time/n*1e3:.2f} ms per call"
    )


@modelkit_cli.command("serve")
@click.argument("models", type=str, nargs=-1, required=False)
@click.option("--required-models", "-r", type=str, multiple=True)
@click.option("--host", type=str, default="localhost")
@click.option("--port", type=int, default=8000)
def serve(models, required_models, host, port):
    pass


@modelkit_cli.command("predict")
@click.argument("model_name", type=str)
@click.argument("models", type=str, nargs=-1, required=False)
def predict(model_name, models):
    """
    Make predictions for a given model.
    """
    lib = _configure_from_cli_arguments(models, [model_name], {})
    model = lib.get(model_name)
    while True:
        r = click.prompt(f"[{model_name}]>")
        if r:
            res = model(json.loads(r))
            click.secho(json.dumps(res, indent=2, default=safe_np_dump))


def worker(lib, model_name, q_in, q):
    pass


def writer(output, q, n_workers):
    pass


def writer_unordered(output, q, n_workers):
    pass


def reader(input, queues):
    pass


@modelkit_cli.command("batch")
@click.argument("model_name", type=str)
@click.argument("input", type=str)
@click.argument("output", type=str)
@click.option("--models", type=str, multiple=True)
@click.option("--processes", type=int, default=None)
@click.option("--unordered", is_flag=True)
def batch_predict(model_name, input, output, models, processes, unordered):
    """
    Barch predictions for a given model.
    """
    pass


@modelkit_cli.command("tf-serving")
@click.argument("mode", type=click.Choice(["local-docker", "local-process", "remote"]))
@click.argument("models", type=str, nargs=-1, required=False)
@click.option("--required-models", "-r", multiple=True)
@click.option("--verbose", is_flag=True)
def tf_serving(mode, models, required_models, verbose):
    pass


@modelkit_cli.command("download-assets")
@click.argument("models", type=str, nargs=-1, required=False)
@click.option("--required-models", "-r", multiple=True)
def download(models, required_models):
    """
    Download all assets necessary to run a given set of models
    """
    download_assets(
        models=list(models) or None, required_models=list(required_models) or None
    )
