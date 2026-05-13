import pytest
from agentos.cli import main


def test_main_no_args_prints_help_and_exits_2(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2
    err = capsys.readouterr().err
    assert "usage:" in err.lower()


def test_main_help_flag_prints_help_and_exits_0(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert "usage:" in out.lower()
