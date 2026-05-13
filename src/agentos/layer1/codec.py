from pathlib import Path
from ruamel.yaml import YAML
from .model import Project

_yaml = YAML()
_yaml.default_flow_style = False
_yaml.preserve_quotes = True


def load(path: Path) -> Project:
    with path.open("r") as f:
        data = _yaml.load(f)
    return Project.model_validate(data)


def dump(project: Project, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w") as f:
        _yaml.dump(project.model_dump(mode="json"), f)
    tmp.replace(path)
