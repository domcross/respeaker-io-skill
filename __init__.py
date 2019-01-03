# Copyright 2018, domcross
# Github https://github.com/domcross
#
# inspired by https://github.com/andlo/picroft-google-aiy-voicekit-skill.git
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
from evdev import InputDevice
from pixel_ring import pixel_ring
from . import mraa
import os
from mycroft import MycroftSkill, intent_file_handler
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG


class RespeakerIo(MycroftSkill):
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

        self.userkey = None
        try:
            self.userkey = InputDevice("/dev/input/event0")
        except Exception as e:
            LOG.debug("exception while reading InputDevice: {}".format(e))

        if self.userkey:
            self.schedule_repeating_event(self.handle_button, None, 0.1,
                                          'RespeakerIo')

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

    def handle_button(self, message):
        if not self.userkey:
            return

        longpress_threshold = 2
        respeaker_userkey_code = 194

        if respeaker_userkey_code in self.userkey.active_keys():
            pressed_time = time.time()
            while respeaker_userkey_code in self.userkey.active_keys():
                time.sleep(0.2)
            pressed_time = time.time()-pressed_time
            if pressed_time < longpress_threshold:
                self.bus.emit(Message("mycroft.mic.listen"))
            else:
                self.bus.emit(Message("mycroft.stop"))

    @intent_file_handler('ring.pixel.respeaker.intent')
    def handle_ring_pixel_respeaker(self, message):
        self.speak_dialog('ring.pixel.respeaker')


def create_skill():
    return RespeakerIo()
