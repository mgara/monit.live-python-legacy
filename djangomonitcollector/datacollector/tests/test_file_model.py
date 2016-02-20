from test_plus.test import TestCase
from xml.dom import minidom
from ..models import File
import factories
import factory

class TestFileModel(TestCase):

    def setUp(self):
        self.user = self.make_user()
        self.xmldoc = '''
<service name="syslogd">
    <type>3</type>
    <collected_sec>1455305848</collected_sec>
    <collected_usec>881612</collected_usec>
    <status>0</status>
    <status_hint>0</status_hint>
    <monitor>2</monitor>
    <monitormode>0</monitormode>
    <pendingaction>0</pendingaction>
</service>
'''.strip()

    def test_update_or_create(self):
        service = minidom.parseString(self.xmldoc)
        server = factory.RelatedFactory(factories.ServerFactory, 'server')
        f = File.update(None, server, service)

        self.assertTrue(f)
