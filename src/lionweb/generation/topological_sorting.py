from typing import Dict, List, cast

from lionweb.language import Classifier, Concept, Containment, Interface


def _identify_topological_deps(
    classifiers: List[Classifier], id_to_concept
) -> Dict[str, List[str]]:
    graph: Dict[str, List[str]] = {cast(str, el.get_id()): [] for el in classifiers}
    for c in classifiers:
        if isinstance(c, Concept):
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
        elif isinstance(c, Interface):
            c_id = cast(str, c.get_id())
            for i in c.get_extended_interfaces():
                graph[c_id].append(cast(str, i.get_id()))
            for f in c.get_features():
                if isinstance(f, Containment):
                    f_type = f.get_type()
                    if f_type and cast(str, f_type.get_id()) in id_to_concept:
                        graph[cast(str, c_id)].append(cast(str, f_type.get_id()))
        else:
            raise ValueError()
    return graph


def topological_classifiers_sort(classifiers: List[Classifier]) -> List[Classifier]:
    id_to_concept = {el.get_id(): el for el in classifiers}

    # Build graph edges: child -> [parents]
    graph: Dict[str, List[str]] = _identify_topological_deps(classifiers, id_to_concept)

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
