import sys
import click
import logging
import asyncio
import asyncpg
import discord
import importlib
import contextlib

from AggyBot import AggyBot, initial_extensions
from cogs.utils.db import Table

from pathlib import Path

import config
import traceback

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def run_bot():
    loop = asyncio.get_event_loop()
    kwargs = {
        'command_timeout': 60,
        'max_size': 20,
        'min_size': 20,
    }
    try:
        pool = loop.run_until_complete(Table.create_pool(config.postgresql, **kwargs))
    except Exception as e:
        click.echo('Could not set up PostgreSQL. Exiting.', file=sys.stderr)
        return;

    bot = AggyBot()
    bot.pool = pool
    bot.run()


@click.group(invoke_without_command=True, options_metavar='[options]')
@click.pass_context
def main(ctx):
    """Launches the bot."""
    if ctx.invoked_subcommand is None:
        run_bot()


@main.group(short_help='database stuff', options_metavar='[options]')
def db():
    pass


@db.command(short_help='initialises the databases for the bot', options_metavar='[options]')
@click.argument('cogs', nargs=-1, metavar='[cogs]')
@click.option('-q', '--quiet', help='less verbose output', is_flag=True)
def init(cogs, quiet):
    """This manages the migrations and database creation system for you."""

    run = asyncio.get_event_loop().run_until_complete
    try:
        run(Table.create_pool(config.postgresql))
    except Exception:
        click.echo(f'Could not create PostgreSQL connection pool.\n{traceback.format_exc()}', err=True)
        return

    if not cogs:
        cogs = initial_extensions
    else:
        cogs = [f'cogs.{e}' if not e.startswith('cogs.') else e for e in cogs]

    for ext in cogs:
        try:
            importlib.import_module(ext)
        except Exception:
            click.echo(f'Could not load {ext}.\n{traceback.format_exc()}', err=True)
            return

    for table in Table.all_tables():
        try:
            created = run(table.create(verbose=not quiet, run_migrations=False))
        except Exception:
            click.echo(f'Could not create {table.__tablename__}.\n{traceback.format_exc()}', err=True)
        else:
            if created:
                click.echo(f'[{table.__module__}] Created {table.__tablename__}.')
            else:
                click.echo(f'[{table.__module__}] No work needed for {table.__tablename__}.')


if __name__ == '__main__':
    main()
