import asyncio
import websockets
import managedb
import json
import tools
from sys import platform

sockets = []
json_data = 'JSON data was not loaded...'


async def client_handler(client_socket, path):
    while True:
        msg = await client_socket.recv()
        if msg == 'datarequest':
            print('data was requested...')
            await client_socket.send(json.dumps(json_data, ensure_ascii=False))


if platform == "linux" or platform == "linux2":
    print('On linux host')
    init_server = websockets.serve(client_handler, '46.101.59.81', 4357)
else:
    print('On windows/mac host')
    init_server = websockets.serve(client_handler, 'localhost', 4357)

#init_server = websockets.serve(client_handler, 'localhost', 4357)

def start_server(conn):
    # Setup json data
    global json_data
    json_data = {}
    json_data["websites"] = managedb.get_specific_tuples(conn, '''
            SELECT destinationNAME,
            COUNT(destinationNAME) AS frequency FROM links GROUP BY destinationNAME ORDER BY frequency DESC''')

    json_data["links"] = managedb.get_specific_tuples(conn, '''SELECT originNAME, destinationNAME,
            COUNT(*) AS frequency FROM links GROUP BY originNAME, destinationNAME
            ORDER BY frequency DESC''')
    json_data["links"] = list(map(list, json_data["links"]))
    json_data["websites"] = list(map(list, json_data["websites"]))
    tools.print_array(json_data["links"])

    with open('data.json', 'w') as output_file:
        json.dump(json_data, output_file, ensure_ascii=False)


    # Start the server Async
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_server)
    loop.run_forever()

if __name__ == '__main__':
    conn = managedb.create_connection('database.db')
    managedb.create_tables(conn)
    start_server(conn)
    conn.close()
