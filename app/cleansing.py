import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

def casefolding(text):
  text = text.lower()
  text = text.replace('\r', ' ').replace('\n', ' ')  # Replace New Line
  text = re.sub(r'\s+', ' ', text).strip()
  return text

def token(text):
  nstr = text.split()
  dat = []
  a = -1
  for hu in nstr:
    a = a+1
    if hu == '':
      dat.append(a)
  p=0
  b=0
  for q in dat:
    b = q - p
    del nstr[b]
    p = p + 1
  return nstr

def stemming(text):
  factory = StemmerFactory()
  stemmer = factory.create_stemmer()
  do = []
  for w in text:
    dt = stemmer.stem(w)
    do.append(dt)
  d_clean=[]
  d_clean=" ".join(do)
  return(d_clean)