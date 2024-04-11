"""
Base classes for writing management commands (named commands which can
be executed through ``g2scli.py``).

Adapted from the django Management system.
"""
import argparse
import logging
import os
import sys
from argparse import ArgumentParser, HelpFormatter
import functools
import pkgutil
from importlib import import_module
from io import TextIOBase
from collections import defaultdict
from difflib import get_close_matches

import ncpa.g2scli as g2scli
from ncpa.g2scli.settings import config

ALL_CHECKS = "__all__"


class CommandError(Exception):
    """
    Exception class indicating a problem while executing a management
    command.

    If this exception is raised during the execution of a management
    command, it will be caught and turned into a nicely-printed error
    message to the appropriate output stream (i.e., stderr); as a
    result, raising this exception (with a sensible description of the
    error) is the preferred way to indicate that something has gone
    wrong in the execution of a command.
    """
    def __init__(self, *args, returncode=1, **kwargs):
        self.returncode = returncode
        super().__init__(*args, **kwargs)


class SystemCheckError(CommandError):
    """
    The system check framework detected unrecoverable errors.
    """

    pass


class CommandParser(ArgumentParser):
    """
    Customized ArgumentParser class to improve some error messages and prevent
    SystemExit in several occasions, as SystemExit is unacceptable when a
    command is called programmatically.
    """

    def __init__(
        self, *, missing_args_message=None, called_from_command_line=None, **kwargs
    ):
        self.missing_args_message = missing_args_message
        self.called_from_command_line = called_from_command_line
        super().__init__(**kwargs)

    def parse_args(self, args=None, namespace=None):
        # Catch missing argument for a better error message
        if self.missing_args_message and not (
            args or any(not arg.startswith("-") for arg in args)
        ):
            self.error(self.missing_args_message)
        return super().parse_args(args, namespace)

    def error(self, message):
        if self.called_from_command_line:
            super().error(message)
        else:
            raise CommandError("Error: %s" % message)

    def add_subparsers(self, **kwargs):
        parser_class = kwargs.get("parser_class", type(self))
        if issubclass(parser_class, CommandParser):
            kwargs["parser_class"] = functools.partial(
                parser_class,
                called_from_command_line=self.called_from_command_line,
            )
        return super().add_subparsers(**kwargs)


def handle_default_options(options):
    """
    Include any default options that all commands should accept here
    so that ManagementUtility can handle them before searching for
    user commands.
    """
    # if options.settings:
    #     os.environ["G2SCLI_SETTINGS_MODULE"] = options.settings
    if options.pythonpath:
        sys.path.insert(0, options.pythonpath)
    pass


class G2SCLIHelpFormatter(HelpFormatter):
    """
    Customized formatter so that command-specific arguments appear in the
    --help output before arguments common to all commands.
    """

    show_last = {
        "--version",
        "--verbosity",
        "--traceback",
        # "--settings",
        "--pythonpath",
    }

    def _reordered_actions(self, actions):
        return sorted(
            actions, key=lambda a: set(a.option_strings) & self.show_last != set()
        )

    def add_usage(self, usage, actions, *args, **kwargs):
        super().add_usage(usage, self._reordered_actions(actions), *args, **kwargs)

    def add_arguments(self, actions):
        super().add_arguments(self._reordered_actions(actions))


class OutputWrapper(TextIOBase):
    """
    Wrapper around stdout/stderr
    """

    def __init__(self, out, ending="\n"):
        self._out = out
        self.style_func = None
        self.ending = ending

    def __getattr__(self, name):
        return getattr(self._out, name)

    def flush(self):
        if hasattr(self._out, "flush"):
            self._out.flush()

    def isatty(self):
        return hasattr(self._out, "isatty") and self._out.isatty()

    def write(self, msg="", style_func=None, ending=None):
        ending = self.ending if ending is None else ending
        if ending and not msg.endswith(ending):
            msg += ending
        style_func = style_func or self.style_func
        self._out.write(style_func(msg))


