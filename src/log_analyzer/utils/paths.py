from pathlib import Path


def has_matching_name(output: Path, inputs: list[Path]) -> bool:
    """Evaluates if the output and any input share a filename stem in the same directory."""
    return any(
        output.parent.resolve() == input_path.parent.resolve() and output.stem == input_path.stem
        for input_path in inputs
    )
