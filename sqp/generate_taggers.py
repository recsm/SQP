from cPickle import dump
import nltk


# English tagger
tagged_sents = nltk.corpus.brown.tagged_sents(categories='a')
t0 = nltk.DefaultTagger('NN') # if word not known, just guess "noun"
affix_tagger = nltk.AffixTagger(tagged_sents, backoff=t0)
unigram_tagger = nltk.UnigramTagger(tagged_sents, cutoff=0, backoff=affix_tagger)
bigram_tagger = nltk.BigramTagger(tagged_sents, cutoff=0, backoff=unigram_tagger)
trigram_tagger = nltk.TrigramTagger(tagged_sents, cutoff=0, backoff=bigram_tagger)
output = open('bigram_tagger_english.pkl', 'wb')
dump(trigram_tagger, output, -1)
output.close()

tagged_sents = None
t0 = None
affix_tagger = None
unigram_tagger = None
bigram_tagger = None
trigram_tagger = None

# Dutch tagger
tagged_sents = nltk.corpus.alpino.tagged_sents()
t0 = nltk.DefaultTagger('noun') # if word not known, just guess "noun"
affix_tagger = nltk.AffixTagger(tagged_sents, backoff=t0)
unigram_tagger = nltk.UnigramTagger(tagged_sents, cutoff=0, backoff=affix_tagger)
bigram_tagger = nltk.BigramTagger(tagged_sents, cutoff=0, backoff=unigram_tagger)
trigram_tagger = nltk.TrigramTagger(tagged_sents, cutoff=0, backoff=bigram_tagger)
output = open('bigram_tagger_dutch.pkl', 'wb')
dump(trigram_tagger, output, -1)
output.close()

tagged_sents = None
t0 = None
affix_tagger = None
unigram_tagger = None
bigram_tagger = None
trigram_tagger = None

# Catalan tagger
tagged_sents = nltk.corpus.cess_cat.tagged_sents()
t0 = nltk.DefaultTagger('nc') # if word not known, just guess "noun"
affix_tagger = nltk.AffixTagger(tagged_sents, backoff=t0)
unigram_tagger = nltk.UnigramTagger(tagged_sents, cutoff=0, backoff=affix_tagger)
bigram_tagger = nltk.BigramTagger(tagged_sents, cutoff=0, backoff=unigram_tagger)
trigram_tagger = nltk.TrigramTagger(tagged_sents, cutoff=0, backoff=bigram_tagger)
output = open('bigram_tagger_catalan.pkl', 'wb')
dump(trigram_tagger, output, -1)
output.close()

tagged_sents = None
t0 = None
affix_tagger = None
unigram_tagger = None
bigram_tagger = None
trigram_tagger = None

# Spanish tagger
tagged_sents = nltk.corpus.cess_esp.tagged_sents()
t0 = nltk.DefaultTagger('nc') # if word not known, just guess "noun"
affix_tagger = nltk.AffixTagger(tagged_sents, backoff=t0)
unigram_tagger = nltk.UnigramTagger(tagged_sents, cutoff=0, backoff=affix_tagger)
bigram_tagger = nltk.BigramTagger(tagged_sents, cutoff=0, backoff=unigram_tagger)
trigram_tagger = nltk.TrigramTagger(tagged_sents, cutoff=0, backoff=bigram_tagger)
output = open('bigram_tagger_spanish.pkl', 'wb')
dump(trigram_tagger, output, -1)
output.close()

tagged_sents = None
t0 = None
affix_tagger = None
unigram_tagger = None
bigram_tagger = None
trigram_tagger = None

# Portuguese tagger
tagged_sents = nltk.corpus.floresta.tagged_sents()
t0 = nltk.DefaultTagger('H+n') # if word not known, just guess "noun"
affix_tagger = nltk.AffixTagger(tagged_sents, backoff=t0)
unigram_tagger = nltk.UnigramTagger(tagged_sents, cutoff=0, backoff=affix_tagger)
bigram_tagger = nltk.BigramTagger(tagged_sents, cutoff=0, backoff=unigram_tagger)
trigram_tagger = nltk.TrigramTagger(tagged_sents, cutoff=0, backoff=bigram_tagger)
output = open('bigram_tagger_portuguese.pkl', 'wb')
dump(trigram_tagger, output, -1)
output.close()

tagged_sents = None
t0 = None
affix_tagger = None
unigram_tagger = None
bigram_tagger = None
trigram_tagger = None


# German tagger
from read_tagged_sents_tiger import sentences as tagged_sents
t0 = nltk.DefaultTagger('NN') # if word not known, just guess "noun"
affix_tagger = nltk.AffixTagger(tagged_sents, backoff=t0)
unigram_tagger = nltk.UnigramTagger(tagged_sents, cutoff=0, backoff=affix_tagger)
bigram_tagger = nltk.BigramTagger(tagged_sents, cutoff=0, backoff=unigram_tagger)
trigram_tagger = nltk.TrigramTagger(tagged_sents, cutoff=0, backoff=bigram_tagger)
#trigram_tagger = nltk.TrigramTagger(tagged_sents, cutoff=0, backoff=bigram_tagger)
#nltk.tag.accuracy(trigram_tagger, tagged_sents)

output = open('bigram_tagger_german.pkl', 'wb')
dump(trigram_tagger, output, -1)
output.close()




