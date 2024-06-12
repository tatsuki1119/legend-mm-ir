import json
import os
import sys
from time import sleep

import smbus

# データ配置用ディレクトリ
DATA_DIR = "/home/tatsu/piz/flask/ir_data"


def json_to_dict(input_path: str) -> dict:
    """
    jsonを読み込みdict型で返す
    データディレクトリからのpath
    """
    with open(os.path.join(DATA_DIR, input_path), mode="rt", encoding="utf-8") as f:
        return json.load(f)


def dict_to_json(input_dict: dict, output_path: str) -> None:
    """
    dict型のものをjsonで保存する
    データディレクトリからのpath
    """
    with open(os.path.join(DATA_DIR, output_path), mode="wt", encoding="utf-8") as f:
        json.dump(input_dict, f, ensure_ascii=False, indent=4)
    return None


# IR関連設定
bus = smbus.SMBus(1)
SLAVE_ADDRESS = 0x5A
W1_data_num_write = 0x19
W2_data_write = 0x29
W3_trans_req = 0x39


# 信号データを取得
SIGNAL_DATA_DICT = json_to_dict("signal_data.json")


def send_signal(signal: str) -> None:
    """
    signalに16進で信号のデータを受け取り
    そのデータを赤外線で発信する
    ex.
    9000500015003000150015001500150015001500150015001500300015003000150030001500300015003000150030001500300015005000
    """

    str_tmp = ""
    int_tmp = []
    for i in range(int(len(signal) / 2)):
        str_tmp = signal[i * 2] + signal[i * 2 + 1]
        int_tmp.append(int(str_tmp, 16))
    data_num = int(len(int_tmp) / 4)
    data_numHL = [0x31, 0x32]
    data_numHL[0] = int(data_num / 256)
    data_numHL[1] = int(data_num % 256)
    bus.write_i2c_block_data(SLAVE_ADDRESS, W1_data_num_write, data_numHL)
    data_numHL = [0x31, 0x32, 0x33, 0x34]
    for i in range(data_num):
        data_numHL[0] = int_tmp[i * 4 + 0]
        data_numHL[1] = int_tmp[i * 4 + 1]
        data_numHL[2] = int_tmp[i * 4 + 2]
        data_numHL[3] = int_tmp[i * 4 + 3]
        bus.write_i2c_block_data(SLAVE_ADDRESS, W2_data_write, data_numHL)
    bus.write_byte(SLAVE_ADDRESS, W3_trans_req)


