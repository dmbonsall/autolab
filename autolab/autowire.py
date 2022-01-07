import functools

def autowire(arg, generator):
    """Uses the provided generator function to inject a dependency into the function."""
    def autowire_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            dep_generator = None
            if kwargs.get(arg, None) is None:
                dep_generator = generator()
                dep = next(dep_generator)
                kwargs.update({arg: dep})

            ret_val = func(*args, **kwargs)

            if dep_generator is not None:
                dep_generator.close()

            return ret_val

        return wrapper

    return autowire_decorator
