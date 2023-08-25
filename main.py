from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from simplecache import SimpleCache
import logging

logger = logging.getLogger(__name__)

# Set up a cache that expires after 1 hour (3600 seconds)
cache = SimpleCache('cache.pkl', duration=2*3600)
class InvalidCacheException(Exception):
    pass

def increment_dummy(entry, extension):
    parts = entry.split(str(extension.preferences['dummymail_ext']))
    if not len(parts) > 1:
        raise InvalidCacheException()
    counter_and_domain = parts[1].split('@');
    if not len(counter_and_domain) > 1:
        raise InvalidCacheException()
    counter = int(counter_and_domain[0])
    return parts[0] + str(extension.preferences['dummymail_ext']) + str(counter + 1) + '@' + counter_and_domain[1]



class DummyMailExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        # get next
        cached_data = cache.load()
        entry = None
        if cached_data:
            entry = cached_data
        else:
            entry = str(extension.preferences['dummymail_base']) + '+' + str(extension.preferences['dummymail_ext']) + '0@' + str(extension.preferences['dummymail_domain'])

        new_entry = None
        try:
            new_entry = increment_dummy(entry, extension)
        except InvalidCacheException:
            logging.error('error trying to increment alias')
            new_entry = entry = str(extension.preferences['dummymail_base']) + '+' + str(extension.preferences['dummymail_ext']) + '0@' + str(extension.preferences['dummymail_domain'])

        cache.save(new_entry)
        item = ExtensionResultItem(icon='images/email_icon.svg',
                                             name='%s' % new_entry,
                                             description='%s' % new_entry,
                                             on_enter=CopyToClipboardAction(new_entry))

        return RenderResultListAction([item])

if __name__ == '__main__':
    DummyMailExtension().run()


