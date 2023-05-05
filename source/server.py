import json
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='command_queue')
channel.queue_declare(queue='data_queue')


def get_file(file_name):
    with open(f"{file_name}",'rb') as f:
        file_contents=f.read()
        return file_contents
    
while True:
    # Read command from user input
    command_input = input("Enter command (ls, cd <directory>, get_file <file>), send_file <file>: ")
    command_args = command_input.split()

    #skip empty input
    if not command_args:
        continue

    command = command_args[0]

    if command == 'cd':
        if len(command_args) < 2:
            print("Usage: cd <directory>")
            continue
        arg = command_args[1]
        message = json.dumps({'command': command, 'arg': arg})

    elif command == 'get_file':
        if len(command_args) < 2:
            print("Usage: get_file <file>")
            continue
        file_name = ' '.join(command_args[1:])
        #arg = ommand_args[1]
        print(file_name)
        arg=file_name
        message = json.dumps({'command': command, 'arg': arg})

      
    elif command == "send_file": 
        if len(command_args) < 2:
            print("Usage: send_file <file>")
            continue
        arg = command_args[1]
        try:
            file_name = arg
            file_data = get_file(file_name).hex()
            message = json.dumps({'command': command, 'arg': arg, 'file_data':file_data})

        except:
             data = {'status': 'error', 'message': f"Not a valid file: {arg}"}
             command="null"
             message=data

    elif command == 'ls':
        arg = ''
        message = json.dumps({'command': command, 'arg': arg})
    
    #execute arbitary command
    else:
        if len(command_args)<2:
             arg=""
        else:
            arg = ' '.join(command_args[1:])

        message = json.dumps({'command': command, 'arg': arg})
    

    # Send command to the command queue
    channel.basic_publish(exchange='', routing_key='command_queue', body=message)

    print(f" [x] Sent '{command} {arg}'")

connection.close()
