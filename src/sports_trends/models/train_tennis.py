"""Train the baseline tennis model."""

from __future__ import annotations

from ._train_core import train_sport


def train(**kwargs):
    return train_sport("tennis", **kwargs)


if __name__ == "__main__":
    print(train())
