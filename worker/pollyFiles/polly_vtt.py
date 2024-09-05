from .polly import Polly
from .vtt import VTT


class PollyVTT:
    def __init__(self, params,**kwargs):
        self.polly = Polly(params)

    def generate(self, filename, format="vtt", **polly_params):
        resp, filename, length = self.polly.synthesize(filename, **polly_params)
        vtt = VTT(AudioLengthInMs=length, PollyResponse=resp, Filename=filename, Format=format)
        vtt.write(t = polly_params["Text"])
        return length/1000