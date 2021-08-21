# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Protocol, Text, Type, TypeVar

import cast_unknown as cast

_LOGGER = logging.getLogger(__name__)


class SceneHolder(Protocol):
    scene: Scene


class AbstractScene(ABC):
    @classmethod
    @abstractmethod
    def name(cls) -> Text:
        ...

    @classmethod
    @abstractmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        ...


T = TypeVar("T", bound=AbstractScene)


class Scene(AbstractScene):
    @classmethod
    def enter(cls: Type[T], ctx: SceneHolder) -> T:
        name = cls.name()
        if ctx.scene.name() == name:
            _LOGGER.debug("already in: %s", name)
        else:
            _LOGGER.info("enter: %s", name)
            ctx.scene = cls._enter(ctx)
            _LOGGER.info("entered: %s", name)
        return cast.instance(ctx.scene, cls)
