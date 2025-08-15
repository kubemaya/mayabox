import time
import os
import cv2
import numpy as np
from tinydb import TinyDB
from nicegui import ui
from multiprocessing import Queue
import json

# Utility functions from utils module
def resize_image(image, width, height):
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)

def hex_to_bgr(hex_color):
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])

def bgr_to_hsv(bgr_color):
    bgr_array = np.uint8([[bgr_color]])
    hsv_color = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2HSV)[0][0]
    return hsv_color

def hex_to_hsv(hex_color):
    bgr_color = hex_to_bgr(hex_color)
    hsv_color = bgr_to_hsv(bgr_color)
    return hsv_color

def generate_color_range(hex_color, hue_offset=10, saturation_offset=50, value_offset=50):
    base_hsv = hex_to_hsv(hex_color)
    lower_bound = np.array([
        max(0, base_hsv[0] - hue_offset), 
        max(0, base_hsv[1] - saturation_offset),
        max(0, base_hsv[2] - value_offset)
    ], dtype=np.uint8)
    
    upper_bound = np.array([
        min(179, base_hsv[0] + hue_offset),
        min(255, base_hsv[1] + saturation_offset),
        min(255, base_hsv[2] + value_offset)
    ], dtype=np.uint8)
    
    return lower_bound, upper_bound

def filter_contours_by_aspect_ratio(contours, min_ratio=0.2, max_ratio=4.0, min_area=100, max_area=20000):
    filtered_contours = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h if h != 0 else 0
        area = cv2.contourArea(contour)
        if min_ratio <= aspect_ratio <= max_ratio and min_area <= area <= max_area:
            filtered_contours.append(contour)
    return filtered_contours

def save_image(output_folder, filename, image):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    cv2.imwrite(os.path.join(output_folder, filename), image)

