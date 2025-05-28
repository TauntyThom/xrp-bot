#!/bin/bash
gunicorn -w 1 -b 0.0.0.0:$PORT xrp_bot_webhook:app
