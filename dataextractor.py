
import urllib.request
import urllib.robotparser

print("Start.")
default_user_agent = "Python-urllib/3.7"
base_url = "https://www.filmaffinity.com/"
base_path = "es/all_awards.php?order=all"


rp = urllib.robotparser.RobotFileParser()
rp.set_url(base_url + "robots.txt")
rp.read()
next_url = base_url + base_path
if rp.can_fetch(default_user_agent, next_url):
    response = urllib.request.urlopen(base_url)
    data = response.read().decode('utf-8')

    print(data)
else:
    print ("Cannot fetch")