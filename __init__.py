from mycroft import MycroftSkill, intent_file_handler


class RespeakerPixelRing(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('ring.pixel.respeaker.intent')
    def handle_ring_pixel_respeaker(self, message):
        self.speak_dialog('ring.pixel.respeaker')


def create_skill():
    return RespeakerPixelRing()