def main():
    status = json_to_dict("status.json")
    # s_mode = status["mode"]
    s_mode = "auto"
    s_pattern = status["pattern"]
    s_color = status["color"]
    loop_count = 0
    while 1:
        status = json_to_dict("status.json")
        if status["update"] == "1":  # 更新あったら
            s_mode = status["mode"]
            s_pattern = status["pattern"]
            s_color = status["color"]
            # 更新ステータス戻す
            status["update"] = "0"
            dict_to_json(status, "status.json")

        if s_color == "momo":
            if s_pattern == "fadein":
                s_pattern = "fixed"

        if s_mode == "auto":
            interval = 110
            loop_count = (loop_count % interval) + 1
            if loop_count <= 5:
                send_signal(SIGNAL_DATA_DICT.get("w-on"))
            elif loop_count <= 10:
                send_signal(SIGNAL_DATA_DICT.get("r-on"))
            elif loop_count <= 15:
                send_signal(SIGNAL_DATA_DICT.get("g-on"))
            elif loop_count <= 20:
                send_signal(SIGNAL_DATA_DICT.get("b-on"))
            elif loop_count <= 25:
                send_signal(SIGNAL_DATA_DICT.get("c-on"))
            elif loop_count <= 30:
                send_signal(SIGNAL_DATA_DICT.get("m-on"))
            elif loop_count <= 35:
                send_signal(SIGNAL_DATA_DICT.get("y-on"))
            elif loop_count <= 40:
                send_signal(SIGNAL_DATA_DICT.get("momo-on"))
            elif loop_count <= 50:
                send_signal(SIGNAL_DATA_DICT.get("w-fadein"))
            elif loop_count <= 60:
                send_signal(SIGNAL_DATA_DICT.get("r-fadein"))
            elif loop_count <= 70:
                send_signal(SIGNAL_DATA_DICT.get("g-fadein"))
            elif loop_count <= 80:
                send_signal(SIGNAL_DATA_DICT.get("b-fadein"))
            elif loop_count <= 90:
                send_signal(SIGNAL_DATA_DICT.get("c-fadein"))
            elif loop_count <= 100:
                send_signal(SIGNAL_DATA_DICT.get("m-fadein"))
            elif loop_count <= 110:
                send_signal(SIGNAL_DATA_DICT.get("y-fadein"))
            else:
                send_signal(SIGNAL_DATA_DICT.get("momo-on"))
            sleep(0.2)
            continue
        elif s_mode == "custom":
            if s_pattern == "fixed":
                send_signal(SIGNAL_DATA_DICT.get(f"{s_color}-on"))
                sleep(0.2)
                continue
            if s_pattern == "blink1":
                interval = 15
                loop_count = (loop_count % interval) + 1
                if loop_count <= 5:
                    send_signal(SIGNAL_DATA_DICT.get("off"))
                else:
                    send_signal(SIGNAL_DATA_DICT.get(f"{s_color}-on"))
                sleep(0.2)
                continue
            if s_pattern == "blink2":
                interval = 5
                loop_count = (loop_count % interval) + 1
                if loop_count <= 2:
                    send_signal(SIGNAL_DATA_DICT.get("off"))
                else:
                    send_signal(SIGNAL_DATA_DICT.get(f"{s_color}-on"))
                sleep(0.2)
                continue
            if s_pattern == "blink3":
                interval = 2
                loop_count = (loop_count % interval) + 1
                if loop_count == 1:
                    send_signal(SIGNAL_DATA_DICT.get("off"))
                else:
                    send_signal(SIGNAL_DATA_DICT.get(f"{s_color}-on"))
                sleep(0.05)
                continue
            if s_pattern == "fadein":
                interval = 30
                loop_count = (loop_count % interval) + 1
                if loop_count == 1:
                    send_signal(SIGNAL_DATA_DICT.get("off"))
                else:
                    send_signal(SIGNAL_DATA_DICT.get(f"{s_color}-fadein"))
                sleep(0.2)
                continue
            if s_pattern == "flash":
                interval = 8
                loop_count = (loop_count % interval) + 1
                if loop_count == 1:
                    send_signal(SIGNAL_DATA_DICT.get(f"{s_color}-on"))
                    sleep(0.05)
                    send_signal(SIGNAL_DATA_DICT.get("off"))
                    sleep(0.05)
                    send_signal(SIGNAL_DATA_DICT.get(f"{s_color}-on"))
                    sleep(0.05)
                    send_signal(SIGNAL_DATA_DICT.get("off"))
                else:
                    send_signal(SIGNAL_DATA_DICT.get("off"))
                sleep(0.2)
                continue
            if s_pattern == "rainbow":
                interval = 6
                loop_count = (loop_count % interval) + 1
                rainbow_list = ["r", "m", "b", "c", "g", "y"]
                send_signal(SIGNAL_DATA_DICT.get(f"{rainbow_list[loop_count - 1]}-on"))
                sleep(0.1)
            if s_pattern == "gj":
                interval = 32
                loop_count = (loop_count % interval) + 1
                on_count_list = [1, 3, 5, 9, 11, 13, 17, 19, 21, 23, 25, 27, 29]
                if loop_count in on_count_list:
                    send_signal(SIGNAL_DATA_DICT.get(f"{s_color}-on"))
                else:
                    send_signal(SIGNAL_DATA_DICT.get("off"))
                sleep(0.12)
            if s_pattern == "ds":
                interval = 128
                loop_count = (loop_count % interval) + 1
                on_count_list = [
                    1,
                    9,
                    17,
                    19,
                    21,
                    29,
                    37,
                    39,
                    41,
                    49,
                    51,
                    53,
                    57,
                    59,
                    61,
                ]
                if loop_count in on_count_list:
                    send_signal(SIGNAL_DATA_DICT.get(f"{s_color}-on"))
                else:
                    send_signal(SIGNAL_DATA_DICT.get("off"))
                sleep(0.021)
        else:
            signal_val = "momo"
            send_signal(SIGNAL_DATA_DICT.get(signal_val))
            sleep(0.2)


if __name__ == "__main__":

    main()
