"""Shared print helpers for pipeline stage headers and results."""


def print_stage_header(num: str, name: str, description: str) -> None:
    print(f"\n{'═' * 70}")
    print(f"  STAGE {num}: {name}")
    print(f"  {description}")
    print(f"{'═' * 70}")


def print_stage_result(num: str, name: str, details: dict, success: bool = True) -> None:
    icon = "✅" if success else "❌"
    print(f"\n{icon} Stage {num} · {name} complete")
    for k, v in details.items():
        print(f"   {k:<22} {v}")