def get_reports():
    db = TinyDB('reports.json')
    data = db.all()
    print(data)
    fdata = []
    for exp in data:
        try:
            # Handle both old field names and new descriptive names for backward compatibility
            result = exp["result"]
            fdata.append({
                "latitude":exp["latitude"],
                "longitude":exp["longitude"],
                "image_source":exp["image_source"],
                "output_image":result.get("output_image", ""),
                "objects_detected":result.get("objects_detected", result.get("field1", "")),
                "color_analyzed":result.get("color_analyzed", result.get("field2", "")),
                "contour_filtering":result.get("contour_filtering", result.get("field3", "")),
            })
        except:
            fdata.append({
                "latitude":exp["latitude"],
                "longitude":exp["longitude"],
                "image_source":exp["image_source"],
                "output_image":"",
                "objects_detected":"",
                "color_analyzed":"",
                "contour_filtering":"",
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
        print(f"Error: The file '{file}' was not found.")
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
    try:
        # Get analysis data
        data = get_analysis()
        if not data:
            return 'Error: No analysis data found'
        
        image_path = data.get("image_source")
        color_to_detect = data.get("color_input", "#A98876")  # Default color if not provided
        
        if not image_path or not os.path.exists(image_path):
            return 'Error: Image file not found'
        
        steps = 8
        step = 1
        q.put_nowait(step / steps)

        # Check if results folder exists
        if not os.path.exists('./results'):
            os.makedirs('./results')
        
        # Create output folder for results
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        output_folder = f'./results/{image_name}/'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Step 1: Read and validate image
        image = cv2.imread(image_path)
        if image is None:
            return f'Error: Could not load image from {image_path}'
        
        step = 2
        q.put_nowait(step / steps)
        
        # Step 2: Convert to HSV and resize
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        save_image(output_folder, 'hsv.png', hsv_image)
        
        
        step = 3
        q.put_nowait(step / steps)
        
        # Step 3: Generate color mask
        lower_bound, upper_bound = generate_color_range(color_to_detect, hue_offset=5, saturation_offset=25, value_offset=25)
        mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        save_image(output_folder, 'mask.png', mask)
        
        step = 4
        q.put_nowait(step / steps)
        
        # Step 4: Apply morphological operations
        kernel = np.ones((5, 5), np.uint8)
        
        # Dilation
        mask_dilated = cv2.dilate(mask, kernel, iterations=1)
        save_image(output_folder, 'dilated.png', mask_dilated)
        
        step = 5
        q.put_nowait(step / steps)
        
        # Erosion
        mask_eroded = cv2.erode(mask_dilated, kernel, iterations=1)
        save_image(output_folder, 'eroded.png', mask_eroded)
        
        # Gaussian smoothing
        mask_smoothed = cv2.GaussianBlur(mask_eroded, (5, 5), 0)
        save_image(output_folder, 'smooth.png', mask_smoothed)

        sobel_x = cv2.Sobel(mask_smoothed, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(mask_smoothed, cv2.CV_64F, 0, 1, ksize=3)
        sobel_combined = cv2.magnitude(sobel_x, sobel_y)
        sobel_combined = np.uint8(np.clip(sobel_combined, 0, 255))
        save_image(output_folder, 'sobel_edges.png', sobel_combined)

        # Laplacian edge detection
        laplacian = cv2.Laplacian(mask_smoothed, cv2.CV_64F)
        laplacian = np.uint8(np.clip(np.absolute(laplacian), 0, 255))
        save_image(output_folder, 'laplacian_edges.png', laplacian)

        edge_mask = laplacian
                
        step = 6
        q.put_nowait(step / steps)
        
        # Step 5: Find and filter contours
        contours, _ = cv2.findContours(edge_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = filter_contours_by_aspect_ratio(contours)
        
        step = 7
        q.put_nowait(step / steps)
        
        # Step 6: Count detected objects and create result image
        num_figures = len(filtered_contours)
        
        # Draw contours on original image
        contour_image = image.copy()
        cv2.drawContours(contour_image, filtered_contours, -1, (0, 255, 0), 1)
        save_image(output_folder, 'contours.png', contour_image)
        
        # Add text with count - create a copy for the final result
        final_image = contour_image.copy()
        
        # Add background rectangle for better text visibility
        text = f'Fragments detected: {num_figures}'
        font = cv2.FONT_HERSHEY_COMPLEX
        font_scale = 0.8
        thickness = 2
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_width, text_height = text_size
        
        # Get text size to create background rectangle
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Draw background rectangle
        cv2.rectangle(final_image, (5, 5), (text_width + 15, text_height + baseline + 15), (0, 0, 0), -1)
        
        # Draw text on top of rectangle
        cv2.putText(final_image, text, (10, text_height + 10), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
        
        # Save final result with timestamp to avoid caching issues
        timestamp = str(int(time.time()))
        final_result_filename = f'final_result_{timestamp}.png'
        final_result_path = os.path.join(output_folder, final_result_filename)
        save_image(output_folder, final_result_filename, final_image)
        
        step = 8
        q.put_nowait(step / steps)
        
        # Step 7: Prepare results
        result = {
            "output_image": final_result_path,
            "objects_detected": f"{num_figures}",
            "color_analyzed": f"{color_to_detect}",
            "contour_filtering": f"{len(contours)} -> {num_figures}"
        }
        
        # Update analysis.json with results
        store_analysis(data["latitude"], data["longitude"], data["color_input"], data["image_source"], result)
        
        print(f'Analysis completed - Objects detected: {num_figures}')
        return 'Done!'
        
    except Exception as e:
        print(f'Error during analysis: {str(e)}')
        return f'Error: {str(e)}'

def save_report():
    data = get_analysis()
    db = TinyDB('reports.json')
    db.insert(data)
#    Process = Query()
#    db.search(Process.img == "img")
#    db.update({'state': "finished"}, Process.img == "img")
#    print(f"Analysis {param1} task finished.")
    ui.notify("Report saved")
