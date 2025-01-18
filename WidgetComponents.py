from abc import ABC, abstractmethod
from PIL import Image, ImageTk
import tkinter as tk
import time

class WidgetComponent(ABC):
    @abstractmethod
    def display(self):
        pass

# Concrete Components
class LabelWidget(WidgetComponent):
    def __init__(self, master, text, font, pady, fg="black", **kwargs):
        self.text = text
        self.font = font
        self.pady = pady
        self.fg = fg
        self.arg_place = kwargs
        self.canvas = master

    def display(self):
        x = self.arg_place.get('x', 0)
        y = self.arg_place.get('y', 0)
        self.canvas.create_text(x, y, text=self.text, font=self.font, fill=self.fg)

class PhotoWidget(WidgetComponent):
    def __init__(self, master, photoImg, width=None, height=None, **kwargs):
        self.image = Image.open(photoImg) 
        self.canvas = master

        if width and height:
            self.image = self.image.resize((width, height))
        self.photo = ImageTk.PhotoImage(self.image)

        self.arg_place = kwargs

    def display(self):
        self.canvas.pack()
        self.canvas.place(**self.arg_place)
        self.canvas.create_image(0, 0, image=self.photo, anchor='nw')

class ButtonWidget(WidgetComponent):
  
    def __init__(self, master, text, font, command, height=None, width=None, relief=None, **kwargs):
        
        self.button = tk.Button(master, text=text, font=font, bg='gainsboro', command=command, height=height, width=width, relief=relief)

        self.button.bind("<Enter>", self.change_color_on_enter)  
        self.button.bind("<Leave>", self.reset_color_on_leave)  
        self.arg_place = kwargs

    def change_color_on_enter(self, hover):
        self.button.config(bg="skyblue3")

    def reset_color_on_leave(self, hover):
        self.button.config(bg="gainsboro")

    def display(self):
        self.button.pack(pady=15)
        self.button.place(self.arg_place)

class CompositeWidget(WidgetComponent):
    def __init__(self):
        self.children = []

    def add(self, child):
        self.children.append(child)

    def display(self):
        for child in self.children:
            child.display()