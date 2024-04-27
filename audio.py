import pygame
import utils


class Audio:
    def __init__(self):
        pygame.mixer.init()
        self.is_audio_paused = False
        self.audio_file = utils.resource_path('sound.mp3')
        pygame.mixer.music.load(self.audio_file)

    def play_audio(self):
        '''
        Play audio if any notice gets retrieved
        '''

        self.play_audio = False
        pygame.mixer.music.play(loops=-1)

    def pause_unpause_audio(self, event):
        '''
        Pause or unpause audio when pressed space key
        '''

        if self.is_audio_paused:
            pygame.mixer.music.unpause()

        else:
            pygame.mixer.music.pause()

        self.is_audio_paused = not self.is_audio_paused
