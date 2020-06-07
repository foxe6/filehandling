from filehandling import join_path
import os
from typing import Any


__ALL__ = ["create_tree", "create_cascade", "format_cascade", "browse_directory"]


def create_tree(root: str, files: list = None, key: Any = None) -> dict:
    if files is None and key is None:
        files = []
        for a, b, c in os.walk(root):
            for file in c:
                st_result = os.stat(join_path(a, file))
                files.append((
                    join_path(a, file).replace(root, "")[1:],
                    {k: getattr(st_result, k) for k in dir(st_result) if k.startswith('st_')}
                ))
        files = sorted(files, reverse=True)
        key = 0
    tree = {}
    for file in files:
        paths = file[key].split(os.path.sep)
        if len(paths) == 1:
            _dir = ""
            item = (paths[0], file)
        else:
            _dir = os.path.sep.join(paths[:-1])
            item = (paths[-1], file)
        if _dir not in tree:
            if _dir == "":
                tree[""] = []
            else:
                tree[_dir] = {"": []}
        if _dir == "":
            tree[_dir].append(item)
        else:
            tree[_dir][""].append(item)
    while any([os.path.sep in k for k, v in tree.items()]):
        for k, v in tree.copy().items():
            if os.path.sep in k:
                ks = k.split(os.path.sep)
                new_k = os.path.sep.join(ks[:-1])
                sub_k = ks[-1]
                if new_k not in tree:
                    tree[new_k] = {}
                tree[new_k][sub_k] = v
                tree.pop(k)
    return tree


def create_cascade(root: str, tree: dict) -> list:
    return [(0, root)] + dump_tree(tree)


def dump_tree(d: dict, depth: int = 1) -> list:
    d = sorted(d.copy().items(), key=lambda x: x[0])
    cascade = []
    for k, v in d:
        if k == "":
            v = sorted(v, key=lambda x: x[0])
            for _k, _v in v:
                cascade.append((depth, _k, _v))
            continue
        elif isinstance(v, dict):
            cascade.append((depth, k))
            cascade += dump_tree(v, depth + 1)
    return cascade


def format_cascade(cascade: list) -> str:
    formatted = ""
    for i, info in enumerate(cascade):
        indent = ""
        for j in range(1, info[0] + 1):
            if i+1 <= len(cascade) and j == info[0]:
                if i+1 == len(cascade):
                    head = "'"
                elif j > cascade[i+1][0]:
                    head = "'"
                else:
                    last = -1
                    for k in range(i+1, len(cascade)):
                        # print(i, k, j, cascade[k][0], " ", end="")
                        if cascade[k][0] == j:
                            last = k
                            break
                        elif cascade[k][0] < j:
                            break
                    # print(last)
                    if last > 0:
                        head = "|"
                    else:
                        head = "'"
                indent += head+"---"
                if j == info[0]:
                    indent += " "
            else:
                # if not (i-1+1 <= len(cascade) and j == info[0]) and \
                #         not (i-1+1 == len(cascade)) and \
                #         not (j > cascade[i-1+1][0]):
                last = -1
                for k in range(i, len(cascade)):
                    # print(i, k, j, cascade[k][0], " ", end="")
                    if cascade[k][0] == j:
                        last = k
                        break
                    elif cascade[k][0] < j:
                        break
                # print(last)
                if last > 0:
                    head = "|"
                else:
                    head = " "
                indent += head+"  "
        formatted += indent+info[1]+"\n"
    return formatted


def get_tree_info(tree: dict) -> dict:
    info = {"files": [], "folder": []}
    for k, v in tree.items():
        if k == "":
            for _v in v:
                info["files"].append({
                    "name": _v[0],
                    "st_atime": _v[1][1]["st_atime"],
                    "st_mtime": _v[1][1]["st_mtime"],
                    "st_ctime": _v[1][1]["st_ctime"],
                    "st_size": _v[1][1]["st_size"]
                })
        else:
            info["folder"].append(k)
    info["folder"] = sorted(info["folder"])
    return info


def format_tree(tree: dict) -> str:
    formatted = ""
    tree_info = get_tree_info(tree)
    for folder in tree_info["folder"]:
        formatted += folder+"\n"
    for file in tree_info["files"]:
        formatted += "{}{}{}{}{}\n".format(
            file["name"].ljust(50),
            (str(file["st_size"]//1024)+"kB").rjust(9)+" "*4+" "*4,
            str(int(file["st_mtime"])).ljust(20),
            str(int(file["st_ctime"])).ljust(20),
            str(int(file["st_atime"])).ljust(20)
        )
    return formatted


def browse_directory(root: str):
    previous_dir = ""
    current_dir = ""
    tree = create_tree(root)
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("{}{}{}{}{}".format(
            " "*23+"Name"+" "*23,
            " "*2+"Size"+" "*2+" "*2,
            " "*4+"Date Modified"+" "*3+" "*1,
            " "*4+"Date Created"+" "*3+" "*1,
            " "*4+"Date Accessed"+" "*3
        ))
        try:
            if current_dir == "..":
                if previous_dir == "":
                    current_dir = ""
                else:
                    current_dir = join_path(previous_dir, "..")
            else:
                current_dir = join_path(previous_dir, current_dir)
            if current_dir == ".":
                current_dir = ""
            if current_dir == "":
                print(format_tree(tree))
            else:
                dirs = current_dir.split(os.path.sep)
                cur_tree = tree.copy()
                for _dir in dirs:
                    cur_tree = cur_tree[_dir]
                print(format_tree(cur_tree))
        except KeyError as e:
            current_dir = previous_dir
            previous_dir = ""
            continue
        except Exception as e:
            raise e
        print()
        print()
        previous_dir = current_dir
        current_dir = input("Input sub-directory: ")



