#The following import statements and functions are taken from Mining-the-Social-Web-3rd-Edition Chapter 9 (Twitter Cookbook Examples 1, 16, 17, 19, and 22)
import sys
import time
from urllib.error import URLError
from http.client import BadStatusLine
import json
import twitter
from functools import partial
from sys import maxsize as maxint
import os

#for Graph
import networkx as nx
import pylab as plt

#Example 1
def oauth_login():
    CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
    CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
    OAUTH_TOKEN = os.environ.get("OAUTH_TOKEN")
    OAUTH_TOKEN_SECRET = os.environ.get("OAUTH_TOKEN_SECRET")

    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api




#Example 16
def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):

    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):

        if wait_period > 3600: # Seconds
            print('Too many retries. Quitting.', file=sys.stderr)
            raise e

        # See https://developer.twitter.com/en/docs/basics/response-codes
        # for common codes

        if e.e.code == 401:
            print('Encountered 401 Error (Not Authorized)', file=sys.stderr)
            return None
        elif e.e.code == 404:
            print('Encountered 404 Error (Not Found)', file=sys.stderr)
            return None
        elif e.e.code == 429:
            print('Encountered 429 Error (Rate Limit Exceeded)', file=sys.stderr)
            if sleep_when_rate_limited:
                print("Retrying in 15 minutes...ZzZ...", file=sys.stderr)
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print('...ZzZ...Awake now and trying again.', file=sys.stderr)
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print('Encountered {0} Error. Retrying in {1} seconds'\
                  .format(e.e.code, wait_period), file=sys.stderr)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function

    wait_period = 2
    error_count = 0

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError as e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("URLError encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise
        except BadStatusLine as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("BadStatusLine encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise





#Example 17 changed by me
def get_user_num_of_followers(twitter_api, screen_names=None, user_ids=None):

    # Must have either screen_name or user_id (logical xor)
    assert (screen_names != None) != (user_ids != None), \
    "Must have screen_names or user_ids, but not both"

    items_to_info = {}

    items = screen_names or user_ids

    while len(items) > 0:

        # Process 100 items at a time per the API specifications for /users/lookup.
        # See http://bit.ly/2Gcjfzr for details.

        items_str = ','.join([str(item) for item in items[:100]])
        items = items[100:]

        if screen_names:
            response = make_twitter_request(twitter_api.users.lookup,
                                            screen_name=items_str)
        else: # user_ids
            response = make_twitter_request(twitter_api.users.lookup,
                                            user_id=items_str)
        #Changed to only retrieve followers_count from user info to match as value with id as key
        for user_info in response:
            if screen_names:
                items_to_info[user_info['screen_name']] = user_info.get("followers_count")
            else: # user_ids
                items_to_info[user_info['id']] = user_info.get("followers_count")

    return items_to_info





#Example 19
def get_friends_followers_ids(twitter_api, screen_name=None, user_id=None,
                              friends_limit=maxint, followers_limit=maxint):

    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None), \
    "Must have screen_name or user_id, but not both"

    # See http://bit.ly/2GcjKJP and http://bit.ly/2rFz90N for details
    # on API parameters

    get_friends_ids = partial(make_twitter_request, twitter_api.friends.ids,
                              count=5000)
    get_followers_ids = partial(make_twitter_request, twitter_api.followers.ids,
                                count=5000)

    friends_ids, followers_ids = [], []

    for twitter_api_func, limit, ids, label in [
                    [get_friends_ids, friends_limit, friends_ids, "friends"],
                    [get_followers_ids, followers_limit, followers_ids, "followers"]
                ]:

        if limit == 0: continue

        cursor = -1
        while cursor != 0:

            # Use make_twitter_request via the partially bound callable...
            if screen_name:
                response = twitter_api_func(screen_name=screen_name, cursor=cursor)
            else: # user_id
                response = twitter_api_func(user_id=user_id, cursor=cursor)

            if response is not None:
                ids += response['ids']
                cursor = response['next_cursor']

            print('Fetched {0} total {1} ids for {2}'.format(len(ids),\
                  label, (user_id or screen_name)),file=sys.stderr)

            # XXX: You may want to store data during each iteration to provide an
            # an additional layer of protection from exceptional circumstances

            if len(ids) >= limit or response is None:
                break

    # Do something useful with the IDs, like store them to disk...
    return friends_ids[:friends_limit], followers_ids[:followers_limit]






#Example 22 greatly changed by me
#Takes in api, starting id, and limit for number of nodes
def crawl_followers(twitter_api, seed_id, limit=100):

    #Creates nx graph
    graph = nx.Graph()

    #Starts list of ids with seed id
    list_of_ids = [int(seed_id)]

    #Makes next queue as list of seed id's 5 most popular reciprocal friends
    next_queue = findMostPopularReciprocalFriends(twitter_api, seed_id, limit=5000)

    #Adds seed id and links to 5 popular recip. friends to graph
    graph.add_edges_from([(seed_id, x) for x in next_queue])

    #Adds pop recip friends to list of ids
    list_of_ids = list_of_ids + next_queue

    #Runs while the number at the end of while loop is less than 100
    while graph.number_of_nodes() < limit:
        #Makes queue next queue and empties next queue
        (queue, next_queue) = (next_queue, [])
        #Takes each id from the queue
        for fid in queue:
            #Makes list to add as list of fid's 5 most popular reciprocal friends
            toAdd = findMostPopularReciprocalFriends(twitter_api, fid, limit=5000)
            #Adds fid and links to 5 popular recip. friends to graph
            graph.add_edges_from([(fid, x) for x in toAdd])
            #Adds toAdd to next queue (ends up being a list of all pop recip friends of each id checked)
            next_queue = next_queue + toAdd

        #Adds next queue to list of ids
        list_of_ids = list_of_ids + next_queue

    #Returns finished graph with at least 100 nodes
    return graph





#My Code
def findMostPopularReciprocalFriends(twitter_api, id, limit=100):


    #Taken from Mining-the-Social-Web-3rd-Edition Chapter 9 Example 19
    friends_ids, followers_ids = get_friends_followers_ids(twitter_api,
                                                               user_id=id,
                                                               friends_limit=limit,
                                                               followers_limit=limit)

    #Makes recip friends by taking friends that are also followers
    reciprocal_friends = [x for x in friends_ids if x in followers_ids]

    #Creates empty list for popular recip friends
    pop_reciprocal_friends = []

    #Gets a dictionary where ids are the key and followers count are the values
    recip_friends_profiles = get_user_num_of_followers(twitter_api, user_ids=reciprocal_friends)

    #Runs until 5 ids are added to pop recip friends
    for x in range(len(reciprocal_friends)):
        #Breaks when loop has run 5 times
        if(x > 4):
            break
        #Makes most popular friend and their most follower count
        mpf = ''
        mfc = -1
        #Checks each friend in recip friends' profiles
        for friend in recip_friends_profiles:
            #Checks to see if current most popular friend is less popular than the friend being currently checked
            #While also checking if they're not already in the list of popular recip friends
            if(int(recip_friends_profiles[friend]) > mfc) and (friend not in pop_reciprocal_friends):
                #Replaces values correctly
                mpf = friend
                mfc = recip_friends_profiles[friend]
        #Adds found most popular friend to list of pop recip friends
        pop_reciprocal_friends.append(mpf)

    #Prints the list of the current id's top 5 popular recip friends and returns it
    print("Most popular friends for " + str(id) + ": " + str(pop_reciprocal_friends))
    return pop_reciprocal_friends






#Start
def start():

    #Taken from Mining-the-Social-Web-3rd-Edition Chapter 9
    twitter_api = oauth_login()


    #My code
    #My ID (ID for smeister25)
    startingName = "938267362285015040"
    #Creates graph of at least 100 nodes starting from starting name
    graph = crawl_followers(twitter_api, startingName, limit=100)
    #Draws graph
    nx.draw(graph)
    #Saves drawn graph to computer
    plt.savefig('graph.png')
    #Prints out the graph's number of nodes, diameter, and average distance
    print("Number of nodes = ", graph.number_of_nodes())
    print("Diameter = ", nx.diameter(graph))
    print("Average distance = ", nx.average_shortest_path_length(graph))




#__main__ for script
if __name__ == "__main__":
        start()
