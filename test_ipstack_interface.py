import ipstack_interface as ipstack
import os
import pytest
import time

# TODO check debug flag option messages


# Constants
TMP_DIRECTORY = "./.tmp"
EMPTY_FILE = "empty"
VALID_KEY_FILE = ".key"

DEFAULT_KEY_FILE = "./credentials/.key"
DEFAULT_DEBUG = False
DEFAULT_API_PATH = "http://api.ipstack.com/"
DEFAULT_JSON_RETURN = False

VALID_IPV4 = "8.8.8.8"
VALID_IPV6 = "2001:4860:4860::8888"
INVALID_IP_GIBBERISH = "GiBBERISH"
INVALID_IP_MALFORMED = "8.8.8."
INVALID_IP_NUM = 8
VALID_IPV4_EXPECTED_OUTPUT = (
    "latitude: 40.5369987487793\nlongitude: -82.12859344482422\n"
)
VALID_IPV4_EXPECTED_JSON_OUTPUT = (
    "{'latitude': 40.5369987487793, 'longitude': -82.12859344482422}\n"
)

# Constructed Constants
EMPTY_FILE_PATH = f"{TMP_DIRECTORY}/{EMPTY_FILE}"
VALID_KEY_FILE_PATH = f"{TMP_DIRECTORY}/{VALID_KEY_FILE}"


class successful_api_response:
    status_code = 200
    headers = {"content-type": "application/json"}

    def json():
        return {"latitude": 40.5369987487793, "longitude": -82.12859344482422}


class unsuccessful_api_response_400:
    status_code = 400


class unsuccessful_api_response_401:
    status_code = 401


class successful_api_response_wrong_content:
    status_code = 200
    headers = {"content-type": "text/html"}


class successful_api_response_lon_missing:
    status_code = 200
    headers = {"content-type": "application/json"}

    def json():
        return {"latitude": 40.5369987487793}


class successful_api_response_lat_missing:
    status_code = 200
    headers = {"content-type": "application/json"}

    def json():
        return {"latitude": 40.5369987487793}


class successful_api_response_json_missing:
    status_code = 200
    headers = {"content-type": "application/json"}

    def json():
        return {}


@pytest.fixture(scope="session", autouse=True)
def create_resources():
    # Create Temporary Directory for dummy files etc
    if not os.path.exists(TMP_DIRECTORY):
        os.makedirs(TMP_DIRECTORY)

    # Create Empty File
    empty_file = open(EMPTY_FILE_PATH, "w")

    with open(VALID_KEY_FILE_PATH, "w") as valid_key_file:
        valid_key_file.write("any_old_value_here")


@pytest.mark.unit
@pytest.mark.input_checks
def test_input_check_happy_day():
    """
    test_input_check_blank_key_file valid inputs excepted for IPv4 & IPv6
    """
    try:
        ipstack._check_inputs(VALID_KEY_FILE_PATH, False, VALID_IPV4)
        ipstack._check_inputs(VALID_KEY_FILE_PATH, False, VALID_IPV6)
    except:
        assert False
    else:
        assert True


@pytest.mark.unit
@pytest.mark.input_checks
def test_input_check_blank_key_file():
    """
    test_input_check_blank_key_file checks exception raised when access key file is blank
    """
    try:
        ipstack._check_inputs(EMPTY_FILE_PATH, False, VALID_IPV4)
    except:
        assert True
    else:
        assert False


@pytest.mark.unit
@pytest.mark.input_checks
def test_input_check_ip_gibberish():
    """
    test_input_check_ip_gibberish checks exception raised a number fed in for ip rather than string
    to be honest for this example this is silly
    """
    try:
        ipstack._check_inputs(VALID_KEY_FILE_PATH, False, INVALID_IP_GIBBERISH)
    except:
        assert True
    else:
        assert False


@pytest.mark.unit
@pytest.mark.input_checks
def test_input_check_ip_malformed():
    """
    test_input_check_ip_malformed checks exception raised for a mostly correct but malformed IP address
    """
    try:
        ipstack._check_inputs(VALID_KEY_FILE_PATH, False, INVALID_IP_MALFORMED)
    except:
        assert True
    else:
        assert False


