import requests
import re
import io
import os
import sys
from datetime import datetime, timedelta
import pytz

EPG_ROOT = '.'  # مكان حفظ bein.xml

print('**************BEIN SPORTS EPG******************')
sys.stdout.flush()

def bein():
    channels_found = []

    # 🕐 التوقيت المحلي (مثال: الرياض)
    local_timezone = pytz.timezone("Asia/Riyadh")
    today = datetime.now(local_timezone)

    for i in range(0, 3):  # ثلاث أيام قدام
        week = (today + timedelta(days=i)).strftime('%Y-%m-%d')
        with requests.Session() as s:
            for idx in range(0, 4):
                url = f'https://www.bein.com/ar/epg-ajax-template/?action=epg_fetch&category=sports&serviceidentity=bein.net&offset=00&mins=00&cdate={week}&language=AR&postid=25344&loadindex={idx}'
                data = s.get(url).text
                time = re.findall(r'<p\sclass=time>(.*?)<\/p>', data)
                times = [t.replace('&nbsp;-&nbsp;', '-').split('-') for t in time]
                title = re.findall(r'<p\sclass=title>(.*?)<\/p>', data)
                formt = re.findall(r'<p\sclass=format>(.*?)<\/p>', data)
                channels = re.findall(r"data-img.*?sites\/\d+\/\d+\/\d+\/(.*?)\.png", data)
                live_events = re.findall(r"li\s+live='(\d)'", data)
                channels_found += channels

                desc = []
                title_chan = []
                for tit in title:
                    title_chan.append(tit.replace('   ', ' ').split('- ')[0])
                    spl = re.search(r'-\s(.*)', tit)
                    if spl:
                        desc.append(spl.group().replace('- ', '').replace('&', 'and'))
                    else:
                        desc.append(tit.replace('&', 'and'))

                try:
                    for title_, form_, time_, ch, des, is_live in zip(title_chan, formt, times, channels, desc, live_events):
                        date = week
                        starttime = datetime.strptime(date + ' ' + time_[0], '%Y-%m-%d %H:%M').strftime('%Y%m%d%H%M%S')
                        endtime = datetime.strptime(date + ' ' + time_[1], '%Y-%m-%d %H:%M').strftime('%Y%m%d%H%M%S')
                        live = "Live: " if is_live == "1" else ""
                        epg = ''
                        epg += 2 * ' ' + f'<programme start="{starttime} +0300" stop="{endtime} +0300" channel="{ch.replace("_Digital_Mono", "").replace("-1", "")}">\n'
                        epg += 4 * ' ' + f'<title lang="en">{live}{title_.replace("&", "and").strip()} - {form_.replace("2014", "2021")}</title>\n'
                        epg += 4 * ' ' + f'<desc lang="ar">{des}</desc>\n  </programme>\r'
                        with io.open(os.path.join(EPG_ROOT, 'bein.xml'), "a", encoding='UTF-8') as f:
                            f.write(epg)
                except:
                    break

                if len(title) != 0:
                    print(f'Date : {week} & Index : {idx}')
                    sys.stdout.flush()
                else:
                    print('No data found')
                    break

    if len(channels_found) > 0:
        channels_found = sorted([ch.replace('_Digital_Mono', '').replace('-1', '') for ch in list(dict.fromkeys(channels_found))])
        print("Found channels:", channels_found)

def main():
    bein()

if __name__ == '__main__':
    main()

print("**************FINISHED******************")
