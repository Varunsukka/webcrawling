# these are the libraries which i used for this program. 
from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError, ReadTimeout, InvalidURL
from requests.packages import urllib3
import networkx as nx
import matplotlib.pyplot as plt
import community as com

# i used disable warnings to disable https certification warnings.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


BASE_URL = "https://ontariotechu.ca/"
# I used dictionary to remove duplicate values anf maintain url list and fetched state.
GLOBAL_DICT = {}
# I used queue so that every node is searched in BFS manner.
URL_QUEUE = []

G = nx.Graph()

# in this function we add nodes to graph
def add_to_graph(base_url, children):
    for child in children:
        G.add_edge(base_url, child)
    GLOBAL_DICT[base_url] = True

# The following function remove unnessasary urls and i removed convocation to reduce my Mwmory error(RAM Consumption)
def exclude(url):
    exclude_list = [
        "index",
        "youtube",
        "convocation",
        ".pdf",
        ".jpeg",
        ".jpg",
        ".doc",
        ".aspx",
        ".xlsx",
        ".png",
        ".img",
        ".mp4",
        ".gif",
        ".mov",
        ".wmv",
        ".avi",
        ".zip",
        "#",
        "javascript",
        "instagram",
        "linkedin",
        "mailto",
        "twitter",
        "facebook",
        "tiktok",
        "snapchat",
        "utils",
        "trudeaufoundation",
        "2d-square-falling-from-the-sky",
    ]

    for i in exclude_list:
        if i in url:
            return False

    return True

# This will make sure that we get links only related to "uoit.ca", "ontariotechu.ca"
def include(url):
    includelist = ["uoit.ca", "ontariotechu.ca"]
    for i in includelist:
        if i in url:
            return True

    return False

# it will convert relative URLS to absolute URLS.
def resolveUrl(base_url, child):

    domain = base_url[: base_url[9:].find("/") + 10]
    # it will just consider the domain then if the link  dont have ".html" or".php" then we will add a "/" to reduce duplicate values
    child_page = child.split(".")[-1] in ["html", "php"] or child[-1] == "/"
    child = child + ("" if child_page else "/")
    # if in worst case if we have "/" after "HTML" or "PHP" then we are removing "/" from the end
    if child.split(".")[-1] in ["html/", "php/"]:
        child = child[:-1]
    # if link start with out domain then we will give our base URL as domain
    if child[0] == "/":
        child = domain + child[1:]
    elif child[0:4] == "http":
        child = child
    #if a link dont have http or "/" or "." then it can be any file name so i just asdded that to end of base URL.
    elif child[0] not in ["h", "/", "."]:
        child = base_url[: base_url.rfind("/") + 1] + child
    #if a link have "../" in starting part of child then it indicated to go back a directory so i went back a directory. 
    else:
        base_path = base_url[: base_url.rfind("/")]
        child_chunks = child.split("/")
        for i in range(len(child_chunks)):
            if child_chunks[i] == "..":
                base_path = "/".join(base_path.split("/")[:-1])
            else:
                child = base_path + "/" + "/".join(child_chunks[i:])
                break

    return child

# it will verify if the url is valid or not
def verify_url(url):
    if url[-1] == "/" or url.split(".")[-1] in ["html", "php"]:
        return True
    return False

# this function crawls all the website in a BFS manner
def crawl(url):
    try:
        #if a links doesnt respod with in 3 minutes then it is probably not in service so i just raise an error 
        with requests.get(url, verify=False, timeout=3, allow_redirects=False) as response:
            response_text = response.content

        links = set()
         # it take the link response and convert to beautiful soap object 
        response_soup = BeautifulSoup(response_text, features="html.parser")
        # getting all the achor tags qith Href and deleting params
        for a in response_soup.find_all("a", href=True):
            href = a["href"].lower().strip().split("?")[0]
            if len(href) > 0 and exclude(href) and verify_url(href):
                child_url = resolveUrl(url, href)
                #if child and parent URL are same then we will directly move to the next child URL
                if child_url == url:
                    continue
                # this will add the urls obtains from the above anchor tags to Links
                links.add(child_url)
                # this will check if the link is visited or not then adding it to URL queue and global_dict
                if include(child_url):
                    GLOBAL_DICT[child_url] = GLOBAL_DICT.get(child_url, False)
                    if not GLOBAL_DICT[child_url] and child_url not in URL_QUEUE:
                        URL_QUEUE.append(child_url)
        # after retriving all child links we will add them to graph (networkx)
        add_to_graph(url, links)
    #if link throws an exception then it will go into fail nodes file
    except (ReadTimeout, ConnectionError, InvalidURL):
        GLOBAL_DICT[url] = True
        with open("FAILED.txt", "a", encoding="utf-8") as f:
            f.write(url + "\n")

    return


nodes = 0
#it makes the global value to be visited
GLOBAL_DICT[BASE_URL] = False
# then it will append the current base url to URL_Queue
URL_QUEUE.append(BASE_URL)
# initialsing URL len to zero
urllen = 0
#
while len(URL_QUEUE) > 0:
    if not GLOBAL_DICT[URL_QUEUE[0]]:
        crawl(URL_QUEUE[0])
        urllen += 1
# printing the stats of URLs visited and fetched to maintain a record during Code execution
    URL_QUEUE.pop(0)
    print(
        "URLS visited:",
        urllen,
        "STACK LENGTH:",
        len(URL_QUEUE),
        "CURRENT URLS COUNT:",
        len(GLOBAL_DICT.keys()),
        end="\r",
    )
    if nodes + 1000 < len(GLOBAL_DICT.keys()):
        with open("URLSads1.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(GLOBAL_DICT.keys())))
        nodes += 1000
        print(f"Saved {len(GLOBAL_DICT.keys())} to JSON -- URLS1.txt")
# generating graph 
print("statistics of network")
#using community detection to split all nodes into modules

print(nx.info(G))
print("Directed Graph:", nx.is_directed(G))
print("Weighted Graph:", nx.is_weighted(G))
print("Edge density",nx.density(G))
print("average clustering coeff", nx.average_clustering(G))
print("connected components",[len(x) for x in sorted(nx.connected_components(G),key=len)])
print ("Network diameter:", nx.diameter(G))
print("avg path length:",nx.average_shortest_path_length(G))
print("Degree centrality")
count1=0
for x in sorted(nx.degree_centrality(G),key=nx.degree_centrality(G).get):
    print(x,nx.degree_centrality(G)[x])
    count1=count1+1
    if(count1==10):
        break
count1=0
print("Eigenvector centrality")

for x in sorted(nx.eigenvector_centrality(G),key=nx.eigenvector_centrality(G).get):
    print(x,nx.eigenvector_centrality(G)[x])
    count1=count1+1
    if(count1==10):
        break
print("community detection")

p = com.best_partition(G)

values = [p.get(node) for node in G.nodes()]
print("Number of communities",len(values))
nx.draw_spring(
    G, cmap=plt.get_cmap(), node_color=values, node_size=10, with_labels=False
)
plt.savefig("page_map_png.png")
plt.show()

degrees = [G.degree(n) for n in G.nodes()]
plt.hist(degrees)
plt.show()

with open("URL.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(GLOBAL_DICT.keys())))