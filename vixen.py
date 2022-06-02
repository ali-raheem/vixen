import sqlite3
import json
import secp256k1
import re
from flask import Flask
from flask import request as flask_request
from flask_cors import CORS
from dataclasses import dataclass
from dataclasses import asdict
from datetime import datetime
from hashlib import sha256

app = Flask(__name__)
CORS(app)

@dataclass
class Result:
    ok: bool
    message: str
    error_code: int

@dataclass
class Post:
    vid: int
    timestamp: str
    content: str
    address: str
    signature: str
    replyto: str
    proof : str

class DB:
    """
    Class to manage the SQLite3 database
    (id integer primary key, timestamp text, content text, address text, signature text, proof text)
    """
    con = None
    cur = None
    def __init__(self, path):
        self.con = sqlite3.connect(path, check_same_thread=False)
        self.cur = self.con.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS posts
    (id INTEGER, timestamp text, content text, address text, signature text, replyto text, proof text, UNIQUE(proof))''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS user (address text, signature text, following text, UNIQUE(address))''')
        self.commit()
    def getPostsByAddr(self, addr, limit = 10, offset = 0):
        db.cur.execute('''SELECT * FROM posts WHERE address = ? ORDER BY id LIMIT ? OFFSET ?''', (addr, limit, offset))
        return [Post(*x) for x in db.cur]
    def getPostByProof(self, proof):
        db.cur.execute('''SELECT * FROM posts WHERE proof = ?''', (proof,))
        return [Post(*x) for x in db.cur][0]
    def insertPost(self, msg, sig, addr, proof, replyto):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = msg[:255]
        self.cur.execute('''INSERT INTO posts VALUES (NULL, ?, ?, ?, ?, ?, ?)''', (timestamp, msg, addr, sig, replyto, proof))
        self.commit()
    def getRepliesByProof(self, proof, limit = 10, offset = 0):
        db.cur.execute('''SELECT * FROM posts WHERE replyto = ? ORDER BY id LIMIT ? OFFSET ?''', (proof, limit, offset))
        return [Post(*x) for x in db.cur]
    def checkNewProof(self, proof):
        db.cur.execute('''SELECT COUNT(*) FROM posts WHERE proof = ?''', (proof,))
        used = db.cur.fetchone()[0]
        return used == 0
    def commit(self):
        self.con.commit()

def checkSig(msg, pow, sig, addr):
    try:
        address = bytes(bytearray.fromhex(addr))
        pubkey = secp256k1.PublicKey(address, raw=True)
        signature = bytes(bytearray.fromhex(sig))
        signature = pubkey.ecdsa_deserialize(signature)
        message = f'{{"message": "{msg}", "nonce": "{pow}"}}'.encode(encoding='ASCII')
        print("Check sig on", message)
        return pubkey.ecdsa_verify(message, signature)
    except Exception as e:
        print('checkSig Exception', e)
        return False

def dataclassToJson(obj):
    return json.dumps(asdict(obj))

def checkHashCash(proof):
#    if not db.checkNewProof(proof):
#        return Result(False, "Proof of Work reused", 0)
    if re.fullmatch("\d{10}-\d{10}-\d{10}", proof) == None:
        return Result(False, "Proof of Work incorrecly formatted", 0)
    try:
        timestamp = int(proof.split('-')[0])
        hashcash = proof.encode(encoding='ASCII')
        nowts = int(datetime.now().timestamp())
        if abs(nowts - timestamp) > 10:
            print(nowts, timestamp)
            return Result(False, "Proof of Work stale", 0)
        hashed = sha256(hashcash).hexdigest()
        powcost = len(hashed) - len(hashed.lstrip('0'))
        if powcost < 4:
            return Result(False, "Proof of Work insufficient", 0)
        return Result(True, "Good proof of work", 0)
    except Exception as e:
        return Result(False, e, 0)

@app.route("/")
def homepage():
    return "backend server"

@app.route("/post", methods = ['POST'])
@app.route("/p", methods = ['POST'])
def postVix():
    try:
        hashcash = flask_request.headers.get('X-hashcash')
        powResult = checkHashCash(hashcash)
        if not powResult.ok:
            return dataclassToJson(powResult)
    except Exception as e:
        print(e)
        return dataclassToJson(Result(False, "Hashcash header failed. ", 0))
    req = flask_request.json
    if checkSig(req['message'], hashcash, req['signature'], req['address']):
        # Make post
        db.insertPost(req['message'], req['signature'], req['address'], hashcash, req['replyto'])
        return dataclassToJson(Result(True, "OK", 0))
    else:
        # Error
        return dataclassToJson(Result(False, "Signature check failed", 0))

@app.route("/post/<proof>")
@app.route("/p/<proof>")
def getPostByProof(proof):
    post = db.getPostByProof(proof)
    if post != None:
        return json.dumps(asdict(post))
    return ""

@app.route("/history/<addr>")
@app.route("/h/<addr>")
def getVixByAddr(addr):
    return json.dumps([asdict(x) for x in db.getPostsByAddr(addr)])

@app.route("/thread/<proof>")
@app.route("/t/<proof>")
def getThreadByProof(proof):
    return ""

@app.route("/replies/<proof>")
@app.route("/r/<proof>")
def getRepliesByProof(proof):
    return json.dumps([asdict(x) for x in db.getRepliesByProof(proof)])

if __name__ == '__main__':
    db = DB('./vixen.db')
    app.run(debug = True)
