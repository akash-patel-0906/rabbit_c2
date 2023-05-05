import pika
import json
import os

def save_file(file_data,file_name):
    destination_path = "downloads/"+os.path.basename(file_name)
    with open(destination_path, 'wb') as file:
        file.write(file_data)


#receive non-file data
def on_data_received(ch, method, properties, body):
    data = json.loads(body.decode())
    print(" [x] Received data:")
    print(data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

#receive file data
def on_file_received(ch, method, properties, body):
    print("Received file")
    message = json.loads(body)
    filename = message['filename']
    file_data = bytes.fromhex(message['file_data'])  # Convert the hex string back to binary data

    save_file(file_data,filename)

    ch.basic_ack(delivery_tag=method.delivery_tag)

#connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

#declare data (non-file) queue
channel.queue_declare(queue='data_queue')
channel.basic_consume(queue='data_queue', on_message_callback=on_data_received)

#declare file-retrieve queue
channel.queue_declare(queue='file_retrieve_queue')
channel.basic_consume(queue='file_retrieve_queue', on_message_callback=on_file_received)

print(' [*] Waiting for data. To exit press CTRL+C')
channel.start_consuming()
