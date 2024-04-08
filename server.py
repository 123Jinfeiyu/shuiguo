import random
import socket
import time
import logging

# 设置日志格式
logging.basicConfig(filename='receiver.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# 定义端口号
PORT = 8888

# 创建 UDP 套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("localhost", PORT))

logger.info("STP 服务正在运行")

# 用于存储接收到的数据段的缓冲区
buffer = []

# 当前已确认接收的数据段的序号
acked_sequence_number = 0

# 重传计时器
retransmission_timer = None

# 处理数据段无序到达的情况
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

# 主程序逻辑
while True:
    syn, client_addr = sock.recvfrom(1024)  # 接收数据和客户端地址
    if syn.decode() == "SYN":
        logger.info("收到客户端的 ACK 信息")
        # break

    # 发送确认信息
    ack = "ACK"
    sock.sendto(ack.encode(), client_addr)
    logger.info("发送 ACK 段给 client")

    # 开始数据传输
    while True:
        data, addr = sock.recvfrom(1024)
        logger.info(f"收到{addr}:{data.decode()}")

        # 模拟随机丢包
        if random.random() < 0.3:
            logger.info(f"数据包丢失")
            time.sleep(2)
        else:
            handle_data_segment(data, addr)  # 处理数据段

    # 关闭连接
    fin, addr = sock.recvfrom(1024)
    if fin.decode() == "FIN":
        logger.info("从客户端收 FIN 段")

    # 发送确认
    ack = "ACK"
    sock.sendto(ack.encode(), addr)
    logger.info("发送确认字段给客户端")
    sock.close()