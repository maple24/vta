import cv2
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import json
from loguru import logger

class WebCamController:
    def __init__(self, camera_index=0):
        self.camera = cv2.VideoCapture(camera_index)
        self.root = tk.Tk()
        self.root.title("WebCamera Controller")

        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()

        self.start_button = tk.Button(self.button_frame, text="Start Region Selection", command=self.start_region_selection)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_button = tk.Button(self.button_frame, text="Save Region", command=self.save_selected_region, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete Region", command=self.delete_selected_region, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.exit_button = tk.Button(self.button_frame, text="Exit Region Selection", command=self.exit_region_selection, state=tk.DISABLED)
        self.exit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.coordinates_label = tk.Label(self.button_frame, text="Mouse Coordinates: ")
        self.coordinates_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.region_frame = tk.Frame(self.root)
        self.region_frame.pack(pady=10)

        self.region_name_label = tk.Label(self.region_frame, text="Region Name:")
        self.region_name_label.pack(side=tk.LEFT)

        self.region_name_entry = tk.Entry(self.region_frame, width=30)
        self.region_name_entry.pack(side=tk.LEFT)

        self.region_table_frame = tk.Frame(self.root)
        self.region_table_frame.pack(pady=10)

        self.region_table = ttk.Treeview(self.region_table_frame, columns=("name", "start_x", "start_y", "end_x", "end_y"), show="headings")
        self.region_table.heading("name", text="Name")
        self.region_table.heading("start_x", text="Start X")
        self.region_table.heading("start_y", text="Start Y")
        self.region_table.heading("end_x", text="End X")
        self.region_table.heading("end_y", text="End Y")
        self.region_table.pack(side=tk.LEFT)

        self.region_table_scrollbar = ttk.Scrollbar(self.region_table_frame, orient=tk.VERTICAL, command=self.region_table.yview)
        self.region_table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.region_table.configure(yscrollcommand=self.region_table_scrollbar.set)

        self.selection_in_progress = False
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.selected_region = None
        self.regions = {}

        self.load_saved_regions()
        self.update_region_table()
        self.update_video_feed()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)   
        self.region_table.bind("<<TreeviewSelect>>", self.on_table_select)

        self.video_label.bind('<Motion>', self.update_coordinates)
        self.root.mainloop()
        
    def update_coordinates(self, event):
        coordinates_text = "Mouse Coordinates: ({}, {})".format(event.x, event.y)
        self.coordinates_label.config(text=coordinates_text)

    def update_video_feed(self):
        ret, frame = self.camera.read()
        if ret:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Draw bounding boxes for all saved regions
            for region_name, region_data in self.regions.items():
                start_x = region_data['start_x']
                start_y = region_data['start_y']
                end_x = region_data['end_x']
                end_y = region_data['end_y']
                color = (0, 255, 0)  # Default color (green)
                if region_name == self.selected_region:
                    color = (255, 0, 0)  # Selected color (red)
                cv2.rectangle(img, (start_x, start_y), (end_x, end_y), color, 2)
                label = region_name
                cv2.putText(img, label, (start_x, start_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # Draw bounding box overlay if a selection is in progress
            if self.start_x is not None and self.start_y is not None and self.end_x is not None and self.end_y is not None:
                cv2.rectangle(img, (self.start_x, self.start_y), (self.end_x, self.end_y), (0, 255, 0), 2)

            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)
            self.video_label.img_tk = img_tk
            self.video_label.config(image=img_tk)
        self.video_label.after(30, self.update_video_feed)

    def start_region_selection(self):
        # Reset the coordinates for the next selection
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.region_name_entry.delete(0, tk.END)
        
        self.selection_in_progress = True
        self.start_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.NORMAL)
        self.region_name_entry.config(state=tk.NORMAL)
        self.region_name_entry.focus_set()
        self.video_label.bind("<Button-1>", self.on_mouse_click)
        self.video_label.bind("<B1-Motion>", self.on_mouse_drag)
        # self.video_label.bind("<ButtonRelease-1>", self.on_mouse_release)

    def on_mouse_click(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event):
        self.end_x = event.x
        self.end_y = event.y

    # def on_mouse_release(self, event):
    #     if self.selection_in_progress:
    #         self.video_label.after(100, self.unbind_mouse_events)

    # def unbind_mouse_events(self):
    #     self.video_label.unbind("<Button-1>")
    #     self.video_label.unbind("<B1-Motion>")
    #     self.video_label.unbind("<ButtonRelease-1>")
    #     self.selection_in_progress = False

    def save_selected_region(self):
        region_name = self.region_name_entry.get()
        if region_name:
            if self.start_x is not None and self.start_y is not None and self.end_x is not None and self.end_y is not None:
                selected_region = {
                    'start_x': self.start_x,
                    'start_y': self.start_y,
                    'end_x': self.end_x,
                    'end_y': self.end_y
                }
                self.regions[region_name] = selected_region
                logger.success("Region '{}' saved: {}".format(region_name, selected_region))

                # Update the region table
                self.update_region_table()

                # Rebind the mouse events for next selection
                self.start_region_selection()
            else:
                logger.warning("No region selected!")
                self.start_region_selection()
        else:
            logger.warning("No region name given!")
            self.start_region_selection()

    def delete_selected_region(self):
        if self.selected_region:
            del self.regions[self.selected_region]
            self.update_region_table()
            logger.success("Region '{}' deleted.".format(self.selected_region))

    def exit_region_selection(self):
        self.selection_in_progress = False
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.selected_region = None
        self.start_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.DISABLED)
        self.region_name_entry.delete(0, tk.END)
        self.video_label.unbind("<Button-1>")
        self.video_label.unbind("<B1-Motion>")
        self.video_label.unbind("<ButtonRelease-1>")

    def exit_application(self):
        self.save_regions_to_file()
        self.root.destroy()

    def update_region_table(self):
        # Clear existing rows
        self.region_table.delete(*self.region_table.get_children())

        # Add regions to the table
        for region_name, region_data in self.regions.items():
            start_x = region_data['start_x']
            start_y = region_data['start_y']
            end_x = region_data['end_x']
            end_y = region_data['end_y']
            self.region_table.insert("", tk.END, values=(region_name, start_x, start_y, end_x, end_y))

    def load_saved_regions(self):
        try:
            with open("regions.json", "r") as json_file:
                self.regions = json.load(json_file)
        except FileNotFoundError:
            self.regions = {}

    def save_regions_to_file(self):
        with open("regions.json", "w") as json_file:
            json.dump(self.regions, json_file, indent=4)

    def on_table_select(self, event):
        selected_item = self.region_table.selection()
        if selected_item:
            region_name = self.region_table.item(selected_item, "values")[0]
            if region_name == self.selected_region:
                self.selected_region = None
                self.delete_button.config(state=tk.DISABLED)
            else:
                self.selected_region = region_name
                self.delete_button.config(state=tk.NORMAL)

app = WebCamController()
