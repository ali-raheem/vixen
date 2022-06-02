PRIVKEY=8a0a05ac2d958c36968f6b9b4e128ac5ead9c881039a4e7c4852c9eef9ea401a
PUBKEY=03bbaf3294e8eae159554a8b71476c1921e95954f5d8ef0c25362e88092dff3d4e
TEXT="$1"
REPLYTO="$2"
NONCE=`python gen_pow.py`
MESSAGE="{\"replyto\": \"$REPLYTO\", \"message\": \"$TEXT\", \"pow\": \"$NONCE\"}"
SIGNATURE=`python -m secp256k1 sign -k $PRIVKEY -m "$MESSAGE"`
JSON="{\"message\": \"$TEXT\", \"signature\": \"$SIGNATURE\", \"address\": \"$PUBKEY\", \"replyto\":  \"$REPLYTO\"}"
echo "curl -X POST localhost:5000/post -H \"X-hashcash: $NONCE\"  -H 'Content-Type: application/json' -d '$JSON'"
