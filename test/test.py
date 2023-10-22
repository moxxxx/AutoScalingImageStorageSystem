import os

import requests

url = 'http://44.200.16.192' + ':5000/api'

response = requests.post(url + "/delete_all")
jsonResponse = response.json()
print(jsonResponse)

response = requests.post(url + "/list_keys")
print(response.json())

filenames = ['1.jpeg', '2.png']
work_dir = os.path.abspath(os.getcwd())

file_1 = {'file': open(work_dir + '/images/' + filenames[0], 'rb')}
response = requests.post(url + "/upload", files=file_1, data={'key': 'test_1'})
print(response.json())
response = requests.post(url + "/list_keys")
print(response.json())
file_2 = {'file': open(work_dir + '/images/' + filenames[1], 'rb')}
response = requests.post(url + "/upload", files=file_2, data={'key': 'test_2'})
print(response.json())
response = requests.post(url + "/list_keys")
print(response.json())
response = requests.post(url + "/key/test_1")
print(response.json())
response = requests.post(url + "/key/test_2")
print(response.json())
# test 5: configure cache settings
print("--------------------------------------------------------------------")
print("test 5: configure the cache (manual mode)")

test_5_flag_1 = True
try:
    response = requests.post(url + '/configure_cache',
                             params={'mode': 'manual', 'numNodes': 2, 'cacheSize': 3, 'policy': 'RR'})
except:
    print("error in test 5: could not post /configure_cache to your web app")
    print("check the web app connection, IP, port, API endpoint path, etc.")
    test_5_flag_1 = False

if test_5_flag_1:
    try:
        jsonResponse = response.json()
    except:
        print("error in test 5: your response cannot be represented in JSON format.")

    try:
        if jsonResponse["success"] == "true" and jsonResponse["mode"] == "manual" \
                and jsonResponse["numNodes"] == 2 and jsonResponse["cacheSize"] == 3 \
                and jsonResponse["policy"] == "RR":
            score += 1
        else:

            print("""error in test 5: /configure_cache operation should return 
                    {
                        "success": "true",
                        "mode": "manual",
                        "numNodes": 2,
                        "cacheSize": 3,
                        "policy": "RR"
                    }""")
            print("your response: ")
            print(jsonResponse)
            print("")
    except:
        print(
            "error in test 5: access failure on ['success']/['mode']/['numNodes']/['cacheSize']/['policy'] of the post response.")
        print("")

# test 6: get number of nodes
print("--------------------------------------------------------------------")
print("test 6: get number of nodes")

test_6_flag_1 = True
try:
    response = requests.post(url + '/getNumNodes')
except:
    print("error in test 6: could not post /getNumNodes to your web app")
    print("check the web app connection, IP, port, API endpoint path, etc.")
    test_6_flag_1 = False

if test_6_flag_1:
    try:
        jsonResponse = response.json()
    except:
        print("error in test 6: your response cannot be represented in JSON format.")
    try:
        if jsonResponse["success"] == "true" and jsonResponse["numNodes"] == 2:
            score += 1
        else:
            print("""error in test 6: /getNumNodes operation should return 
                {
                    "success": "true",
                    "numNodes": 2
                }""")
            print("your response: ")
            print(jsonResponse)
            print("")
    except:
        print("error in test 6: access failure on ['success']/['numNodes'] of the post response.")
        print("")

# test 7: get miss rate
print("--------------------------------------------------------------------")
print("test 7: get miss rate")

test_7_flag_1 = True
try:
    response = requests.post(url + "/getRate", params={'rate': 'miss'})
except:
    print("error in test 7: could not post /getRate to your web app")
    print("check the web app connection, IP, port, API endpoint path, etc.")
    test_7_flag_1 = False

if test_7_flag_1:
    try:
        jsonResponse = response.json()
    except:
        print("error in test 7: your response cannot be represented in JSON format.")
    try:
        if jsonResponse["success"] == "true" and jsonResponse["rate"] == "miss":
            score += 1
            print(jsonResponse["value"])
            print("Endpoint passes, but you should also check that your 'value' field returns the miss rate for the "
                  "last 1 minute.")
        else:
            print("""error in test 7: /getRate operation should return 
                {
                   "success": "true",
                    "rate": "miss",
                    "value": miss rate for the last 1 minute (as float)
                }""")
            print("your response: ")
            print(jsonResponse)
            print("")
    except:
        print("error in test 7: access failure on ['success']/['getRate'] of the post response.")
        print("")

print("--------------------------------------------------------------------")
print("tester total: {}/8".format(score))
