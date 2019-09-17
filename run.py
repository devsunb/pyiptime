import argparse
import logging

from iptime import IPTime

logger = logging.getLogger('IPTIME')


def get_option():
    parser = argparse.ArgumentParser(description='Interval copier')
    parser.add_argument('-o', '--host', type=str,
                        default='http://192.168.0.1/', help='ipTIME 접속 URL')
    parser.add_argument('-u', '--user', type=str, required=True, help='User')
    parser.add_argument('-p', '--password', type=str,
                        required=True, help='Password')
    parser.add_argument('-m', '--mac', type=str,
                        required=True, help='WOL 할 기기의 MAC 주소')
    parser.add_argument('-l', '--log-level', type=str,
                        default='INFO', help='Log level')
    return parser.parse_args()


def setup_logger(log_level):
    logger.setLevel(log_level.upper())
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


if __name__ == '__main__':
    option = get_option()
    setup_logger(option.log_level)
    i = IPTime(option.host)
    i.login(option.user, option.password)
    wol_list = i.list_wol()
    i.wake(option.mac)