class BaseCommand:
    """
    The base class from which all management commands ultimately
    derive.

    Use this class if you want access to all of the mechanisms which
    parse the command-line arguments and work out what code to call in
    response; if you don't need to change any of that behavior,
    consider using one of the subclasses defined in this file.

    If you are interested in overriding/customizing various aspects of
    the command-parsing and -execution behavior, the normal flow works
    as follows:

    1. ``g2scli.py`` loads the command class and calls its 
       ``run_from_argv()`` method.

    2. The ``run_from_argv()`` method calls ``create_parser()`` to get
       an ``ArgumentParser`` for the arguments, parses them, performs
       any environment changes requested by options like
       ``pythonpath``, and then calls the ``execute()`` method,
       passing the parsed arguments.

    3. The ``execute()`` method attempts to carry out the command by
       calling the ``handle()`` method with the parsed arguments; any
       output produced by ``handle()`` will be printed to standard
       output and, if the command is intended to produce a block of
       SQL statements, will be wrapped in ``BEGIN`` and ``COMMIT``.

    4. If ``handle()`` or ``execute()`` raised any exception (e.g.
       ``CommandError``), ``run_from_argv()`` will  instead print an error
       message to ``stderr``.

    Thus, the ``handle()`` method is typically the starting point for
    subclasses; many built-in commands and command types either place
    all of their logic in ``handle()``, or perform some additional
    parsing work in ``handle()`` and then delegate from it to more
    specialized methods as needed.

    Several attributes affect behavior at various steps along the way:

    ``help``django
        A short description of the command, which will be printed in
        help messages.

    ``stealth_options``
        A tuple of any options the command uses which aren't defined by the
        argument parser.
    """

    # Metadata about this command.
    help = ""

    # Configuration shortcuts that alter various logic.
    _called_from_command_line = False
    # Arguments, common to all commands, which aren't defined by the argument
    # parser.
    base_stealth_options = ("stderr", "stdout")
    # Command-specific options not defined by the argument parser.
    stealth_options = ()
    suppressed_base_arguments = set()

    def __init__(self, stdout=None, stderr=None):
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)

    def get_version(self):
        """
        Return the version, which should be correct for all built-in
        commands. User-supplied commands can override this method to
        return their own version.
        """
        return g2scli.get_version()

    def create_parser(self, prog_name, subcommand, **kwargs):
        """
        Create and return the ``ArgumentParser`` which will be used to
        parse the arguments to this command.
        """
        parser = CommandParser(
            prog="%s %s" % (os.path.basename(prog_name), subcommand),
            description=self.help or None,
            missing_args_message=getattr(self, "missing_args_message", None),
            called_from_command_line=getattr(self, "_called_from_command_line", None),
            **kwargs,
        )
        self.add_base_argument(
            parser,
            "--version",
            action="version",
            version=self.get_version(),
            help="Show program's version number and exit.",
        )
        self.add_base_argument(
            parser,
            "-v",
            "--verbosity",
            default=config['logging'].get('level','warning'),
            type=str,
            choices=['debug','info','warning','error','critical'],
            help=(
                "Verbosity level"
            ),
        )
        self.add_base_argument(
            parser,
            "--logfile",
            default=None,
            type=str,
            nargs='+',
            help="File for log messages instead of stdout/stderr",
        )
        self.add_base_argument(
            parser,
            "--stdout",
            action="store_true",
            help="Log to stdout/stderr as well as to --logfile",
            )
        self.add_base_argument(
            parser,
            "--logargs",
            default=None,
            type=str,
            help="Arguments to pass to logger, as key=value,key=value,etc"
            )
        self.add_base_argument(
            parser,
            "--pythonpath",
            help=(
                "A directory to add to the Python path, e.g. "
                '"/home/python/myproject".'
            ),
        )
        self.add_base_argument(
            parser,
            "--traceback",
            action="store_true",
            help="Raise on CommandError exceptions.",
        )
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.
        """
        pass

    def add_base_argument(self, parser, *args, **kwargs):
        """
        Call the parser's add_argument() method, suppressing the help text
        according to BaseCommand.suppressed_base_arguments.
        """
        for arg in args:
            if arg in self.suppressed_base_arguments:
                kwargs["help"] = argparse.SUPPRESS
                break
        parser.add_argument(*args, **kwargs)

    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command, derived from
        ``self.usage()``.
        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        """
        Set up any environment changes requested (e.g., Python path), then run this command. If the
        command raises a ``CommandError``, intercept it and print it sensibly
        to stderr. If the ``--traceback`` option is present or the raised
        ``Exception`` is not ``CommandError``, raise it.
        """
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])

        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop("args", ())
        handle_default_options(options)
        try:
            self.execute(*args, **cmd_options)
        except CommandError as e:
            if options.traceback:
                raise

            # SystemCheckError takes care of its own formatting.
            if isinstance(e, SystemCheckError):
                self.stderr.write(str(e), lambda x: x)
            else:
                self.stderr.write("%s: %s" % (e.__class__.__name__, e))
            sys.exit(e.returncode)
    
    def setup_logging(self, loggername='g2scli', *args, **options):
        logargs = {}
        if options.get('logargs'):
            kvpairs = options.get('logargs').split(',')
            for pair in kvpairs:
                k,v = pair.split('=')
                if v:
                    logargs[k] = v
        logging.basicConfig(
            format='%(asctime)s|%(levelname)-8s|%(message)s',
            level=getattr(logging, options.get('verbosity').upper()),
            encoding='utf-8',
            datefmt='%Y%m%d %H%M%S',
            **logargs
            )
        logger = logging.getLogger(loggername)
        formatter = logging.Formatter('%(asctime)s|%(levelname)-8s|%(message)s')
        if options.get('logfile'):
            for logfile in options.get('logfile'):
                fh = logging.FileHandler(logfile)
                fh.setLevel(getattr(logging, options.get('verbosity').upper()))
                fh.setFormatter(formatter)
                logger.addHandler(fh)
        if options.get('stdout') or (not options.get('logfile')):
            herr = logging.StreamHandler(self.stderr)
            herr.setFormatter(formatter)
            herr.setLevel(logging.WARNING)
            hout = logging.StreamHandler(self.stdout)
            hout.setFormatter(formatter)
            hout.setLevel(getattr(logging, options.get('verbosity').upper()))
            logger.addHandler(hout)
            logger.addHandler(herr)
        logger.propagate = False
        return logger

    def execute(self, *args, **options):
        """
        Try to execute this command, performing system checks if needed (as
        controlled by the ``requires_system_checks`` attribute, except if
        force-skipped).
        """
        if options.get("stdout"):
            self.stdout = OutputWrapper(options["stdout"])
        if options.get("stderr"):
            self.stderr = OutputWrapper(options["stderr"])

        # if self.requires_system_checks and not options["skip_checks"]:
        #     if self.requires_system_checks == ALL_CHECKS:
        #         self.check()
        #     else:
        #         self.check(tags=self.requires_system_checks)
        output = self.handle(*args, **options)
        if output:
            self.stdout.write(output)
        return output

    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError(
            "subclasses of BaseCommand must provide a handle() method"
        )


# class AppCommand(BaseCommand):
#     """
#     A management command which takes one or more installed application labels
#     as arguments, and does something with each of them.
#
#     Rather than implementing ``handle()``, subclasses must implement
#     ``handle_app_config()``, which will be called once for each application.
#     """
#
#     missing_args_message = "Enter at least one application label."
#
#     def add_arguments(self, parser):
#         parser.add_argument(
#             "args",
#             metavar="app_label",
#             nargs="+",
#             help="One or more application label.",
#         )
#
#     def handle(self, *app_labels, **options):
#         from django.apps import apps
#
#         try:
#             app_configs = [apps.get_app_config(app_label) for app_label in app_labels]
#         except (LookupError, ImportError) as e:
#             raise CommandError(
#                 "%s. Are you sure your INSTALLED_APPS setting is correct?" % e
#             )
#         output = []
#         for app_config in app_configs:
#             app_output = self.handle_app_config(app_config, **options)
#             if app_output:
#                 output.append(app_output)
#         return "\n".join(output)
#
#     def handle_app_config(self, app_config, **options):
#         """
#         Perform the command's actions for app_config, an AppConfig instance
#         corresponding to an application label given on the command line.
#         """
#         raise NotImplementedError(
#             "Subclasses of AppCommand must provide a handle_app_config() method."
#         )


