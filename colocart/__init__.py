#!/usr/bin/env python3

"""
Copyright 2020 The Johns Hopkins University Applied Physics Laboratory.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


                        |==
     |------------------/
      \ \ \ \ \ \ \ \ \/
       \ \ \ \ \ \ \ \/
        ^^^^^^^^^^^...
                   \|
         ^^^^^^^^^^^^
         O O        OO

          COLOCART
"""


import configparser
import datetime
import mimetypes
import os
import subprocess
import sys

import boto3
import click
import colored
from colored import stylize


def upload_directory(
    directory: str,
    bucket_name: str,
    profile_name: str = None
) -> bool:

    session = boto3.Session(profile_name=profile_name)
    s3 = session.resource("s3")

    for root, dirs, files in os.walk(directory):
        for name in files:
            path = root.split(os.path.sep)
            path.append(name)
            mimetype = mimetypes.guess_type(os.path.sep.join(path))[0]
            if mimetype is None:
                print("Skipping file {} with no MIME type.".format(name))
                continue
            print(mimetype + "\t" + os.path.sep.join(path))
            s3.Bucket(bucket_name).upload_file(
                os.path.sep.join(path),
                os.path.sep.join(path[2:]),
                ExtraArgs={
                    "ContentType": mimetype
                }
            )
    return True


def print_succeed(val: str):
    """
    Print in green!
    """
    if len(val.split("\n")) > 1:
        val = val
    else:
        val = "🛒   {}".format(val)
    click.echo(stylize(val, colored.fg("green"), colored.attr('bold')))


def print_warn(val: str):
    """
    Print a warning.
    """
    if len(val.split("\n")) > 1:
        val = val
    else:
        val = "🛒   {}".format(val)
    click.echo(stylize(val, colored.fg("yellow")))


def print_error(val: str):
    """
    Print an error.
    """
    if len(val.split("\n")) > 1:
        val = val
    else:
        val = "🛒   {}".format(val)
    click.echo(stylize(val, colored.fg("red"), colored.attr("bold")))


def print_info(val: str):
    """
    Print in green!
    """
    if len(val.split("\n")) > 1:
        val = val
    else:
        val = "🛒   {}".format(val)
    click.echo(stylize(val, colored.fg("blue")))


@click.group()
def cli():
    pass


@cli.command('build')
@click.argument('project')
def build(project: str):
    print_info(f"Building {project}...")

    starting_directory = os.getcwd()

    if not os.path.isdir(project):
        print_error(f"No such directory [{project}].")
        sys.exit(1)

    os.chdir(project)


    subprocess.check_output("""
        echo "export default {
        \\\"commit\\\": \\\"$(git rev-parse HEAD)\\\",
        \\\"user\\\": \\\"$USER\\\",
        \\\"creation\\\": new Date(""" + str(
            int(datetime.datetime.now().timestamp() * 1000)
            ) + """),
    };"  > src/_build_info.js
    """, shell=True)

    build_output = subprocess.run(
        "yarn build",
        shell=True,
        stdout=subprocess.PIPE,
    )

    if "Compiled" not in build_output.stdout.decode('utf8'):
        print_error("Build failed:")
        print_error("="*80)
        print_error(build_output.stdout.decode('utf8'))
        print_error("="*80)
        print_error("Failed with errors, aborting.")
        sys.exit(1)

    os.chdir(starting_directory)
    print_succeed("Build complete.")
    sys.exit(0)


@cli.command('deploy')
@click.argument('project', default=".")
@click.option('--profile-name', default=None)
def deploy(project: str, profile_name: str):
    print_info(f"Deploying {project}...")

    starting_directory = os.getcwd()

    if project == ".":
        project = starting_directory

    if not os.path.isfile(project + "/colocart.cfg"):
        print_error(f"The project [{project}] has no colocart.cfg.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(project + "/colocart.cfg")
    
    if not os.path.isdir(project):
        print_error(f"No such directory [{project}].")
        sys.exit(1)

    bdir = config['BUILD'].get("BuildDirectory", "build")
    if not os.path.isdir(project + "/" + bdir):
        print_error(f"The project [{project}] has no build directory (" + bdir + ").")
        print_warn(f"Have you run the 'build' command yet?")
        sys.exit(1)


    try:
        upload_directory(
            "{}/{}".format(project, bdir),
            config['UPLOAD']['BucketName'],
            profile_name=profile_name
        )
    except Exception as e:
        print_error(f"Upload to bucket [] failed:")
        print(e)
        print_warn("Check your AWS permissions?")
        sys.exit(1)

    os.chdir(starting_directory)
    print_succeed("Deploy complete.")
    sys.exit(0)


def main():
    cli()


if __name__ == "__main__":
    main()
