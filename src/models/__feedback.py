class FeedBack:
    def __init__(self, fb_json: dict):
        self.false_positives = {
            link["source"]: link["target"] for link in fb_json["falsePositives"]
        }
        self.false_alerts = fb_json["notBelong"]
        self.new_links = {
            link["source"]: link["target"] for link in fb_json["addedLinks"]
        }
