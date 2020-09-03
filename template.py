
class Template():
    @staticmethod
    def __get(file_name):
        path = f'templates/{file_name}.txt'
        with open(path, encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def about():
        return Template.__get('about')

    @staticmethod
    def data_error():
        return Template.__get('data_error')

    @staticmethod
    def feed_a():
        return Template.__get('feed_a')
    
    @staticmethod
    def feed_b_a():
        return Template.__get('feed_b_a')

    @staticmethod
    def feed_q():
        return Template.__get('feed_q')

    @staticmethod
    def count_n_q():
        return Template.__get('count_n_q')

    @staticmethod
    def count_r_q():
        return Template.__get('count_r_q')

    @staticmethod
    def end_set():
        return Template.__get('end_set')
    
    @staticmethod
    def first_message():
        return Template.__get('first_message')

    @staticmethod
    def get_words():
        return Template.__get('get_words')

    @staticmethod
    def lang_b_a():
        return Template.__get('lang_b_a')

    @staticmethod
    def lang_g_a():
        return Template.__get('lang_g_a')

    @staticmethod
    def lang_q():
        return Template.__get('lang_q')

    @staticmethod
    def manual():
        return Template.__get('manual')

    @staticmethod
    def no_await():
        return Template.__get('no_await')

    @staticmethod
    def no_digit():
        return Template.__get('no_digit')

    @staticmethod
    def reset():
        return Template.__get('reset')

    @staticmethod
    def time_b_a():
        return Template.__get('time_b_a')

    @staticmethod
    def time_g_a():
        return Template.__get('time_g_a')

    @staticmethod
    def time_q():
        return Template.__get('time_q')

    @staticmethod
    def limit():
        return Template.__get('limit')