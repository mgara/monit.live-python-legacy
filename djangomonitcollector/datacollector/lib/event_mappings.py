

def type_to_string(type):
    array_type = [
        "FileSystem",
        "Directory",
        "File",
        "Process",
        "Remote Host",
        "System",
        "Fifo",
        "Program",
        "Network"
    ]
    return array_type[int(type)]


def event_status_to_string(status):
    status_int = int(status)
    state_dic = {
        1: 'checksum',
        2: 'resource',
        4: 'timeout',
        8: 'timestamp',
        16: 'size',
        32: 'connection',
        64: 'permission',
        128: 'UID',
        256: 'GID',
        512: 'nonexist',
        1024: 'invalid',
        2048: 'data',
        4096: 'exec',
        8192: 'fsflags',
        16384: 'icmp',
        32768: 'content',
        65536: 'instance',
        131072: 'action',
        262144: 'PID',
        524288: 'PPID',
        1048576: 'heartbeat',
        16777216: 'link mode/speed',
        2097152: 'status',
        4194304: 'uptime'
    }

    try:
        return state_dic[status_int]
    except:
        return status_int


def event_state_to_string(state):
    state_int = int(state)
    state_dic = {
        0: 'Sucess',
        1: 'Error',
        2: 'Change',
        3: 'Link mode not changed',
        4: 'Host Down',
    }
    return state_dic[state_int]


def action_to_string(action):
    action_int = int(action)
    action_dict = {
        1: 'Alert',
        2: 'Restart',
        3: 'Stop',
        4: 'Exec',
        5: 'Unmonitor',
        6: 'Reload',
    }
    return action_dict[action_int]


EVENT_ACTION_CHOICES = (
    (1, 'Alert'),
    (2, 'Restart'),
    (3, 'Stop'),
    (4, 'Exec'),
    (5, 'Unmonitor'),
    (6, 'Reload')
)

EVENT_STATE_CHOICES = (
    (0, 'Sucess'),
    (1, 'Error'),
    (2, 'Change'),
    (3, 'Link mode not changed'),
    (4, 'Host Down'),
)

EVENT_ID_CHOICES = (
    (1, 'checksum'),
    (2, 'resource'),
    (4, 'timeout'),
    (8, 'timestamp'),
    (16, 'size'),
    (32, 'connection'),
    (64, 'permission'),
    (128, 'UID'),
    (256, 'GID'),
    (512, 'nonexist'),
    (1024, 'invalid'),
    (2048, 'data'),
    (4096, 'exec'),
    (8192, 'fsflags'),
    (16384, 'icmp'),
    (32768, 'content'),
    (65536, 'instance'),
    (131072, 'action'),
    (262144, 'PID'),
    (524288, 'PPID'),
    (1048576, 'heartbeat'),
    (16777216, 'link mode/speed'),
    (2097152, 'status'),
    (4194304, 'uptime')
)

EVENT_TYPE_CHOICES = (
    (0, 'FileSystem'),
    (1, 'Directory'),
    (2, 'File'),
    (3, 'Process'),
    (4, 'Remote Host'),
    (5, 'System'),
    (6, 'Fifo'),
    (7, 'Program'),
    (8, 'Network'),
)
