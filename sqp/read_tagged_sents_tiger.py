import re

tags = r"(UNKNOWN|--|ADJA|ADJD|ADV|APPR|APPRART|APPO|APZR|ART|CARD|FM|ITJ|KOUI|KOUS|KON|KOKOM|NN|NE|PDS|PDAT|PIS|PIAT|PPER|PPOSS|PPOSAT|PRELS|PRELAT|PRF|PWS|PWAT|PWAV|PROAV|PTKZU|PTKNEG|PTKVZ|PTKANT|PTKA|TRUNC|VVFIN|VVIMP|VVINF|VVIZU|VVPP|VAFIN|VAIMP|VAINF|VAPP|VMFIN|VMINF|VMPP|XY|\$,|\$.|\$\(|NNE)"

bos = re.compile(r"^#BOS[ \t]+([0-9]+)")
tagged_pair = re.compile(r"^([^\t#]+?)[\t]+[^\t]+?[\t]+" + tags)
eos = re.compile(r"^#EOS[ \t]+([0-9]+)")

f = open("/usr/share/nltk_data/corpora/tiger/corpus/tiger_release_aug07.export", 'rb')

sentences = [ [], ]
cur_sentence = 0
line = f.readline()

while(line):
   pair = tagged_pair.findall(line)
   if (len(pair) > 0):
      sentences[cur_sentence].extend(pair)
   else:
      if(len(bos.findall(line)) > 0):
         sentences.append( [] )
         cur_sentence += 1
   line = f.readline()

f.close()
sentences = sentences[1:]
