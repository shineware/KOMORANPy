from timeit import default_timer as timer


class TimeChecker:
    time_store_dict = {}
    elapsed_time_dict = {}

    @staticmethod
    def start(key, suffix='_start'):
        TimeChecker.time_store_dict[key + suffix] = timer()

    @staticmethod
    def end(key, suffix='_end'):
        TimeChecker.time_store_dict[key + suffix] = timer()
        elapsed_time = TimeChecker.elapsed_time_dict.get(key)
        if elapsed_time is None:
            elapsed_time = 0.0
        elapsed_time += TimeChecker.time_store_dict[key + '_end'] - TimeChecker.time_store_dict[key + '_start']
        TimeChecker.elapsed_time_dict[key] = elapsed_time

