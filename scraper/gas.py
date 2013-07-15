import requests
import lxml.html

html = requests.get("http://gsmbensin.is/gsmbensin_web.php")
root = lxml.html.fromstring(html.text)
niutiuogfimmokt = []
diesel = []
trs95 = root.xpath('//div[@id="okt95"]/table/tr')
trsdiesel = root.xpath('//div[@id="disel"]/table/tr')
for tr in trs95[1:]:
    niutiuogfimmokt.append( float(tr[2].text_content()))
for tr in trsdiesel[1:]:
    diesel.append( float(tr[2].text_content()))

niutiuogfimmprice = round(sum(niutiuogfimmokt) / float(len(niutiuogfimmokt)))
#print niutiuogfimmprice
dieselprice = round(sum(diesel) / float(len(diesel)))
#print dieselprice


f = open('gas.txt','w')
f.write(str(niutiuogfimmprice))
f.write('\n')
f.write(str(dieselprice))
f.close
