import os
import subprocess


class ToolRegistry(type):
    def __init__(cls, name, bases, nmspc):
        super(ToolRegistry, cls).__init__(name, bases, nmspc)
        if not hasattr(cls, 'registry'):
            cls.registry = set()
        cls.registry.add(cls)
        cls.registry -= set(bases) # Remove base classes
    # Metamethods, called on class objects:
    def __iter__(cls):
        return iter(cls.registry)
    def __str__(cls):
        if cls in cls.registry:
            return cls.__name__
        return cls.__name__ + ": " + ", ".join([sc.__name__ for sc in cls])


class Tool(metaclass=ToolRegistry):

    @classmethod
    def is_present(cls, path):
        return False


class PreCommitTool(Tool):

    def run(self):
        os.system(["pre-commit", "run", "-a"])

    def is_present(path):
        if os.path.isfile(os.path.join(path, '.pre-commit-config.yaml')):
            return True
        return False


class ToxTool(Tool):
    def is_present(path):
        if os.path.isfile(os.path.join(path, 'tox.ini')):
            return True
        return False


class MakeTool(Tool):
    pass


class NpmTool(Tool):
    pass
