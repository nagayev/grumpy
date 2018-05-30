# -*- coding: utf-8 -*-

"""Console script for grumpy_tools."""
import os
import sys
from StringIO import StringIO
from pkg_resources import resource_filename, Requirement, DistributionNotFound

import click

from . import grumpc, grumprun, pydeps


@click.group('grumpy')
def main(args=None):
    """Console script for grumpy_tools."""
    return 0


@main.command('transpile')
@click.argument('script', type=click.File('rb'))
@click.option('-m', '-modname', '--modname', default='__main__', help='Python module name')
@click.option('--pep3147', is_flag=True, help='Put the transpiled outputs on a __pycache__ folder')
def transpile(script=None, modname=None, pep3147=False):
    """
    Translates the python SCRIPT file to Go, then prints to stdout
    """
    _ensure_gopath(raises=False)

    output = grumpc.main(stream=script, modname=modname, pep3147=pep3147)
    click.echo(output)
    sys.exit(0)


@main.command('run')
@click.argument('file', required=False, type=click.File('rb'))
@click.option('-c', '--cmd', help='Program passed in as string')
@click.option('-m', '-modname', '--modname', help='Run run library module as a script')
def run(file=None, cmd=None, modname=None, pep3147=True):
    _ensure_gopath()

    if modname:
        stream = None
    elif file:
        stream = StringIO(file.read())
    elif cmd:
        stream = StringIO(cmd)
    else:   # Read from STDIN
        stream = StringIO(click.get_text_stream('stdin').read())

    if stream is not None:
        stream.seek(0)
        stream.name = '__main__.py'

    result = grumprun.main(stream=stream, modname=modname, pep3147=pep3147)
    sys.exit(result)


@main.command('depends')
@click.argument('script')
@click.option('-m', '-modname', '--modname', default='__main__', help='Python module name')
def depends(script=None, modname=None):
    """
    Discover with modules are needed to run the 'script' provided
    """
    _ensure_gopath()
    result = pydeps.main(script=script, modname=modname)
    sys.exit(result)


def _ensure_gopath(raises=True):
    environ_gopath = os.environ.get('GOPATH', '')

    try:
        runtime_gopath = resource_filename(
            Requirement.parse('grumpy-runtime'),
            'grumpy_runtime/data/gopath',
        )
    except DistributionNotFound:
        runtime_gopath = None

    if runtime_gopath and runtime_gopath not in environ_gopath:
        gopaths = environ_gopath.split(':') + [runtime_gopath]
        new_gopath = os.pathsep.join([p for p in gopaths if p])  # Filter empty ones
        if new_gopath:
            os.environ['GOPATH'] = new_gopath

    if raises and not runtime_gopath and not environ_gopath:
        raise click.ClickException("Could not found the Grumpy Runtime 'data/gopath' resource.\n"
                                   "Is 'grumpy-runtime' package installed?")


if __name__ == "__main__":
    import sys
    sys.exit(main())
