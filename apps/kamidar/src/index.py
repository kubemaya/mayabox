from nicegui import run,ui, events
from multiprocessing import Manager
#import base64
from PIL import Image
import time
from analyze import *
import os
from random import randint


ii = None
color_input = None
gps = None
spinner = None
color_input = None
label_color = None

@ui.refreshable
def show_history():
    columns = [
        {'name': 'latitude', 'label': 'Latitude', 'field': 'latitude'},
        {'name': 'longitude', 'label': 'Longitude', 'field': 'longitude'},
        {'name': 'image_source', 'label': 'Image Source', 'field': 'image_source'},
        {'name': 'output_image', 'label': 'Output Image', 'field': 'output_image'},
        {'name': 'objects_detected', 'label': 'Objects Detected', 'field': 'objects_detected'},
        {'name': 'color_analyzed', 'label': 'Color Analyzed', 'field': 'color_analyzed'},
        {'name': 'contour_filtering', 'label': 'Contour Filtering', 'field': 'contour_filtering'},
    ]
    rows = get_reports()
    table = ui.table(columns=columns, rows=rows, row_key='image_source').classes('w-full')

@ui.refreshable
def show_report():
    ui.label('Analysis Report')
    data = get_analysis()
    ui.label("Original image")
    try:
        img_original = ui.image(data["image_source"]).classes('w-64')
    except:
        print("Ignore image error when first time running")
    ui.label("Detected objects")
    try:
        img_analysis = ui.image(data["result"]["output_image"]).classes('w-64')
        report = ui.log(max_lines=10).classes('w-full')
        report.push("Report Summary")
        report.push("---------------")
        
        # Handle both old field names and new descriptive names for backward compatibility
        result = data["result"]
        objects_detected = result.get("objects_detected", result.get("field1", "N/A"))
        color_analyzed = result.get("color_analyzed", result.get("field2", "N/A"))
        contour_filtering = result.get("contour_filtering", result.get("field3", "N/A"))
        
        report.push("Objects Detected: " + objects_detected)
        report.push("Color Analyzed: " + color_analyzed)
        report.push("Contour Filtering: " + contour_filtering)
        ui.button('Save Report',on_click=lambda: save_report())
    except:
        print("Error when loading history")


