import pika
import os
import json
import subprocess

#changes directory
def change_directory(directory):
    try:
        os.chdir(directory)
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

#lists directory
def list_directory():
    return {'files': os.listdir()}

#get file
def get_file(file_name):
    with open(f"{file_name}",'rb') as f:
        file_contents=f.read()
        return file_contents

#save uploaded file
def save_file(file_data,file_name):
    destination_path = os.path.basename(file_name)
    with open(destination_path, 'wb') as file:
        file.write(file_data)


#parses command, sends directory
def on_command_received(ch, method, properties, body):
    message = json.loads(body.decode())
    command = message['command']
    arg = message['arg']

    print(f" [x] Received command: {command} {arg}")

    if command == 'ls':
        data = list_directory()
      
    elif command == 'cd':
        directory = change_directory(arg)
        data = "new directory: " + str(directory)
    
    elif command == "get_file": 

        try:
            file_name = arg
            file_data = get_file(file_name).hex()
            data = {
            'filename': arg,
            'file_data': file_data # Convert binary data to a hex string for serialization
            }

            #different queue
            ch.basic_publish(exchange='', routing_key='file_retrieve_queue', body=json.dumps(data))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            return
        
        except:
             data = {'status': 'error', 'message': f"Not a valid file: {arg}"}
    
    elif command == "send_file":
            filename = arg
            file_data = bytes.fromhex(message['file_data'])  # Convert the hex string back to binary data
            save_file(file_data,filename)
            data = "successfully uploaded" + filename 

    else:
        #data = {'status': 'error', 'message': f"Unknown command: {command}"}
        command_to_execute = command + ' ' + arg
        result = subprocess.run(command_to_execute, capture_output=True, text=True, shell=True)

        if result.returncode == 0:
        # Clean the output by removing leading/trailing whitespaces and replacing multiple spaces with a single space
            #clean_output = '\n'.join(line.strip() for line in result.stdout.strip().split('\n'))
            data = result.stdout

        else:
            data = "failed to execute command"

        

    ch.basic_publish(exchange='', routing_key='data_queue', body=json.dumps(data))
    ch.basic_ack(delivery_tag=method.delivery_tag)


directory = os.getcwd()

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

#consume from queue
channel.queue_declare(queue='command_queue')
channel.basic_consume(queue='command_queue', on_message_callback=on_command_received)

print(' [*] Waiting for commands. To exit press CTRL+C')
channel.start_consuming()
