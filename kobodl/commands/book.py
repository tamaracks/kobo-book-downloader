import os

import click
from tabulate import tabulate

from kobodl import actions, cli
from kobodl.commands.utils import boolAsEmoji
from kobodl.globals import Globals


@click.group(name='book', short_help='list and download books')
def book():
    pass


@book.command(name='get', short_help='download book')
@click.option(
    '-u',
    '--user',
    type=click.STRING,
    help='Required when multiple accounts exist. Use either Email or UserKey',
)
@click.option(
    '-o',
    '--output-dir',
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    default='kobo_downloads',
)
@click.option(
    '-a', '--get-all', is_flag=True,
)
@click.argument('product-id', nargs=-1, type=click.STRING)
@click.pass_obj
def get(ctx, user, output_dir, get_all, product_id):
    if len(Globals.Settings.UserList.users) == 0:
        click.echo('error: no users found.  Did you `kobodl user add`?', err=True)
        exit(1)

    if not user:
        if len(Globals.Settings.UserList.users) > 1:
            click.echo('error: must provide --user option when more than 1 user exists.')
            exit(1)
        # Exactly 1 user account exists
        usercls = Globals.Settings.UserList.users[0]
    else:
        # A user was passed
        usercls = Globals.Settings.UserList.getUser(user)
        if not usercls:
            click.echo(f'error: could not find user with name or id {user}')
            exit(1)

    if get_all and len(product_id):
        click.echo(
            'error: cannot pass product IDs when --get-all is used. Use one or the other.',
            err=True,
        )
        exit(1)
    if not get_all and len(product_id) == 0:
        click.echo('error: must pass at least one Product ID, or use --get-all', err=True)
        exit(1)

    os.makedirs(output_dir, exist_ok=True)
    if get_all:
        actions.GetBookOrBooks(usercls, output_dir)
    else:
        for pid in product_id:
            output = actions.GetBookOrBooks(usercls, output_dir, productId=pid)


@book.command(name='list', help='list books')
@click.option(
    '-u',
    '--user',
    type=click.STRING,
    required=False,
    help='Limit list to a single user. Use either Email or UserKey',
)
@click.option('--read', is_flag=True, help='include books marked as read')
@click.pass_obj
def list(ctx, user, read):
    userlist = Globals.Settings.UserList.users
    if user:
        userlist = [Globals.Settings.UserList.getUser(user)]
    books = actions.ListBooks(userlist, read)
    headers = ['Title', 'Author', 'RevisionId', '🗃️', '🎧', 'Owner']
    data = sorted(
        [
            (
                book.Title,
                book.Author,
                book.RevisionId,
                boolAsEmoji(book.Archived),
                boolAsEmoji(book.Audiobook),
                book.Owner.Email,
            )
            for book in books
        ]
    )
    click.echo(tabulate(data, headers, tablefmt=ctx['fmt']))


cli.add_command(book)
