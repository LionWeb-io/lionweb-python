from typing import cast

from lionweb.language import Classifier, Concept, Containment, Interface


def _identify_topological_deps(
    classifiers: list[Classifier], id_to_concept: dict
) -> dict[str, list[str]]:
    """Build a dependency graph mapping each classifier ID to the IDs it depends on.

    A classifier depends on its extended concept/interfaces, the interfaces it
    implements, and the (concept) types of its containments — but only for
    dependencies that are themselves part of `classifiers`.

    Args:
        classifiers: The classifiers to analyze.
        id_to_concept: Mapping from classifier ID to classifier, restricted to
            the classifiers of interest; used to filter out external dependencies.

    Returns:
        dict[str, list[str]]: Adjacency list mapping each classifier ID to the
        list of IDs it depends on.

    Raises:
        ValueError: If a classifier is neither a Concept nor an Interface.
    """
    graph: dict[str, list[str]] = {cast(str, el.get_id()): [] for el in classifiers}
    for c in classifiers:
        match c:
            case Concept():
                c_id = cast(str, c.get_id())
                ec = c.get_extended_concept()
                if ec and cast(str, ec.get_id()) in id_to_concept:
                    graph[c_id].append(cast(str, ec.get_id()))
                for i in c.get_implemented():
                    graph[c_id].append(cast(str, i.get_id()))
                for f in c.get_features():
                    if isinstance(f, Containment):
                        f_type = f.get_type()
                        if f_type and cast(str, f_type.get_id()) in id_to_concept:
                            graph[cast(str, c_id)].append(cast(str, f_type.get_id()))
            case Interface():
                c_id = cast(str, c.get_id())
                for i in c.get_extended_interfaces():
                    graph[c_id].append(cast(str, i.get_id()))
                for f in c.get_features():
                    if isinstance(f, Containment):
                        f_type = f.get_type()
                        if f_type and cast(str, f_type.get_id()) in id_to_concept:
                            graph[cast(str, c_id)].append(cast(str, f_type.get_id()))
            case _:
                raise ValueError(f"Unsupported classifier type: {type(c).__name__}")
    return graph


def topological_classifiers_sort(classifiers: list[Classifier]) -> list[Classifier]:
    """Sort classifiers so that each one appears after the classifiers it depends on.

    Dependencies considered are: extended concepts/interfaces, implemented
    interfaces, and containment target types (limited to the given classifiers).
    The sort is a depth-first post-order traversal of the dependency graph.

    Args:
        classifiers: The classifiers to sort.

    Returns:
        list[Classifier]: The classifiers in topological (dependency-first) order.
    """
    id_to_concept = {el.get_id(): el for el in classifiers}

    # Build graph edges: child -> [parents]
    graph: dict[str, list[str]] = _identify_topological_deps(classifiers, id_to_concept)

    visited = set()
    sorted_list = []

    def visit(name: str):
        if name in visited:
            return
        visited.add(name)
        if name in graph:
            for dep in graph[name]:
                visit(dep)
        if name in id_to_concept:
            sorted_list.append(id_to_concept[name])

    for c in classifiers:
        visit(cast(str, c.get_id()))

    return sorted_list
