# anyledger-backend
Backend for AnyLedger Hub

## How to use
`pip install -r requirements.txt`

`flask run` will automatically run server.py, listens on http://localhost:5000

Currently server.py has 2 endpoints:

`/data` IoT device should POST here with X-Anyledger-Sig HTTP header

`/sensors/`
`/sensors/<eth_address>` The frontend should GET here to get JSON data to display.

`signtest.py` Random scratchpad. Currently generates curl commands in post.sh.

`post.sh` used to quickly fill up the backend's database with mock data.