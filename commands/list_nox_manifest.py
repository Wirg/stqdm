from __future__ import annotations

import functools
import json
import sys
from argparse import Namespace
from typing import Any

from nox import _options, tasks, workflow
from nox._option_set import Option
from nox._version import get_nox_version
from nox.logger import setup_logging
from nox.manifest import Manifest


def flag_pair_merge_func_with_no_noxfile(
    enable_name: str,
    disable_name: str,
    command_args: Namespace,
    noxfile_args: Namespace,  # pylint: disable=unused-argument
) -> bool:
    """Merge function for flag pairs. If the flag is set in the Noxfile or
    the command line params, return ``True`` *unless* the disable flag has been
    specified on the command-line.
    """

    command_value = getattr(command_args, enable_name)
    disable_value = getattr(command_args, disable_name)

    return command_value and not disable_value


def make_flag_pair_no_noxfile(
    name: str,
    enable_flags: tuple[str, str] | tuple[str],
    disable_flags: tuple[str, str] | tuple[str],
    default: bool = False,
    **kwargs: Any,
) -> tuple[Option, Option]:
    """Returns two options - one to enable a behavior and another to disable it.

    The positive option is considered to be available to the Noxfile, as
    there isn't much point in doing flag pairs without it.
    """
    disable_name = f"no_{name}"

    kwargs["action"] = "store_true"
    enable_option = Option(
        name,
        *enable_flags,
        noxfile=False,
        merge_func=functools.partial(flag_pair_merge_func_with_no_noxfile, name, disable_name),
        default=default,
        **kwargs,
    )

    kwargs["help"] = f"Disables {enable_flags[-1]} if it is enabled in the Noxfile."
    disable_option = Option(disable_name, *disable_flags, **kwargs)

    return enable_option, disable_option


_options.options.add_options(
    *make_flag_pair_no_noxfile(
        "json",
        ("--json",),
        ("--no-json",),
        group=_options.options.groups["general"],
        help="Should list parameters as json",
        default=True,
    ),
    *make_flag_pair_no_noxfile(
        "return_parametrized_sessions",
        ("--return-parametrized-sessions",),
        ("--no-return-parametrized-sessions", "--return-base-sessions"),
        group=_options.options.groups["general"],
        help="Should return parametrized sessions or base sessions",
        default=True,
    ),
    *make_flag_pair_no_noxfile(
        "list_python_versions",
        ("--list-python-versions",),
        ("--no-list-python-versions",),
        group=_options.options.groups["general"],
        help="Should list python version",
        default=False,
    ),
)


def main() -> None:
    """
    The goal of this command is to be able to list available sessions to use with Github Actions.
    See https://stackoverflow.com/a/66747360
    """
    # Copied from https://github.com/wntrblm/nox/blob/6646b24d62e69442a55502e460e33c252d54beb4/nox/__main__.py
    args = _options.options.parse_args()

    if args.help:
        _options.options.print_help()
        return

    if args.version:
        print(get_nox_version(), file=sys.stderr)
        return

    setup_logging(color=args.color, verbose=args.verbose, add_timestamp=args.add_timestamp)

    # Execute the appropriate tasks.
    exit_code = workflow.execute(
        global_config=args,
        workflow=(
            tasks.load_nox_module,
            tasks.merge_noxfile_options,
            tasks.discover_manifest,
            tasks.filter_manifest,
            list_manifest_information,
        ),
    )

    # Done; exit.
    sys.exit(exit_code)


def _produce_json_listing(manifest: Manifest) -> None:
    # From https://github.com/wntrblm/nox/pull/665
    report = []
    for session, selected in manifest.list_all_sessions():
        if selected:
            report.append(
                {
                    "session": session.friendly_name,
                    "name": session.name,
                    "description": session.description or "",
                    "python": session.func.python,
                    "tags": session.tags,
                    "call_spec": getattr(session.func, "call_spec", {}),
                }
            )
    print(json.dumps(report))


def list_manifest_information(manifest: Manifest, global_config: Namespace) -> int:
    """Tasks that lists sessions in the manifest and print it to stdout.

    Args:
        manifest (~.Manifest): The manifest of sessions to be run.
        global_config (~nox.main.GlobalConfig): The global configuration.

    Returns:
        Exit Code 0
    """
    if global_config.json:
        _produce_json_listing(manifest)
        return 0
    if global_config.list_python_versions:
        python_versions = {session.func.python for session in manifest if isinstance(session.func.python, str)}
        print(json.dumps(sorted(python_versions)))
        return 0
    if global_config.return_parametrized_sessions:
        session_names = [session.friendly_name for session in manifest]
    else:
        session_names = list({session.name for session in manifest})
    print(json.dumps(session_names))
    return 0


if __name__ == "__main__":
    main()
