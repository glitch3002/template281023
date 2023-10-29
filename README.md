# IP Stack Interface
CLI Application to allow interfacing with the IPStack API translating an IP address into geolocation.

## Setup
* * *
### Docker Build
- navigate to this directory
- `docker build . -t ` desired tag 


### Local
(Advisable to use venv)
- navigate to this directory
- install python3 if required
- python3 -m pip install -r ./requirements.txt
- create a file .key in a folder within this directory called ./credentials/ to contain your access key
- (This can be in another directory but you will need use -k option and specify file path)


## Usage
* * *
### Docker
https://hub.docker.com/r/glitch3002/ipstack
`docker pull glitch3002/ipstack:latest`

Easiest method for execution is to store your credentials within a file .key I have stored mine within a folder ./credentials from my current directory
and mount it into the container as so it picks it up as default. However you can mount it somewhere else within the container and use the -a flag 
to specify where you like.
`docker run -v ./credentials:/app/credentials -it glitch3002/ipstack:latest bash`

Simple example command below
`./ipstack_interface.py -i 8.8.8.8`
you should be able to use all local examples below


### Local
Use
`python3 ipstack_interface.py -i 8.8.8.8`
8.8.8.8 being an example IPv4 address
`python3 ipstack_interface.py -i 2001:4860:4860::8888`
2001:4860:4860::8888 being an example IPv6 address

Access Help
`python3 ipstack_interface.py -h`

Alternative Key file location being specified
`python3 ipstack_interface.py -i 8.8.8.8 -k ~/.credentials/.my_IPStack_key`

Alternative IPStack API Path, useful for mocking or potential mirrors
`python3 ipstack_interface.py -i 8.8.8.8 -a http://api.myIPStackMirror.com/`

Debug Mode for greater logging and stack traceback
`python3 ipstack_interface.py -i 8.8.8.8 -d`

Raw JSON Return, useful if someone has JSON tooling, to see raw return and for others downstream if they cannot modify this script to be able to get values out.
`python3 ipstack_interface.py -i 8.8.8.8 -j`

## Linting & Testing
* * *
### Linting
Python module black used for linting and formating. 

Assuming you are in the current directory with the requirements installed
`black ./`
or
`python3 -m black ./`

Should trigger linting and formatting.

### Testing
Broken down into unit and one integration Test all using PyTest
- Run all `python3 -m pytest -v` (verbose)

I put in some marks for different areas of the code somewhat overkill in this example but in a larger program useful to test sections.
- Run unit`python3 -m pytest -v -m unit`


For coverage metrics
`coverage run -m pytest -v`

`coverage report`

I would in a practical example write a component test mocking the IPStack API
Also as the need arose I would start looking at ways to break the testing up, 
In this context I think unit tests should ideally remain sub 1 minute if the total tests cannot run in that time I would start to mark tests
smoke, core, soak but this would be driven by need with each bundle being a superset needed to merge to master. 

This gets more relevant with larger codebases and as you get more and more higher level tests integration and system tests for example.

## Decisions & Assumptions
* * *
- Language selection many languages could be used I am just going to start advantages and disadvantages of my selection
	### Advantages
	- Python has a mature and wide ranging module ecosystem
	- Python is very quick to iterate within
	- Python is easy to extend later
	- PyTest is listed as a desirable skill on the job spec so using it for both sides reduces number of things to install/setup
	### Disadvantages
	- Requires Python to be installed (Go, Rust, C would allow something more contained in a single compiled binary)
	- Python can be compiled with some tools however this would be outside the scope for this exercise
	- Python is slow, not sure this is an issue in this context
- click module is reasonably mature and implements some nice type checking on inputs by default so rather than use argparser and implement all of that myself used module.
- Security of the API Key was done by 
	- a) keeping it inside a file this way it is not recorded directly in console history
	- b) ensuring the value from the file is not used globally but kept reduced to the scope needed
	- Note: Some added security can be added to the file by ensuring only root has read access and giving the script an elevated privileges for execution
	`sudo python3 ipstack_interface.py -i 8.8.8.8` only do this with scripts you understand and trust.
	- Note: I could have immediately erased the variable holding the access key and the request composed from it after use however I think this would be the illusion of doing something useful if someone is able view memory for your applications your system is already significantly compromised and they are likely to see the file path and gain access to the key that way
- Assuming security comment in assignment is not related enable security module that can be added onto with the & security = 1 parameter as this requires a subscription plan 
- Following Unix Principles meant to me
	- use input arguments 
	- plain text output allows for piping and easy manipulation
	- standard flag practices -h, --help for help information etc
- I decided to avoid returning data in a JSON format for default return this can be useful in certain environments however if I am sticking strictly to a Unix toolset `sed` requires some frankly horrific regex to extract values from it `<json_data_text>| sed -E 's/.*"longitude":"?([^,"]*)"?.*/\1/'` and would potentially be very brittle. You can use a tool like jq to parse json easily included both output types anyway.  


## General Useful commands / Notes

Update requirements.txt after install new module
` python3 -m pip freeze > ./requirements.txt

Just to integrate it a bit better you could make the script executable
`chmod +x script_name.py`
and add to your profile, bashrc or zshrc
`alias ipstack="/<path>/ipstack_interface.py"`
Alternatively you could modify path
Alternatively alternatively could look at compiling and moving the binary to /bin