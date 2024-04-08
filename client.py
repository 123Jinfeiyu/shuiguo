import random
import socket
import time
import logging
# 设置日志格式
logging.basicConfig(filename='sender.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
# 定义服务器地址和端口号
SERVER_ADDRESS = "localhost"
PORT = 8888
#定义最大的传输窗口的大小
MAX_WINDOW_SIZE = 1024
#用于储存接收到的数据段的缓冲区
buffer_area = []
# 重传计时器
retransmission_timer = None
# 当前已确认接收的数据段的序号
acked_sequence_number = 0
# 数据段到达的处理函数
def handle_data_segment(data, sender_address):
    global acked_sequence_number, buffer, retransmission_timer

    sequence_number = len(buffer) + 1  # 给数据段分配序号

    buffer.append((sequence_number, data))  # 将数据段添加到缓冲区

    if sequence_number == acked_sequence_number + 1:  # 如果是下一个预期的数据段
        acked_sequence_number += 1

        with open('received_data.txt', 'a') as file:  # 将数据段按序写入文件
            file.write(data.decode('utf-8'))

        sock.sendto("ACK".encode(), sender_address)  # 发送 ACK 给发送方

        if retransmission_timer:  # 如果有正在运行的重传计时器，停止它
            retransmission_timer.cancel()

    else:
        start_retransmission_timer(sequence_number)  # 启动重传计时器
# 启动重传计时器的函数
def start_retransmission_timer(sequence_number):
    global retransmission_timer

    retransmission_timer = time.after(sequence_number * 0.5)  # 设置重传计时器的超时时间

    def on_timer_expired():
        sock.sendto(buffer[sequence_number - 1][1].encode(), buffer[sequence_number - 1][0])  # 重传数据段
        logger.info(f"重传数据段 {sequence_number}")

    retransmission_timer.add_callback(on_timer_expired)  # 注册计时器超时的回调函数

# 创建UDP套接字,主要逻辑传输
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 发送连接请求（SYN）
syn = "SYN"
sock.sendto(syn.encode(), (SERVER_ADDRESS, PORT))
logger.info("发送SYN给服务端")

# 等待确认（ACK）
ack, server_addr = sock.recvfrom(1024)
if ack.decode() == "ACK":
    logger.info("收到服务端的ACK信息")

#计数器统计丢包率
counter=0
# 数据传输
for i in range(5):
    # 随机生成丢包率
    PACKET_LOSS_PROBABILITY = random.uniform(0, 1)
    if random.random()>PACKET_LOSS_PROBABILITY:
        data=f"数据包{i}发送成功"
        if len(data.encode())<=MAX_WINDOW_SIZE:
             sock.sendto(data.encode(),server_addr)
             logger.info(f"发送数据包{i+1}给服务端")
        else:
             # 如果数据长度超过最大传输窗口大小，需要进行分割和发送data[i: j]这个j变量是可以进行调整的
             for part in [data[i:100] for i in range(0, len(data), MAX_WINDOW_SIZE)]:
                 sock.sendto(part.encode(), server_addr)
                 logger.info(f"发送数据包{i + 1}的部分数据给服务端")
    else:
        counter += 1
        logger.info(f"数据包丢包了")
    time.sleep(1)  # 模拟数据传输延迟
    logger.info(f'丢包率:{(counter / 5) * 100}%')
# 发送连接终止请求（FIN）
fin = "FIN"
sock.sendto(fin.encode(), server_addr)
logger.info("发送FIN段给服务端")

# 等待确认（ACK）
ack, addr = sock.recvfrom(1024)
if ack.decode() == "ACK":
    logger.info("收到服务端的ACK信息")
sock.close()