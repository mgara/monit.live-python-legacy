import json

from django.conf import settings

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


monit_update_period = getattr(settings, 'MONIT_UPDATE_PERIOD', 60)
maximum_store_days = getattr(settings, 'MAXIMUM_STORE_DAYS', 7)





def get_string(xmldoc, element, default=None):
    elements = element.split(".")
    for el in elements:
        try:
            xmldoc = xmldoc.getElementsByTagName(el)[0]
        except:
            return default
    value = xmldoc.childNodes[0].nodeValue
    return value


def get_int(xmldoc, element, default=None):
    ret = get_string(xmldoc, element, default)
    if ret:
        return int(ret)
    return ret


def get_value(xmldoc, parent_element="", child_element="", attribute=""):
    try:
        if parent_element == "" and attribute == "":
            element = xmldoc.childNodes[0]
        elif parent_element == "":
            element = xmldoc
        elif child_element == "":
            # first index, because there could be multiple Elements with that tag, second index because there could be multiple childNodes
            element = xmldoc.getElementsByTagName(parent_element)[0].childNodes[0]
        else:
            element = xmldoc.getElementsByTagName(parent_element)[0].getElementsByTagName(child_element)[0].childNodes[
                0]
        if attribute == "":
            return element.nodeValue
        else:
            return element.attributes[attribute].value
    except:
        # monit sometimes does not pass cpu/memory info (e.g. if it sends event messages), so we have to filter it
        return "none"


def json_list_append(json_list, value):
    try:
        new_list = json.loads(json_list)
        new_list.append(value)
    except:
        new_list = [value]
    # maximum allowed table size, if monit reports every monite, this stores data for one week
    maximum_table_length = int(maximum_store_days * 24. * 60. * 60. / monit_update_period)
    # just remove the first one, should be better in future
    if len(new_list) > maximum_table_length:
        new_list = new_list[-int(maximum_table_length):]
    return json.dumps(new_list)


def remove_old_services(server, service_list):
    if server.system.name not in service_list:
        server.system.delete()
    processes = server.process_set.all()
    for process in processes:
        if process.name not in service_list:
            process.delete()


"""
from the monit source code (monit/contrib/wap.php):
//For conversion of status codes to text
$event[0] = 'OK';
$event[1] = 'Checksum failed';
$event[2] = 'Resource limit matched';
$event[4] = 'Timeout';
$event[8] = 'Timestamp failed';
$event[16] = 'Size failed';
$event[32] = 'Connection failed';
$event[64] = 'Permission failed';
$event[128] = 'UID failed';
$event[256] = 'GID failed';
$event[512] = 'Does not exist';
$event[1024] = 'Invalid type';
$event[2048] = 'Data access error';
$event[4096] = 'Execution failed';
$event[8192] = 'Changed';
$event[16384] = 'ICMP failed';
$monitored[0] = 'No';
$monitored[1] = 'Yes';
$monitored[2] = 'Init';
"""


def decode_status(status, type=0):
    errors_messages = ['Ok', 'Checksum failed', 'Resource limit matched', 'Timeout', 'Timestamp failed', 'Size failed',
                       'Connection failed', 'Permission failed', 'UID failed', 'GID failed', 'Does not exist',
                       'Invalid type', 'Data access error', 'Execution failed', 'Changed', 'ICMP failed']
    # choice_monitor = ['No', 'Yes', 'Init']
    # format to a bitarray
    bits = '{0:015b}'.format(status)
    out_str = ''
    ok = True
    for i in range(len(bits)):
        if bits[i] == "1":
            if not ok:
                out_str += ", "
            out_str += errors_messages[-i - 1]
            ok = False
    if ok:
        return "running"
    return out_str
