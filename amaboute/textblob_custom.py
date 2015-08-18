from textblob import Blobber
from textblob_fr import PatternTagger, PatternAnalyzer

__all__ = ('TextBlob',)

TextBlob = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())
