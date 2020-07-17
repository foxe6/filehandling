import queue
import traceback
import threading
from .path import *
from encryptedsocket import SC as ESC, SS as ESS
from unencryptedsocket import SC as USC, SS as USS
from easyrsa import *
from omnitools import str_or_bytes, utf8d, charenc, p, args, key_pair_format


__ALL__ = ["file_size", "read", "write", "Writer"]


def file_size(path: str) -> int:
    if os.path.isdir(path):
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    elif os.path.isfile(path):
        return os.path.getsize(path)
    else:
        raise


def read(file_path: str, encoding: str = None, depth: int = 2) -> str_or_bytes:
    if not os.path.isabs(file_path):
        file_path = join_path(abs_main_dir(depth=int(depth)), file_path)
    if encoding:
        try:
            return open(file_path, "rb").read().decode(encoding=encoding)
        except UnicodeDecodeError:
            raise Exception(f"failed to readfile {file_path} with encoding {encoding}.")
    else:
        content = open(file_path, "rb").read()
        try:
            return utf8d(content)
        except UnicodeDecodeError:
            try:
                return content.decode(encoding=charenc(content))
            except UnicodeDecodeError:
                return content


class Writer(object):
    def worker(self) -> None:
        while not self.terminate:
            file_path, mode, content = self.fileq.get()
            if not os.path.isfile(file_path):
                try:
                    os.makedirs(os.path.dirname(file_path))
                except:
                    pass
                try:
                    open(file_path, "ab").close()
                except:
                    pass
            try:
                open(file_path, mode).write(content)
            except Exception as e:
                what = content
                p(f"cannot write {what} to file {file_path} using mode {mode} due to {e}")
                traceback.print_exc()
            self.fileq.task_done()

    def stop(self) -> None:
        self.terminate = True

    def __init__(self, server: bool = False) -> None:
        self.terminate = False
        self.fileq = None
        self.fileq_worker = None
        self.functions = None
        self.is_server = server
        self.sc = None
        if self.is_server:
            self.fileq = queue.Queue()
            self.fileq_worker = threading.Thread(target=self.worker)
            self.fileq_worker.daemon = True
            self.fileq_worker.start()
            self.functions = dict(write=self.fileq.put)

    def write(self, file_path: str, mode: str, content: str_or_bytes, depth: int = 2) -> bool:
        if not os.path.isabs(file_path):
            file_path = join_path(abs_main_dir(depth=int(depth)), file_path)
        if mode not in ("w", "a", "wb", "ab"):
            raise Exception(f"mode {mode} is not 'w' or 'a' or 'wb' or 'ab'.")
        if mode in ("w", "a") and isinstance(content, bytes):
            raise Exception(f"mode {mode} cannot write bytes")
        if mode in ("wb", "ab") and isinstance(content, str):
            raise Exception(f"mode {mode} cannot write str")
        _args = (file_path, mode, content)
        if self.is_server:
            self.fileq.put(_args)
        else:
            try:
                self.sc.request(command="write", data=args(_args))
            except ConnectionRefusedError:
                open(file_path, mode).write(content)
        return True


class WriterE(Writer):
    def __init__(self, server: bool = False, key_pair: key_pair_format = None) -> None:
        super().__init__(server)
        host = "127.199.71.10"
        port = 39293
        if self.is_server:
            if key_pair is None:
                key_pair = EasyRSA(bits=1024).gen_key_pair()
            self.ess = ESS(key_pair, self.functions, host, port)
            thread = threading.Thread(target=self.ess.start)
            thread.daemon = True
            thread.start()
        else:
            self.sc = ESC(host, port)

    def stop(self):
        super().stop()
        self.ess.stop()


class WriterU(Writer):
    def __init__(self, server: bool = False) -> None:
        super().__init__(server)
        host = "127.199.71.10"
        port = 39293
        if self.is_server:
            self.uss = USS(self.functions, host, port)
            thread = threading.Thread(target=self.uss.start)
            thread.daemon = True
            thread.start()
        else:
            self.sc = USC(host, port)

    def stop(self):
        super().stop()
        self.uss.stop()


