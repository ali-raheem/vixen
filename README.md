# Vixen

Vixen is an experimental open source social media platform.

It is intended to be a standardized backend server with other parties implementing the frontend interface.

There are no accounts per se but anyone can submit signed messages which then are linked to the public key.

A hashcash like proof of work puzzle to deter spam, it also prevents message relay.

There is not option to edit or delete messages. Messages are authenticated on storing on the server however the signature and public key is also public so anyone can subsequently authenticate it.

Uses `secp256k1` curve with ECDSA (like bitcoin) for signing, and a proof of work based on hashcash (also not too disimilar from bitconi).

# Progress

## What's working
* Can submit messages which are authenticated by signature
* Can find last 10 messages of a user
* Can find messages that replied to a particular message
## Whats to do
* Allow people to submit signed "follower" lists to curate a page of other pubkeys they follow [priority]
* Partially working Angular front-end [here](https://github.com/ali-raheem/vixen-ng)
* Just in general improve actual checks on Proof of work, currently POW can be reused for gets until they time out.

### Screenshot
![Screenshot of vixen-ng](Screenshot.png)

# API

## Scheme

### Posts
* Message - A text string of up to 256 characters
* POW - A proof of work token made up of the Unix timestamp (+/-10 leeway), a nonce, and some junk data each left padded with 0s for a fixed 10 digits separated by hyphens e.g. 0987654321-0000000000-1111111111
* Address - The secp256k1 public key
* Signature - Signature of a JSON object (See below)
* Replyto - The signature of a message that was replied to
* Timestamp - Server reciept time stamp

### Signature

```
{"replyto": "", "message": "Hello, world!", "pow": "0987654321-0000000000-1111111111"}
```
* Replyto
* Message
* PoW

## /post (or /p)
### GET /post/<POW>
Returns a JSON object containing message assocaited with a particular proof of work
### POST /post/
Submit a new signed message

## GET /history/<address> (or /h/<address>)
Returns a JSON object array containing submitted posts of an address.
Will support LIMIT and OFFSET but currently limit to 10 and offset to 0

## GET /replties/<pow> (or /r/<pow>)
Returns a JSON object array containing replyto with the provided proof of work.

Will support LIMIT and OFFSET but currently limit to 10 and offset to 0

## Examples
Edit `post.sh` to contain your privkey and pubkey (can be generated with python secp256k1 module [see here](https://pypi.org/project/secp256k1/))
```
[ali@fedora Vixen]$./post.sh "Hi, from bash!" ""
curl -X POST localhost:5000/post -H "X-hashcash: 1654190562-0004025909-0000005733"  -H 'Content-Type: application/json' -d '{"message": "Hi, from bash!", "signature": "3044022056139af8e4e65296fd6619e399d33950685a34cf249d50a5dea02f10d2f4f00b022035ab62cf378abf0a76fc26a357b5ef876f14dc1f478707cd5af5157c29b0b19e", "address": "03bbaf3294e8eae159554a8b71476c1921e95954f5d8ef0c25362e88092dff3d4e", "replyto":  ""}'

{"ok": true, "message": "OK", "error_code": 0}

[ali@fedora Vixen]$./post.sh "This is a message replying to the last one" "3044022056139af8e4e65296fd6619e399d33950685a34cf249d50a5dea02f10d2f4f00b022035ab62cf378abf0a76fc26a357b5ef876f14dc1f478707cd5af5157c29b0b19e"

curl -X POST localhost:5000/post -H "X-hashcash: 1654190593-0002674477-0000015832"  -H 'Content-Type: application/json' -d '{"message": "This is a message replying to the last one", "signature": "304502210092e29529733dff321243f9de0268ad9b059590359f19ef7e2068cd54a7daa08602207853ca50c8faf27b30d93ddc6ecb7fec9b9564e5aff7a6180152cf5f644ef179", "address": "03bbaf3294e8eae159554a8b71476c1921e95954f5d8ef0c25362e88092dff3d4e", "replyto":  "3044022056139af8e4e65296fd6619e399d33950685a34cf249d50a5dea02f10d2f4f00b022035ab62cf378abf0a76fc26a357b5ef876f14dc1f478707cd5af5157c29b0b19e"}'
```

# Dependencies

* Python3
* Sqlite3
* [secp256k1](https://pypi.org/project/secp256k1/)
* [Flask](https://pypi.org/project/Flask/)
* [Flask-CORS](https://pypi.org/project/Flask-Cors/)