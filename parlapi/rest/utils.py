# -*- coding: utf-8 -*-

from sqlalchemy.orm import joinedload


def prefetched(model, paths):
    """
    Builds a joinedload query on model.
    Paths specify what to join - each path should be a dot-separated attribute
    path from the model.
    """

    def load_from_path(path):
        parts = path.split('.')
        load = joinedload(parts[0])
        for part in parts[1:]:
            load = load.joinedload(part)
        return load

    options = [load_from_path(path) for path in paths]

    def query(id=None):
        q = model.query
        for option in options:
            q = q.options(option)
        if id is not None:
            q = q.filter_by(id=id)
        return q

    return query
