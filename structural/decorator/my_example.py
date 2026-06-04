import time


def log_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Execution time: {end_time - start_time} seconds")
        return result

    return wrapper


def log_args(func):
    def wrapper(*args, **kwargs):
        print(f"Arguments: {args}, {kwargs}")
        return func(*args, **kwargs)

    return wrapper


def log_result(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"Result: {result}")
        return result

    return wrapper


def check_policy(func):
    def wrapper(*args, **kwargs):
        print("Checking policy...")
        if not args or args[0] != "admin":
            raise PermissionError("Access denied")
        return func(*args, **kwargs)

    return wrapper


@check_policy
@log_time
@log_args
@log_result
def process_data(user, data):
    time.sleep(2)  # Simulate processing time
    return f"Processed data for {user}: {data}"


if __name__ == "__main__":
    try:
        process_data("admin", "some important data")
        process_data("guest", "some important data")
    except PermissionError as e:
        print(e)
