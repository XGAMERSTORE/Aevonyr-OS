"""Entry point: python3 -m aevonyr."""
import argparse
from .compat import backend_status, make_plan, execute_plan, CompatibilityError

def main():
    parser = argparse.ArgumentParser(description="Aevonyr OS desktop preview")
    parser.add_argument("--check", action="store_true", help="check runtime availability")
    parser.add_argument("--launch", metavar="FILE", help="launch EXE/MSI or install APK")
    args = parser.parse_args()
    if args.check:
        for key, value in backend_status().items():
            print(f"{key}: {'available' if value else 'unavailable'}")
        return 0
    if args.launch:
        try:
            plan = make_plan(args.launch)
            print(f"Starting {plan.kind}: {plan.command}")
            execute_plan(plan)
        except (CompatibilityError, OSError) as exc:
            parser.exit(1, f"Error: {exc}\n")
        return 0
    from .ui import AevonyrDesktop
    AevonyrDesktop().mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
