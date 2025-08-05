import threading
import time
from tinydb import TinyDB
from nicegui import ui


from multiprocessing import Queue
import json

def get_reports():
    db = TinyDB('reports.json')
    data = db.all()
    print(data)
    fdata = []
    for exp in data:
        try:
            fdata.append({
                "latitude":exp["latitude"],
                "longitude":exp["longitude"],
                "image_source":exp["image_source"],
                "output_image":exp["result"]["output_image"],
                "field1":exp["result"]["field1"],
                "field2":exp["result"]["field2"],
                "field3":exp["result"]["field3"],
            })
        except:
            fdata.append({
                "latitude":exp["latitude"],
                "longitude":exp["longitude"],
                "image_source":exp["image_source"],
                "output_image":"",
                "field1":"",
                "field2":"",
                "field3":"",
            })

    return fdata

def get_analysis():
    file = 'analysis.json' 
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        print("JSON data loaded")
        return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file}'. Check for a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def store_analysis(latitude,longitude,color_input,image_source,result):
    data = {
        "latitude": latitude,
        "longitude": longitude,
        "color_input": color_input,
        "image_source": image_source,
        "result":result
    }
    try:
        with open("analysis.json", "w") as json_file:
            json.dump(data, json_file, indent=4)
    except IOError as e:
        print(f"Error writing to file: {e}")
    except TypeError as e:
        print(f"Error serializing data: {e}")

def analyze(q: Queue) -> str:
    steps = 5
    step = 1
    time.sleep(1)
    q.put_nowait(step / steps)
    step = 2
    time.sleep(2)
    q.put_nowait(step / steps)
    step = 3
    time.sleep(1)
    q.put_nowait(step / steps)
    step = 4
    time.sleep(3)
    q.put_nowait(step / steps)
    step = 5
    time.sleep(1)
    q.put_nowait(step / steps)
    data=get_analysis() #get the written analysis.json when image was loaded
    data["result"]={ #add the results in this data dictionary
        "output_image":"pending",
        "field1":"value1",
        "field2":"value2",
        "field3":"value3"                
    }
    #updates the analysis.json file with the data dictionary
    store_analysis(data["latitude"],data["longitude"],data["color_input"],data["image_source"],data["result"])
    return 'Done!'

def save_report():
    data = get_analysis()
    db = TinyDB('reports.json')
    db.insert(data)
#    Process = Query()
#    db.search(Process.img == "img")
#    db.update({'state': "finished"}, Process.img == "img")
#    print(f"Analysis {param1} task finished.")
    ui.notify("Report saved")
