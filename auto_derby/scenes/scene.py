# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, Text, Type, TypeVar

import cast_unknown as cast

from .. import app


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
            app.log.text("already in: %s" % name, level=app.DEBUG)
        else:
            app.log.text("enter: %s -> %s" % (ctx.scene.name(), name))
            ctx.scene = cls._enter(ctx)
            app.log.text("entered: %s" % name)
        return cast.instance(ctx.scene, cls)