@ui.page('/')
async def main_page():


    async def start_computation(progressbar,va):
        #progressbar.visible = True
        result = await run.cpu_bound(analyze, queue)
        ui.notify(result)
        va.enable()
        #progressbar.visible = False

    async def set_analysis(panels,tab_analyze):
        print(color_input.value)
        print(ii.source)
        gps_pos = gps.value.split(",")
        
        # Check if GPS coordinates are valid
        if len(gps_pos) < 2 or gps.value == "Pending":
            ui.notify("Please wait for GPS coordinates to load or enter them manually", type="warning")
            return
            
        try:
            latitude = float(gps_pos[0].strip())
            longitude = float(gps_pos[1].strip())
        except (ValueError, IndexError):
            ui.notify("Invalid GPS coordinates format. Please use: latitude,longitude", type="error")
            return
            
        # Check if image is loaded
        if not ii.source or ii.source == "None":
            ui.notify("Please upload an image first", type="warning")
            return
            
        # Check if color is selected
        if not color_input.value:
            ui.notify("Please select a color from the image", type="warning")
            return
            
        store_analysis(latitude, longitude, color_input.value, ii.source, {})
        panels.set_value(tab_analyze)

        #progressbar = ui.linear_progress(value=0).props('instant-feedback')
        progressbar.value=0
        #progressbar.visible = False
        #va = ui.button('View Report', on_click=lambda: view_report())
        va.disable()
        #run_analysis()

    async def handle_upload(e: events.UploadEventArguments):
        """Handles the uploaded image and displays it."""
        #global spinner
        gps.set_value("Pending")
        spinner.visible = True
        ui.notify("Loading GPS coordinate",position="top")

        response = await ui.run_javascript('''
            return await new Promise((resolve, reject) => {
                if (!navigator.geolocation) {
                    reject(new Error('Geolocation is not supported by your browser'));
                } else {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            resolve({
                                latitude: position.coords.latitude,
                                longitude: position.coords.longitude,
                            });
                        },
                        () => {
                            reject(new Error('Unable to retrieve your location'));
                        }
                    );
                }
            });
        ''', timeout=30.0)
        #ui.notify(f'Your location is {response["latitude"]}, {response["longitude"]}')
        latitude = response["latitude"]
        longitude = response["longitude"]
        print(f'Your location is {latitude}, {longitude}')
        gps.set_value(f"{latitude},{longitude}")

        name = "pics/img-"+str(int(time.time()))[5:]+".jpg"
        if e.content:
            data = e.content.read()
            with open(name, "wb") as binary_file:
                binary_file.write(data)
            #b64_bytes = base64.b64encode(data)
            #image_data = f'data:{e.type};base64,{b64_bytes.decode()}'
            #ui.image(image_data).classes('w-64 h-64')
            ii.set_source(name)
            spinner.visible = False
            ui.notify("Loaded GPS coordinate",position="top")
        else:
            ui.notify("No file uploaded.")
    def delete_all():
        os.system("rm pics/*;rm reports.json")
        ui.notify("Images & History deleted, Please refresh the page",position="top")
    def get_pixel(x_coord,y_coord):
        print(ii.source)
        try:
            img_tmp = Image.open(ii.source) # Replace with your image file
            pixels = img_tmp.load()
            print("Pixels loaded")
        except FileNotFoundError:
            print("Error: Image file not found. Please check the path.")
            exit()        
        print(pixels)
        pixel_color = pixels[x_coord, y_coord]
        #print(pixel_color[0],pixel_color[1],pixel_color[2])
        r=pixel_color[0]
        g=pixel_color[1]
        b=pixel_color[2]
        print(f"\033[38;2;{r};{g};{b}mHello!\033[0m")
        #ui.notify(f"The color of the pixel at ({x_coord}, {y_coord}) is: {pixel_color}")
        color_input.set_value('#%02x%02x%02x' % (r, g, b))
        lc = color_input.value
        label_color.style(f'color:{lc}')

    def handle_image_click(e: events.MouseEventArguments):
        get_pixel(e.image_x,e.image_y)

    def view_report():
        panels.set_value(tab_report)
        show_report.refresh()
    def update_image_color(color):
        #color_input.value = color
        label_color.style(f'color:{color}')

    queue = Manager().Queue()

    with ui.tabs() as tabs:
        tab_capture = ui.tab('capture', label='Capture', icon='photo_camera')
        tab_analyze = ui.tab('analyze', label='Analyze', icon='image_search')
        tab_report = ui.tab('report', label='Report', icon='article')
        tab_history = ui.tab('history', label='History', icon='history')
        tab_delete = ui.tab('clean', label='Clean', icon='delete')
        #tab_locations = ui.tab('locations', label='Locations', icon='location_searching')
        #tab_export = ui.tab('export', label='Export', icon='ios_share')

    with ui.tab_panels(tabs, value=tab_capture).classes('w-full') as panels:
        with ui.tab_panel(tab_capture):
            ui.label('Take a picture with your phone')

            ui.upload(on_upload=handle_upload, auto_upload=True) \
                .props('accept="image/*" capture="camera"') \
                .classes('w-full')
            ui.label('Pick a color from the picture')
            image_source = None 
            ii = ui.interactive_image(image_source, on_mouse=handle_image_click,cross=True).classes('w-64')
            
                    
        #    color_input = ui.color_input(label='Picked Color', on_change=lambda e: update_image_color(e.value))
            color_input = ui.color_input(label='Picked Color', on_change=lambda e: update_image_color(e.value))
            label_color = ui.label('Selected color looks like this')
            with ui.row():
                gps = ui.input(label='GPS Coordinate', placeholder='GPS Coordinate',value="Pending")
                spinner = ui.spinner(size='lg')
                spinner.visible = False
            ui.button('Save to Analyze', on_click=lambda: set_analysis(panels,tab_analyze))

        with ui.tab_panel(tab_analyze):
            ui.label('Run Image Analysis')
            ui.timer(0.1, callback=lambda: progressbar.set_value(queue.get() if not queue.empty() else progressbar.value))
            # Create the UI
            progressbar = ui.linear_progress(value=0,show_value=False).props('instant-feedback')
            #progressbar.visible = False
            va = ui.button('View Report', on_click=lambda: view_report())
            va.disable()
            ui.button('Analyze', on_click=lambda: start_computation(progressbar,va))

        with ui.tab_panel(tab_report):
            show_report()

        with ui.tab_panel(tab_history):
            ui.label('Reports history')
            show_history()

        with ui.tab_panel(tab_delete):
            ui.label('Delete analysis')
            ui.button('Delete All',on_click=lambda: delete_all())            
        #with ui.tab_panel(tab_locations):
        #    ui.label('Near Locations')
        #with ui.tab_panel(tab_export):
        #    ui.label('Export to the cloud')
        #    ui.button('Export reports')            


ui.timer(5.0, show_history.refresh)

#Use this line instead to generate the container
#ui.run(host='0.0.0.0', port=8080, title='KAMIDAR')
os.environ["UVICORN_WORKERS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
# ui.run(
# reload=False,
# native=False,
# uvicorn_logging_level='warning',
# show=False,  # prevents chromium injection
# port=8080,
# title='KAMIDAR')
ui.run(host='0.0.0.0', port=8081, title='KAMIDAR', \
ssl_keyfile='key.pem', \
ssl_certfile='cert.pem')