class LabelCommand(BaseCommand):
    """
    A management command which takes one or more arbitrary arguments
    (labels) on the command line, and does something with each of
    them.

    Rather than implementing ``handle()``, subclasses must implement
    ``handle_label()``, which will be called once for each label.

    If the arguments should be names of installed applications, use
    ``AppCommand`` instead.
    """

    label = "label"
    missing_args_message = "Enter at least one %s." % label

    def add_arguments(self, parser):
        parser.add_argument("args", metavar=self.label, nargs="+")

    def handle(self, *labels, **options):
        output = []
        for label in labels:
            label_output = self.handle_label(label, **options)
            if label_output:
                output.append(label_output)
        return "\n".join(output)

    def handle_label(self, label, **options):
        """
        Perform the command's actions for ``label``, which will be the
        string as given on the command line.
        """
        raise NotImplementedError(
            "subclasses of LabelCommand must provide a handle_label() method"
        )




def find_commands(management_dir):
    """
    Given a path to a management directory, return a list of all the command
    names that are available.
    """
    command_dir = os.path.join(management_dir, "management/commands")
    return [
        name
        for _, name, is_pkg in pkgutil.iter_modules([command_dir])
        if not is_pkg and not name.startswith("_")
    ]


def load_command_class(app_name, name):
    """
    Given a command name and an application name, return the Command
    class instance. Allow all errors raised by the import process
    (ImportError, AttributeError) to propagate.
    """
    module = import_module("%s.commands.%s" % (app_name, name))
    return module.Command()


