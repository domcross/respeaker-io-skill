import time
from pixel_ring import pixel_ring
from . import mraa
import os
from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.log import LOG


class RespeakerPixelRing(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        LOG.debug("initialising")
        self.en = mraa.Gpio(12)
        if os.geteuid() != 0:
            time.sleep(1)

        self.en.dir(mraa.DIR_OUT)
        self.en.write(0)
        pixel_ring.set_brightness(20)
        pixel_ring.wakeup()

        self.add_event('recognizer_loop:record_begin',
                       self.handle_listener_wakeup)
        self.add_event('recognizer_loop:record_end', self.handle_listener_off)
        self.add_event('recognizer_loop:audio_output_start',
                       self.handle_listener_speak)
        self.add_event('recognizer_loop:audio_output_end',
                       self.handle_listener_off)
        self.add_event('mycroft.skill.handler.start',
                       self.handle_listener_think)
        self.add_event('mycroft.skill.handler.complete',
                       self.handle_listener_off)
        pixel_ring.off()

    def shutdown(self):
        LOG.debug("shutdown")
        pixel_ring.off()
        self.en.write(1)

    def handle_listener_wakeup(self, message):
        LOG.debug("wakeup")
        pixel_ring.wakeup()

    def handle_listener_think(self, message):
        LOG.debug("think")
        pixel_ring.think()

    def handle_listener_speak(self, message):
        LOG.debug("speak")
        pixel_ring.speak()

    def handle_listener_off(self, message):
        LOG.debug("off")
        pixel_ring.off()

    @intent_file_handler('ring.pixel.respeaker.intent')
    def handle_ring_pixel_respeaker(self, message):
        self.speak_dialog('ring.pixel.respeaker')


def create_skill():
    return RespeakerPixelRing()
