import ssl
import socket
import pprint
import subprocess
import os
import tkinter as tk
from tkinter import messagebox
import functools
import time


def retry_on_exception_or_none(retries=3, delay=1):
    """
    함수 실행 중 예외가 발생하거나 None을 반환하면 최대 `retries`번 재시도하는 데코레이터.
    각 재시도는 `delay` 초 동안 대기 후 실행됨.

    :param retries: 최대 재시도 횟수 (기본값: 3)
    :param delay: 재시도 사이의 대기 시간 (기본값: 1초)
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < retries:
                try:
                    result = func(*args, **kwargs)
                    if result:
                        return result  # 정상적인 반환값이면 즉시 반환
                except Exception as e:
                    print(
                        f"Exception occurred: {e}. Retrying {attempts + 1}/{retries}..."
                    )
                attempts += 1
                if attempts < retries:
                    time.sleep(delay)
            return None  # 최종적으로 실패하면 None 반환

        return wrapper

    return decorator


@retry_on_exception_or_none(retries=3, delay=1)
def get_certificate(hostname: str = "10.10.10.34", port=443):
    cert_str = ssl.get_server_certificate((hostname, port))
    return cert_str


def add_certificate_to_windows(cert_path):
    cmd = f'certutil -f -addstore "Root" "{cert_path}"'
    subprocess.run(cmd, shell=True, check=True)
    print("Certificate added to Windows trusted store.")


def mkdir_in_windows(path: str):
    if not os.path.exists(path):
        os.mkdir(path)
    # 폴더 숨기기
    subprocess.run(f'attrib +h "{path}"', shell=True, check=True)
    print(f"Directory created in Windows: {path}")

    return True


def write_file_in_windows(path: str, content: str):
    mkdir_in_windows(path)
    pem_path = os.path.join(path, "SE.pem")
    # 있으면 삭제하고 다시 쓰기
    if os.path.exists(pem_path):
        os.remove(pem_path)
    with open(pem_path, "w") as file:
        file.write(content)
    print(f"File created in Windows: {pem_path}")
    return pem_path


def show_popup(mes: str = "SSL 설치 완료"):
    # 팝업창띄우기
    messagebox.showinfo("AITRICS SSL installer", mes)


if __name__ == "__main__":
    # init tkinter
    root = tk.Tk()
    root.withdraw()
    # 현재 User의 홈 디렉토리 경로를 가져온다.
    home_dir: str = os.path.expanduser("~")
    path: str = os.path.join(home_dir, "se_ssl")
    pem_str: str = get_certificate()
    if not pem_str:
        show_popup("SSL 설치 실패")
        exit()

    try:
        pem_path = write_file_in_windows(path, pem_str)
        add_certificate_to_windows(pem_path)
    except Exception as e:
        show_popup(f"SSL 설치 실패: {e}")
        exit()

    print("SUCCESS install SSL AITRICS")
    show_popup()
