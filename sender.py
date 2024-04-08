# -*- coding: utf-8 -*-
import random
import socket
import time
import sys
import logging

# 设置日志格式
logging.basicConfig(filename='sender.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


# 函数：发送连接请求（SYN）
def send_syn(sock, server_address, port):
    syn = "SYN"
    sock.sendto(syn.encode(), (server_address, port))
    logger.info("发送SYN给服务端")


# 函数：等待确认（ACK）
def receive_ack(sock):
    ack, server_addr = sock.recvfrom(1024)
    if ack.decode() == "ACK":
        logger.info("收到服务端的ACK信息")
        return True
    return False


# 函数：发送数据包
def send_data(sock, server_addr, data):
    sock.sendto(data.encode(), server_addr)
    logger.info(f"发送数据包给服务端: {data}")


# 函数：发送连接终止请求（FIN）
def send_fin(sock, server_addr):
    fin = "FIN"
    sock.sendto(fin.encode(), server_addr)
    logger.info("发送FIN段给服务端")


# 主函数
def main(sender_port, receiver_port, file_to_send, max_win, rto, flp, rlp):
    # 创建UDP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = "localhost"

    # 发送连接请求（SYN）
    send_syn(sock, server_address, receiver_port)

    # 等待确认（ACK）
    if not receive_ack(sock):
        logger.error("未收到服务端的ACK确认，连接失败")
        return

    # 读取文件内容
    with open(file_to_send, 'r') as file:
        data = file.read()

    # 数据传输
    counter = 0
    for i in range(0, len(data), max_win):
        window = data[i:i + max_win]
        for packet in window:
            # 随机生成丢包率
            packet_loss_probability = random.uniform(0, 1)
            if random.random() > packet_loss_probability:
                send_data(sock, (server_address, receiver_port), packet)
            else:
                counter += 1
                logger.info(f"数据包{i + 1}丢包了")
        time.sleep(1)  # 模拟数据传输延迟
    logger.info(f'丢包率{(counter / len(data)) * 100}%')

    # 发送连接终止请求（FIN）
    send_fin(sock, (server_address, receiver_port))

    # 等待确认（ACK）
    if not receive_ack(sock):
        logger.error("未收到服务端的ACK确认，终止连接失败")
    sock.close()


if __name__ == "__main__":
    # 提示用户输入参数
    sender_port = int(input("Enter sender port: "))
    receiver_port = int(input("Enter receiver port: "))
    file_to_send = input("Enter file to send: ")
    max_win = int(input("Enter max window size: "))
    rto = float(input("Enter RTO: "))
    flp = float(input("Enter packet loss probability (FLP): "))
    rlp = float(input("Enter duplicate ACK probability (RLP): "))

    # 调用主函数
    main(sender_port, receiver_port, file_to_send, max_win, rto, flp, rlp)

