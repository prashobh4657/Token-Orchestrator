from flask import Flask,request,jsonify
import time
import threading
import random
from datetime import datetime

app=Flask(__name__)

MAX_KEYS=100
keys={}
blocked_keys=set()
keep_alive_internal=2*60
# keep_alive_internal=60 #Just for testing purpose
block_release_time=60
next_key_id=1

def format_time(epoch_time):
    if epoch_time is None:
        return None
    return datetime.fromtimestamp(epoch_time).strftime('%H:%M:%S')

def remove_expired_keys():
    while True:
        time.sleep(1)
        current_time=time.time()
        #Remove expired keys
        expired_keys=[key for key,info in keys.items() if info['expiry'] and current_time>info['expiry']]
        for key in expired_keys:
            del keys[key]

def release_blocked_keys():
    while True:
        time.sleep(1)
        current_time=time.time()
        #Release blocked keys after 60 seconds
        to_unblock=[key for key in blocked_keys if current_time>keys[key]['blocked_at']+block_release_time]
        for key in to_unblock:
            keys[key]['blocked']=False
            keys[key]['blocked_at']=None
            blocked_keys.remove(key)
threading.Thread(target=remove_expired_keys,daemon=True).start()
threading.Thread(target=release_blocked_keys,daemon=True).start()


@app.route('/keys',methods=['POST']) 
def create_key():
    global next_key_id
    if len(keys)>=MAX_KEYS:
        return jsonify({'error' : 'Maximum no. of keys reached'}),400
    new_key=f"key{next_key_id}"
    keys[new_key]={
        'expiry':time.time()+keep_alive_internal,
        'blocked':False,
        'blocked_at':None,
        'created_at':time.time()
    }
    next_key_id+=1
    return jsonify({'message' : 'Key created'}),201


@app.route('/keys',methods=['GET'])
def retrieve_key(): 
    available_keys=[key for key, info in keys.items() if not info['blocked'] and info['expiry']]
    if not available_keys:
        return jsonify({'error':'No available keys'}),404
    
    selected_key=random.choice(available_keys)
    keys[selected_key]['blocked']=True
    keys[selected_key]['blocked_at']=time.time()
    blocked_keys.add(selected_key)
    return jsonify({'key' : selected_key}),200

@app.route('/keys/<key>',methods=['GET'])
def get_key_info(key):
    if key in keys:
        info = keys[key]
        return jsonify({
            'isBlocked' : info['blocked'],
            'blockedAt' : format_time(info['blocked_at']),
            'createdAt' : format_time(info['created_at']),
            'expiry':format_time(info['expiry'])
        })
    else:
        return jsonify({'error' : 'key not found'}),404

  
@app.route('/keys/<key>',methods=['DELETE'])
def remove_key(key):
    if key in keys:
        del keys[key]
        if key in blocked_keys:
            blocked_keys.remove(key)
        return jsonify({'message':'Key removed'})
    else:
        return jsonify({'error' : 'key not found'}),404
    

@app.route('/keys/<key>',methods=['PUT'])
def unblock(key):
    if key in keys and keys[key]['blocked']:
        keys[key]['blocked']=False
        keys[key]['blocked_at']=None
        blocked_keys.remove(key)
        return jsonify({'message':'Key unblocked'})
    else:
        return jsonify({'error' : 'Key not found or not blocked'}),404
    
@app.route('/keepalive/<key>',methods=['PUT'])
def keep_alive(key):
    if key in keys and keys[key]['expiry']:
        keys[key]['expiry']=time.time()+keep_alive_internal
        return jsonify({'message':'Key-alive signal received'})
    else:
        return jsonify({'error' : 'Key not found'}),404
    

# Testing purpose
@app.route('/all_keys',methods=['GET']) 
def get_all_keys():
    return jsonify({'info' : keys}),200


if __name__ == '__main__':
    app.run(debug=True)