from datetime import date

from src.main import build_parser


def test_parser_accepts_date_override() -> None:
    args = build_parser().parse_args(["--mode", "manual", "--date", "2026-03-11"])

    assert args.mode == "manual"
    assert args.date == date(2026, 3, 11)
