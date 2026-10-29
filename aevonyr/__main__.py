"""Entry point: python3 -m aevonyr."""
import argparse
from .compat import backend_status, make_plan, execute_plan, CompatibilityError
from .i18n import LANGUAGES, CATALOG, install_language_pack
from .diagnostics import diagnose, format_report

def main():
    parser = argparse.ArgumentParser(description="Aevonyr OS desktop preview")
    parser.add_argument("--check", action="store_true", help="check runtime availability")
    parser.add_argument("--launcher", action="store_true", help="open fullscreen Aevonyr launcher")
    parser.add_argument("--app-hub", action="store_true", help="open Universal App Hub")
    parser.add_argument("--welcome", action="store_true", help="open Aevonyr first-run wizard")
    parser.add_argument("--updates", action="store_true", help="open software and firmware update center")
    parser.add_argument("--phone", action="store_true", help="open phone integration")
    parser.add_argument("--restore", action="store_true", help="open system restore and backup tools")
    parser.add_argument("--diagnose", action="store_true", help="show actual Linux system diagnostics")
    parser.add_argument("--launch", metavar="FILE", help="launch EXE/MSI or install APK")
    parser.add_argument("--languages", action="store_true", help="list installed interface languages")
    parser.add_argument("--install-language", metavar="JSON", help="install a community language pack")
    args = parser.parse_args()
    if args.languages:
        count = len(CATALOG["en"])
        for code, name in sorted(LANGUAGES.items()):
            filled = sum(bool(CATALOG[code].get(key)) for key in CATALOG["en"])
            print(f"{code:10} {name} — {filled}/{count} translated labels")
        return 0
    if args.install_language:
        try:
            code = install_language_pack(args.install_language)
        except (ValueError, OSError, UnicodeError) as exc:
            parser.exit(1, f"Language pack error: {exc}\n")
        print(f"Installed language pack: {code}")
        return 0
    if args.diagnose:
        print(format_report(diagnose()))
        return 0
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
    if args.launcher:
        from .launcher import AevonyrLauncher
        AevonyrLauncher().mainloop()
        return 0
    from .ui import AevonyrDesktop
    desktop = AevonyrDesktop()
    if args.app_hub:
        desktop.show("apps")
    elif args.restore:
        desktop.show("restore")
    elif args.updates:
        desktop.show("updates")
    elif args.phone:
        desktop.show("phone")
    if args.welcome:
        desktop.after(150, desktop.show_welcome)
    desktop.mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