@functools.cache
def get_commands():
    """
    Return a dictionary mapping command names to their callback applications.

    Look for a management.commands package in django.core, and in each
    installed application -- if a commands package exists, register all
    commands in that package.

    Core commands are always included. If a settings module has been
    specified, also include user-defined commands.

    The dictionary is in the format {command_name: app_name}. Key-value
    pairs from this dictionary can then be used in calls to
    load_command_class(app_name, command_name)

    The dictionary is cached on the first call and reused on subsequent
    calls.
    """
    commands = {name: "ncpa.g2scli.management" for name in find_commands(
        os.path.abspath(os.path.dirname(__file__))
        )}

    # if not settings.configured:
    #     return commands
    #
    # for app_config in APPS:
    #     path = os.path.join(app_config.path, "management")
    #     commands.update({name: app_config.name for name in find_commands(path)})

    return commands



class ModularCommand:
    """
    Encapsulate the logic of the modular command system.
    """

    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
        if self.prog_name == "__main__.py":
            self.prog_name = "python g2scli"
        self.settings_exception = None

    def main_help_text(self, commands_only=False):
        """Return the script's main help text, as a string."""
        if commands_only:
            usage = sorted(get_commands())
        else:
            usage = [
                "",
                "Type '%s help <subcommand>' for help on a specific subcommand."
                % self.prog_name,
                "",
                "Available subcommands:",
            ]
            commands_dict = defaultdict(lambda: [])
            for name, app in get_commands().items():
                if app == "ncpa.g2scli.management":
                    app = "g2scli"
                else:
                    app = app.rpartition(".")[-1]
                commands_dict[app].append(name)
            for app in sorted(commands_dict):
                usage.append("")
                usage.append("[%s]" % app)
                for name in sorted(commands_dict[app]):
                    usage.append("    %s" % name)
            # Output an extra note if settings are not properly configured
            if self.settings_exception is not None:
                usage.append(
                   "Note that only core commands are listed "
                    "as settings are not properly configured (error: %s)."
                    % self.settings_exception
                )

        return "\n".join(usage)

    def fetch_command(self, subcommand):
        """
        Try to fetch the given subcommand, printing a message with the
        appropriate command called from the command line (usually
        "django-admin" or "manage.py") if it can't be found.
        """
        # Get commands outside of try block to prevent swallowing exceptions
        commands = get_commands()
        try:
            app_name = commands[subcommand]
        except KeyError:
            possible_matches = get_close_matches(subcommand, commands)
            sys.stderr.write("Unknown command: %r" % subcommand)
            if possible_matches:
                sys.stderr.write(". Did you mean %s?" % possible_matches[0])
            sys.stderr.write("\nType '%s help' for usage.\n" % self.prog_name)
            sys.exit(1)
        if isinstance(app_name, BaseCommand):
            # If the command is already loaded, use it directly.
            klass = app_name
        else:
            klass = load_command_class(app_name, subcommand)
        return klass
    
    def execute(self):
        """
        Given the command-line arguments, figure out which subcommand is being
        run, create a parser appropriate to that command, and run it.
        """
        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = "help"  # Display help if no arguments were given.

        # Preprocess options to extract --settings and --pythonpath.
        # These options could affect the commands that are available, so they
        # must be processed early.
        parser = CommandParser(
            prog=self.prog_name,
            usage="%(prog)s subcommand [options] [args]",
            add_help=False,
            allow_abbrev=False,
        )
        parser.add_argument("--settings")
        parser.add_argument("--pythonpath")
        parser.add_argument("args", nargs="*")  # catch-all
        try:
            options, args = parser.parse_known_args(self.argv[2:])
            handle_default_options(options)
        except CommandError:
            pass  # Ignore any option errors at this point.

        if subcommand == "help":
            if "--commands" in args:
                sys.stdout.write(self.main_help_text(commands_only=True) + "\n")
            elif not options.args:
                sys.stdout.write(self.main_help_text() + "\n")
            else:
                self.fetch_command(options.args[0]).print_help(
                    self.prog_name, options.args[0]
                )
        # Special-cases: We want 'django-admin --version' and
        # 'django-admin --help' to work, for backwards compatibility.
        elif subcommand == "version" or self.argv[1:] == ["--version"]:
            sys.stdout.write(g2scli.version.get_version() + "\n")
        elif self.argv[1:] in (["--help"], ["-h"]):
            sys.stdout.write(self.main_help_text() + "\n")
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)




