import warnings

import elasticsearch.exceptions

from .models import ALL_MODELS


__all__ = ('initialize_indexes_by_model',)


def initialize_indexes_by_model(models=None, using='default', fail_gracefully=False):
    """Initialize models. If a list of ``models`` is supplied,
    then only those models will be initialized. Otherwise all known models will be initialized.

    If ``using`` is supplied similar to the expectations of `elasticsearch_dsl` usage,
    the connection name or instance supplied will be used to initialize the models.
    If ``fail_gracefully`` is true, this function will not raise an error on connection problems, but it instead will supply a ``RuntimeWarning``.

    """
    if not models:
        models = ALL_MODELS
    for model in models:
        try:
            model.init(using=using)
        except elasticsearch.exceptions.ConnectionError:
            if fail_gracefully:
                warnings.warn(
                    f"connection error while initializing '{model!r}'",
                    RuntimeWarning,
                )
            else:
                raise