# This exposed a bug in the check approach shouldn't be possible for this to get in as "click" type checks the input
# from the user is a str not a literally number but something to be careful of will make an integration test for this one specifically
# @pytest.mark.unit
# @pytest.mark.input_checks
# def test_input_check_ip_as_number():
#     """
#     test_input_check_ip_as_number checks exception raised a number fed in for ip rather than string
#     """
#     try:
#         ipstack._check_inputs(VALID_KEY_FILE_PATH, False, INVALID_IP_NUM)
#     except:
#         assert True
#     else:
#         assert False

# Test on this function need to be done at component level mocking the IPStack Server or integration level
# def _request_geodata_for_ip():


@pytest.mark.unit
@pytest.mark.process_response
def test_process_response_happy_path(capfd):
    """
    test processing of response does not exception as expected for valid expected json response
    """
    try:
        ipstack._process_response(
            successful_api_response, DEFAULT_DEBUG, DEFAULT_JSON_RETURN
        )
        out, err = capfd.readouterr()
    except:
        assert False
    else:
        assert out == VALID_IPV4_EXPECTED_OUTPUT


@pytest.mark.unit
@pytest.mark.process_response
def test_process_response_400():
    """
    test processing of response exceptions as expected for 400 Bad Request response
    """
    try:
        ipstack._process_response(
            unsuccessful_api_response_400, DEFAULT_DEBUG, DEFAULT_JSON_RETURN
        )
    except:
        assert True
    else:
        assert False


@pytest.mark.unit
@pytest.mark.process_response
def test_process_response_401():
    """
    test processing of response exceptions as expected for 401 forbidden response
    """
    try:
        ipstack._process_response(
            unsuccessful_api_response_401, DEFAULT_DEBUG, DEFAULT_JSON_RETURN
        )
    except:
        assert True
    else:
        assert False


@pytest.mark.unit
@pytest.mark.process_response
def test_process_response_wrong_content():
    """
    test processing of response exceptions as expected for 401 forbidden response
    """
    try:
        ipstack._process_response(
            unsuccessful_api_response_401, DEFAULT_DEBUG, DEFAULT_JSON_RETURN
        )
    except:
        assert True
    else:
        assert False


@pytest.mark.unit
@pytest.mark.process_response
def test_process_response_lon_missing():
    """
    test processing of response exceptions as expected for "successful" response but longitude missing
    """
    try:
        ipstack._process_response(
            successful_api_response_lon_missing, DEFAULT_DEBUG, DEFAULT_JSON_RETURN
        )
    except:
        assert True
    else:
        assert False


@pytest.mark.unit
@pytest.mark.process_response
def test_successful_api_response_lat_missing():
    """
    test processing of response outputs as expected for "successful" response but latitude missing
    """
    try:
        ipstack._process_response(
            successful_api_response_lon_missing, DEFAULT_DEBUG, DEFAULT_JSON_RETURN
        )
    except:
        assert True
    else:
        assert False


@pytest.mark.unit
@pytest.mark.process_response
def test_successful_api_response_json_missing():
    """
    test processing of response outputs as expected for "successful" response but json content being blank
    """
    try:
        ipstack._process_response(
            successful_api_response_json_missing, DEFAULT_DEBUG, DEFAULT_JSON_RETURN
        )
    except:
        assert True
    else:
        assert False


@pytest.mark.integration
def test_integration_happy_day(capfd):
    """
    test running the script from command line
    """
    # REQUIRES API KEY TO BE SET
    os.system("python3 ./ipstack_interface.py -i 8.8.8.8")
    out, err = capfd.readouterr()
    assert out == VALID_IPV4_EXPECTED_OUTPUT


@pytest.mark.integration
def test_integration_happy_day_json_flag(capfd):
    """
    test running the script from command line with -j flag
    """
    # REQUIRES API KEY TO BE SET
    os.system("python3 ./ipstack_interface.py -i 8.8.8.8 -j")
    out, err = capfd.readouterr()
    assert out == VALID_IPV4_EXPECTED_JSON_OUTPUT


@pytest.mark.integration
def test_integration_specific_ip_error(capfd):
    """
    test running the script with number literal instead of ip expected fail
    """
    expected_error = "ValueError: '8' does not appear to be an IPv4 or IPv6 address\n\n"
    expected_error += (
        "During handling of the above exception, another exception occurred:\n\n"
    )
    expected_error += "Exception: '8' is not a valid IP address\n" ""
    # REQUIRES API KEY TO BE SET
    os.system("python3 ./ipstack_interface.py -i 8")
    out, err = capfd.readouterr()
    assert err == expected_error
