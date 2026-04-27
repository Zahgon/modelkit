import time
from collections import OrderedDict, defaultdict
from contextlib import contextmanager
from typing import Dict, Generator, List, Set, Union

from tabulate import tabulate

from modelkit.core.model import Model
from modelkit.core.profilers.base import BaseProfiler


class SimpleProfiler(BaseProfiler):
    """This simple profiler records the duration of model prediction in seconds,
    and compute the net percentage duration of each sub models via 'model_dependencies'.
    Usage:
        model = modelkit.load_model(...)
        profiler = SimpleProfiler(model)
        res = model(item)
        profiler.summary() # return profiling result (Dict) or str

    Attributes:
        recording_hook (Dict[str, float]): record start/end time of each model call
        durations (List[float]): record duration of each model call
        net_durations (List[float]): record net duration of each model call. Net
            duration is the duration minus all the other sub models' duration.
        graph (Dict[str, Set]): model dependencies graph, get all direct children names
            (Set[str])
        graph_calls (Dict[str, Dict[str, int]]): record all model calls
            e.g
            {
                "pipeline": {
                    "__main__": 1, # "pipeline" is called once
                    "model_a": 2,
                    "model_b": 1,
                    "model_c": 1,
                }
            }
    See test_simple_profiler.py for more details.
    """

    def __init__(self, model: Model) -> None:
        super().__init__(model)
        self.recording_hook: Dict[str, float] = {}
        self.durations = defaultdict(list)  # type: ignore
        self.net_durations = defaultdict(list)  # type: ignore
        graph: Dict[str, Set] = defaultdict(set)
        self.graph = self._build_graph(self.model, graph)
        self.graph_calls: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

    def start(self, model_name: str) -> None:
        pass

    def end(  # type: ignore
        self, model_name: str, sub_calls: Dict[str, int]  # type: ignore
    ) -> None:  # type: ignore
        pass

    @contextmanager
    def profile(self, model_name: str) -> Generator:  # type: ignore
        pass

    def summary(  # type: ignore
        self, *args, print_table: bool = False, **kwargs  # type: ignore
    ) -> Union[Dict[str, List], str]:  # type: ignore
        """Usage

            stat: Dict[str, List] = profiler.summary()
        or
            print(profiler.summary(print_table=True, tablefmt="fancy_grid"))

        See: https://pypi.org/project/tabulate/ for all available table formats.

        """
        pass

    def _get_current_sub_calls(self, model_name: str) -> Dict[str, int]:
        """Get the number of current sub model calls.
        Args:
            model_name (str)
        Returns:
            Dict[str, int]: sub model calls
        """
        pass

    def _get_all_subs(self, model_name: str) -> Set[str]:
        """Get the set of all sub model names."""
        pass

    def _compute_sub_calls_and_update_graph_calls(
        self, model_name: str, previous_calls: Dict[str, int]
    ) -> Dict[str, int]:
        """Infer all sub models call (`sub_calls`) using `previous_calls` and update
        `graph_calls` and the end of context manager.

        P.S With the 'shared' context manager, we can't directly record `sub_calls`,
            but only the current model call (incremented in
            self.graph_calls[model_name]["__main__"]).
            Using the counts in "__main__" of all models, we deduce all sub models
            calls.

        Args:
            model_name (str): current model name
            previous_calls (Dict[str, int]):

        Returns:
            Dict[str, int]: sub_calls
        """
        pass

    def _calculate_net_cost(self, duration: float, sub_calls: Dict[str, int]) -> float:
        """Compute net cost of each sub models. Subtracting model "duration" by
        "duration" of all direct sub model.

        Args:
            duration (float): model duration
            sub_calls (Dict[str, int]): number of calls of all sub_model

        Returns:
            float: net cost
        """
        pass
