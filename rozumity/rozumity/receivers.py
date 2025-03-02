from django.dispatch.dispatcher import Signal
from celery import shared_task


# Warning. Monkey patch.
# in the kwargs signal recievers are passed an instance of django.display.dispatcher.Signal and
# this contains an instance of threading.Lock - an object that can't be pickled.
# This leads me to the monkey patch that was shown at the start of this article which
# simply adds a __reduce__ method to the Signal class that alters the pickle behaviour and only
# pickles the provided_args property of the Signal instance.
# Ref: http://dougalmatthews.com/2011/Oct/10/making-djangos-signals-async-with-celery/
# https://gist.github.com/inabhi9/316e2ca25b45222559db
def reducer(self):
    return (Signal, (self.providing_args,))
Signal.__reduce__ = reducer


def async_receiver(signal, **kwargs):
    """
    Decorator to perform django signal asynchronously using Celery. The function decorated with
    this should be recognized by celery. django signal mechanism should be working normally and
    no additional changes are required while using in-built signals or custom signals.
    """
    def _decorator(func):
        # Convert normal function to celery task
        func_celery = shared_task(func)

        # Connect to a signal
        if isinstance(signal, (list, tuple)):
            for s in signal:
                # Weak is false as proxyfunc doesn't exists outside the closure scope. So cannot
                # be referenced weakly and will be erased by garbage collector
                s.connect(func_celery.delay, **kwargs)
        else:
            signal.connect(func_celery.delay, **kwargs)

        # To let celery recognize normal function as celery task
        return func_celery

    return _decorator
