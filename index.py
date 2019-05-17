from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import pprint
pp = pprint.PrettyPrinter()

conn = BigchainDB('https://test.bigchaindb.com')
#conn = new Mongo()

def create_transaction(prepared_transfer_tx, private_key):
    _id = prepared_transfer_tx['inputs'][0]['fulfills']['transaction_id']
    block_height = conn.blocks.get(txid=_id) #If it is None it can have different reasons for example the transaction was not valid or is still in the queue and you can try again later.
    block = conn.blocks.retrieve(str(block_height))
    authorized = block['transactions'][0]['asset']['data']['canLink']

    if authorized is None or (prepared_transfer_tx['outputs'][0]['public_keys'][0] in authorized):
        print('can transfer')
        return conn.transactions.fulfill(
            prepared_transfer_tx,
            private_keys=private_key,
        )
    else:
        raise Exception('Unauthorized! Transfer not made')

def assign_transaction(responsible):
    metadata = {'status': 'in process'}
    #transfer
    prepared_transfer_tx = conn.transactions.prepare(
         operation='TRANSFER',
         asset=transfer_asset,
         inputs=transfer_input,
         recipients=responsible.public_key,
         metadata=metadata
    )
    return prepared_transfer_tx

def close_transaction(responsible):
    metadata = {'status': 'closed'}
    #transfer
    prepared_transfer_tx = conn.transactions.prepare(
         operation='TRANSFER',
         asset=transfer_asset,
         inputs=transfer_input,
         recipients=responsible.public_key,
         metadata=metadata
    )
    return prepared_transfer_tx

def create_new(data):
    complaint = {
        'data': data,
    }

    metadata = {'status': 'initial'}

    prepared_creation_tx = conn.transactions.prepare(
         operation='CREATE',
         signers=alice.public_key,
         asset=complaint,
         metadata=metadata,
     )


    fulfilled_creation_tx = conn.transactions.fulfill(
        prepared_creation_tx,
        private_keys=alice.private_key
     )


    sent_creation_tx = conn.transactions.send_commit(fulfilled_creation_tx)

    return sent_creation_tx, fulfilled_creation_tx

#start here
alice, director, hr, police = generate_keypair(), generate_keypair(), generate_keypair(), generate_keypair()
print(alice, director, hr, police)

data = {'denounced': 'Bob Smith',
    'summary': 'Bob harrased me',
    'canLink':[director.public_key,hr.public_key, police.public_key]}

sent_creation_tx, fulfilled_creation_tx = create_new(data)
# print(sent_creation_tx == fulfilled_creation_tx)


transfer_asset = {
     'id': fulfilled_creation_tx['id'],
 }
output_index = 0
output = sent_creation_tx['outputs'][output_index]

transfer_input = {
    'fulfillment': output['condition']['details'],
    'fulfills': {
         'output_index': output_index,
         'transaction_id': fulfilled_creation_tx['id'],
     },
     'owners_before': output['public_keys'],
  }

prepared_transfer_tx = assign_transaction(director)
fulfilled_transfer_tx = create_transaction(prepared_transfer_tx, alice.private_key)


pp.pprint(fulfilled_transfer_tx)

sent_transfer_tx = conn.transactions.send_commit(fulfilled_transfer_tx)

print(sent_transfer_tx == fulfilled_transfer_tx)

print("Is The director the owner?",fulfilled_transfer_tx['outputs'][0]['public_keys'][0] == director.public_key)
print("Was Alice the previous owner?",fulfilled_transfer_tx['inputs'][0]['owners_before'][0] == alice.public_key)


#close transaction
close_transaction_tx = close_transaction(director)
