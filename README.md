# PPP Logging backend

[![Build Status](https://scrutinizer-ci.com/g/ProjetPP/PPP-Logger/badges/build.png?b=master)](https://scrutinizer-ci.com/g/ProjetPP/PPP-Logger/build-status/master)
[![Code Coverage](https://scrutinizer-ci.com/g/ProjetPP/PPP-Logger/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/ProjetPP/PPP-Logger/?branch=master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ProjetPP/PPP-Logger/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ProjetPP/PPP-Logger/?branch=master)


# How to install

With a recent version of pip:

```
pip3 install git+https://github.com/ProjetPP/PPP-logger.git
```

With an older one:

```
git clone https://github.com/ProjetPP/PPP-Logger.git
cd PPP-Logger
python3 setup.py install
```

Use the `--user` option if you want to install it only for the current user.

# How to run the logger (for system administrators)

You can write your `config.json` file in a quite straightforward way, using
the file `example_config.json` as an example.

Then, just run:

```
PPP_LOGGER_CONFIG=/path/to/json/config.json gunicorn ppp_logger:app
```

# How to use the logger API (for frontend developpers)

Just send a POST request to your logger instance, with this content:

```
{"id": "<request id>", "question": "<the question the user wrote>",
"responses": [list of responses returned by the core]}
```
