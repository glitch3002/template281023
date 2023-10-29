#!/usr/bin/env python
# ipstack_interface.py
# A little CLI tool for interfacing with IPStack API and quering data for an IP address

import click
import ipaddress
import json
import os
import requests
import sys

from pathlib import Path

# Extend click default help flag
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)

# Required IP Address Input Argument
@click.option(
    "--ip_address",
    "-i",
    type=click.STRING,
    help="The IP Address you wish to Query IPStack for longitute and latitude",
    required=True,
)
@click.option(
    "--key_file_path",
    "-k",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        path_type=Path,
    ),
    default="./credentials/.key",
    help="Path to a file containing you IPStack Access Key. \n\n [Default: ./credentials/.key]",
)
@click.option(
    "--api_path",
    "-a",
    type=click.STRING,
    default="http://api.ipstack.com/",
    help="Endpoint for ipstack (useful for a mirror/mock). \n\n [Default: http://api.ipstack.com/]",
)
@click.option(
    "--debug/--silent",
    "-d",
    default=False,
    help="Enable better error messaging, useful if encountering problems. \n\n [Default: False]",
)
@click.option(
    "--json_return/--raw_return",
    "-j",
    type=click.BOOL,
    default=False,
    help="Specify if you wish to have output in text format or json returned (json will be raw from API). \n\n [Default: False]",
)
@click.option(
    "--full_geodata/--limited_geodata",
    "-f",
    type=click.BOOL,
    default=False,
    help="Specify if you wish to have all available geodata returned or just desired fields \n\n [Default: False]",
)
@click.version_option("1.0.0", prog_name="Ipstack Interface")
def main(
    key_file_path: Path,
    debug: bool,
    ip_address: str,
    api_path: str,
    json_return: bool,
    full_geodata: bool,
):
    # If not in debug mode disable traceback on failure
    if not debug:
        sys.tracebacklimit = 0

    # Check Input Values Valid
    _check_inputs(key_file_path, debug, ip_address)

    # Make Request
    response = _request_geodata_for_ip(
        key_file_path, debug, ip_address, api_path, full_geodata
    )

    # Process Response and return
    _process_response(response, debug, json_return)


def _check_inputs(key_file_path: Path, debug: bool, ip_address: str):
    """
    _check_inputs: A function to sanity check user input ontop of click type checking specifically that the access key file is not empty and that the ip address is a valid ip address
    :key_file_path: File Path to access key file
    :ip_address: str of an ip address
    """
    if debug:
        click.echo(f"Path to file containing IPStack Key used: {key_file_path}")

    # Check Key File is greater than zero
    if os.stat(key_file_path).st_size == 0:
        raise Exception(f"File {key_file_path} is of size zero")

    # Check IP entered is a valid IP Address
    if debug:
        click.echo(f"IP Address '{ip_address}' input")

    try:
        ipaddress.ip_address(ip_address)
    except:
        raise Exception(f"'{ip_address}' is not a valid IP address")


def _request_geodata_for_ip(
    key_file_path: Path, debug: bool, ip_address: str, api_path: str, full_geodata: bool
):
    """
    _request_geodata_for_ip: A function to briefly read access key and request geodata either
    :key_file_path: File Path to access key file
    :ip_address: str of an ip address
    :api_path: str of base base api path to add on ip address, access key and further optional parameters
    :full_geodata: bool flag set by user if they want all the info IPStack has available or longitude and latitude only
    """

    # Read Access Key From File
    # DO NOT EXPOSE FILE CONTENTS EVEN IN DEBUG MODE
    with open(key_file_path) as key_file:
        access_key = key_file.read()

    # Build Request
    request_str = f"{api_path}{ip_address}?access_key={access_key}"

    # If limited geodata set desired
    if not full_geodata:
        request_str += "&fields=longitude,latitude"

    # Make Request
    raw_response = requests.get(request_str)

    # Return raw response
    return raw_response


def _process_response(response, debug: bool, json_return: bool):
    """
    _process_response: A function to inspect the response from IPStack check it was successful and is json
    then if valid return either the raw json or in plain text
    :param response: class response from request module
    :param json_return: user fed in boolean flag for desired output json or plain text longitude and latitude
    """
    # Check status code sucess
    if response.status_code != 200:
        raise Exception(
            f"'{ipstack_response.code()}' response given to requests against {api_path}"
        )

    # Check response in json format as expected
    if response.headers["content-type"].find("application/json") == -1:
        # Silent by default as always printing invalid responses could be quite noisy on logs
        if debug:
            click.echo("Headers::")
            click.echo(response.headers["content-type"])
        else:
            raise Exception("Response from IPStack not JSON as expected")

    # Check longitude and latitude present in response
    _check_json_for(response, "longitude", debug)
    _check_json_for(response, "latitude", debug)

    # Response to output flag approproately do you want json or raw
    if json_return:
        click.echo(response.json())
    else:
        for entry in response.json():
            click.echo(f"{entry}: {response.json()[entry]}")


def _check_json_for(response, value_key: str, debug: bool):
    """
    _check_json_for small utility function to check json for key and raise exception if not found
    """
    try:
        response.json()[value_key]
    except:
        if debug:
            click.echo("JSON::")
            click.echo(response.json)
        raise Exception(f"Unable to find {value_key} in response")


if __name__ == "__main__":
    main()
