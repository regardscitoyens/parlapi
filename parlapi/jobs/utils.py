import ijson
from ijson.common import ObjectBuilder


def ijson_items(input, prefixes):
    """
    Identical to ijson.items, but accepts multiple prefixes and yields
    (prefix, value) tuples
    """
    def _items(prefixed_events, prefixes):
        prefixed_events = iter(prefixed_events)
        try:
            while True:
                current, event, value = next(prefixed_events)
                if current in prefixes:
                    current_prefix = current
                    if event in ('start_map', 'start_array'):
                        builder = ObjectBuilder()
                        end_event = event.replace('start', 'end')
                        while (current, event) != (current_prefix, end_event):
                            builder.event(event, value)
                            current, event, value = next(prefixed_events)
                        yield (current_prefix, builder.value)
                    else:
                        yield (current_prefix, value)
        except StopIteration:
            pass

    return _items(ijson.parse(input), prefixes)
