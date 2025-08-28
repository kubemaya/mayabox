import gradio as gr
from PIL import Image
import os
import time
import json
from analyze import *

def get_pixel_color(img, evt: gr.SelectData):
    if img is None:
        return "No image loaded.", "#FFFFFF", ""
    
    x, y = evt.index
    pil_img = Image.fromarray(img)
    pixel_color = pil_img.getpixel((x, y))
    rgb_str = f"Clicked at ({x}, {y}). Pixel color: RGB{pixel_color}"
    hex_color = '#%02x%02x%02x' % pixel_color[:3]
    return rgb_str, hex_color, ""

def show_gps():
    return "Waiting for browser location..."

def save_experiment(img, gps):
    if img is None or not gps or gps in ["Waiting for browser location...", "Location access denied.", "Geolocation not supported."]:
        return "", "Image or GPS not available. Please take a picture and get GPS first."
    
    os.makedirs("./files", exist_ok=True)
    timestamp = str(int(time.time()))[-5:]
    filename = f"pic-{timestamp}.png"
    filepath = os.path.join("./files", filename)
    pil_img = Image.fromarray(img)
    pil_img.save(filepath)
    experiment_data = {
        "picture": filename,
        "gps": gps
    }
    json_path = os.path.join("./files", "experiment.json")
    with open(json_path, "w") as f:
        json.dump(experiment_data, f, indent=2)
    return filename, f"Saved: {filename} with GPS {gps}"

def analyze_picture(filename, color,img,gps):
    if img is None or not gps or gps in ["Waiting for browser location...", "Location access denied.", "Geolocation not supported."]:
        return "Image or GPS not available. Please take a picture and get GPS first."

    os.makedirs("./files", exist_ok=True)
    timestamp = str(int(time.time()))[-5:]
    filename = f"pic-{timestamp}.png"
    filepath = os.path.join("./files", filename)
    pil_img = Image.fromarray(img)
    pil_img.save(filepath)

    gps_parts = gps.split(',')
    data = {
        "latitude": gps_parts[0].strip(),
        "longitude": gps_parts[1].strip(),
        "color_input": color,
        "image_source": "./files/"+filename,
    }
    result = analyze(data)
    print(data,result)
    #data["result"] = result
    #result = {
    #    "picture": filename,
    #    "color": color,
    #    "analysis": "This is a sample analysis.",
    #    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    #    "gps": gps
    #}

    for field in result:
        data[field] = result[field]
    print(data)



    print(data["output_image"])
    data["output_image"] = data["output_image"].replace("./","")
    print(data["output_image"])

    txt_data = ""
    for field in data:
        txt_data += f"<li><b>{field}:</b> {data[field]}</li>\n"

    output_image = data.get("output_image", "./files/"+filename)

    html = f"""
    <h3>Analysis Result</h3>
    <ul>
        {txt_data}
    </ul>
    """
    return html,output_image

with gr.Blocks(css="footer{display:none !important}") as kamidar:
    with gr.Row():
        image_input = gr.Image(type="numpy", label="Click on the image")
    with gr.Row():
        color_output = gr.Markdown("Click a pixel to see its color.")
        color_picker = gr.ColorPicker(label="Picked Color", value="#FFFFFF")
    with gr.Row():
        gps_button = gr.Button("Get GPS Location")
        gps_output = gr.Textbox(label="GPS Coordinates")
    with gr.Row():
        save_button = gr.Button("Save Experiment")
        save_output = gr.Markdown("")
    with gr.Row():
        analyze_button = gr.Button("Analyze")
    with gr.Row():
        image_output = gr.Image(type="filepath", label="Output Image")
    with gr.Row():
        analyze_output = gr.HTML("")

    last_filename = gr.Textbox(visible=False)
    selected_color = gr.Textbox(visible=False)

    image_input.select(
        get_pixel_color,
        inputs=[image_input],
        outputs=[color_output, color_picker, last_filename]
    )

    gps_button.click(
        None,
        None,
        [gps_output],
        js="""
        async () => {
            if (navigator.geolocation) {
                return await new Promise((resolve) => {
                    navigator.geolocation.getCurrentPosition(
                        (pos) => {
                            const coords = pos.coords.latitude + "," + pos.coords.longitude;
                            resolve(coords);
                        },
                        (err) => {
                            resolve("Location access denied.");
                        }
                    );
                });
            } else {
                return "Geolocation not supported.";
            }
        }
        """
    )

    save_button.click(
        save_experiment,
        inputs=[image_input, gps_output],
        outputs=[last_filename, save_output]
    )

    analyze_button.click(
        analyze_picture,
        inputs=[last_filename, color_picker,image_input,gps_output],
        outputs=[analyze_output,image_output]
    )

kamidar.launch(server_port=8080,server_name="0.0.0.0")