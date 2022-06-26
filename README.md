# Predictive Services Daily WIMS Feed
Data feed for National [Predictive Services](https://www.predictiveservices.nifc.gov/) program.

Cron lambda deployed to AWS US-West-2 via Serverless used to process and upload
daily WIMS output to the web.

## Setup
Before getting started in the code, we'll need to set up a few dependencies.

### Git and Github
[Github](https://github.com/) is where the code is hosted and `git` is used for
version control. Most computers have [git](https://git-scm.com/downloads) installed
but you'll need to set up a GitHub account to push any changes you make to the repository.
A great set of instructions for setting up this step is found at https://docs.github.com/en/get-started/quickstart/set-up-git.


### Node and Serverless
These dependencies are used for deploying our code and creating our AWS resources.
You don't need to do this step if you have no intention of ever deploying the code "live".

Install Node 16.15.0 LTS [via the node website](https://nodejs.org/en/). Once Node
is installed, run the following to install Serverless:
```bash
npm install -g serverless
```
*NOTE: THERE IS SOME CONFIGURATION REQUIRED WITH SERVERLESS AND AWS THAT IS BEYOND
THIS README. WHEN/IF THE CODE IS HANDED-OFF, I AM HAPPY TO ASSIST ANY AGENCY STAFF
IN GETTING THIS SETUP, ANYTIME*


### Pyenv and Poetry
Pyenv is used to manage our python versions while poetry is used to manage our
python dependencies.

To install `pyenv`, see https://github.com/pyenv/pyenv#installation. Make sure
to follow the instructions closely! After you've installed `pyenv`, use it to
install the python version required:
```bash
pyenv install 3.8.6
```

Now go ahead and install `poetry` (which is a lot easier):
```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

With `pyenv` and `poetry` installed on your computer, navigate into this repo and run:
```bash
pyenv local 3.8.6
poetry install
```
This will make sure we use the `pyenv` we just created and then install all
needed dependencies in a local environment.

Finally, we can ensure we activate our local environment and run our tests:
```bash
poetry shell
pytest
```

## Making code changes
work in progress

## Deploying
Assuming we've configured everything correctly for AWS/Serverless, it's as simple
as:

```
sls deploy
```
