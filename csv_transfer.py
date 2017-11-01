#coding: utf-8

import json
class CSVnode():
    def __init__(self, pos, val):
        self.pos = pos
        self.val = val
        self.children = []
    
    def trasfer_to_json(self):
        if not self.children:
            return {self.val:[]}
        else:
            return {self.val:[child.trasfer_to_json() for child in self.children]}
    def __repr__(self):
        return "pos:"+str(self.pos)+"  children:"+str(self.children)

def csv_to_json():
    f = open('history.csv', 'r')
    lines = f.read().split('\r')
    levels = []
    new_lines = []
    for line in lines:
        items = line.decode('utf-8').split(',')
        new_lines.append(items)
    columns = zip(*new_lines)
    total_col_num = len(columns)
    for col_num, col in enumerate(columns):
        levels.append([CSVnode((row, col_num), val) for row, val in enumerate(col) if val])
    for i, col in enumerate(levels[:0:-1]):
        for node in col:
            row = node.pos[0]
            for fnode in levels[total_col_num-i-2][::-1]:
                if fnode.pos[0] <= row:
                    fnode.children.append(node)
                    break
    return json.dumps(levels[0][0].trasfer_to_json())

def find(keyword):
    csv_dict = json.loads(csv_to_json())
    tmp_path = []
    def find_in_dict(target, path):
        key = target.keys()[0]
        path.append(key)
        if keyword == key.encode('utf-8'):
            return path
        else:
            for child in target[key]:
                res_path = find_in_dict(child, path)
                if res_path:
                    return res_path
        path.pop()
    path = find_in_dict(csv_dict, tmp_path)

    if path:
        return '.'.join(path)
    else:
        return "不存在关键字：%s"%keyword
