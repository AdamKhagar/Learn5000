import json

class FeedbackListIsEmptyError(Exception):
    pass

class FeedbackTemplate():
    def __init__(self, user_id, isBad:bool, desc: 'text'):
        self.user_id = user_id
        self.isBad = isBad
        self.description = desc
        self.obj = {
            'user_id': user_id,
            'isBad': isBad, 
            'description': desc
        }
        
    def get(self):
        return self.obj
        
class Feedback:
    @staticmethod
    def __get_id():
        try:
            with open('feedbacks/feed_id.json') as f:
                feeds_dict = json.load(f)
            return len(feeds_dict) + 1
        except FileNotFoundError:
            with open('feedbacks/feed_id.json', 'w') as f:
                json.dump({}, f)
            return 1

    @staticmethod
    def __add_feed_id(feed_id):
        try:
            with open('feedbacks/feed_id.json') as f:
                feed_id_dict = json.load(f)
        except FileNotFoundError:
            feed_id_dict = {}
        finally:
            feed_id_dict[feed_id] = False
            with open('feedbacks/feed_id.json', 'w', encoding='utf-8') as f:
                json.dump(feed_id_dict, f, ensure_ascii=False, indent=4)

    @staticmethod
    def save_feedback(obj: FeedbackTemplate):
        if obj.user_id != None and obj.description != None:
            path = f'feedbacks/feeds/#{Feedback.__get_id()}.json'
            Feedback.__add_feed_id(Feedback.__get_id())
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(obj.get(), f, ensure_ascii=False, indent=4)

    @staticmethod
    def read_feedback(bad_only:bool):
        def viewed(feed_dict, key):
            feed_dict[key] = True
            with open('feedbacks/feed_id.json', 'w', encoding='utf-8') as f:
                json.dump(feed_dict, f, ensure_ascii=False, indent=4)

        try:
            with open('feedbacks/feed_id.json', encoding='utf-8') as f:
                feeds_dict = json.load(f)
        except FileNotFoundError:
            return 'no feeds'
        else:
            for feed_key, feed_value in feeds_dict.items():
                if not feed_value:
                    with open(f'feedbacks/feeds/#{feed_key}.json', encoding='utf-8') as f:
                        feed = json.load(f)
                    if bad_only:
                        if feed['isBad']:
                            viewed(feeds_dict, feed_key)
                            break
                    else:
                        viewed(feeds_dict, feed_key)
                        break
            else:
                raise FeedbackListIsEmptyError('feedback list is empty or all feedback are viewed')
            return feed