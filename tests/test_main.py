from src.app import main
import runpy
import sys


def test_main_output_and_return(capsys):
    result = main()
    captured = capsys.readouterr()

    assert "Hello from template!" in captured.out

    assert result == 2


def test_main_block():
    # Remove the module from sys.modules if it exists.
    module_name = "src.app"  # adjust the module path as needed
    if module_name in sys.modules:
        del sys.modules[module_name]

    runpy.run_module(module_name, run_name="__main__")
