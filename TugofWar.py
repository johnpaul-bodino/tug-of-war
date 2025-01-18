import tkinter as tk
from WidgetComponents import LabelWidget, ButtonWidget, CompositeWidget, PhotoWidget
import threading


class Player:
    def __init__(self, name, initial_position):
        self.name = name
        self.position = initial_position
        self.pulls = 0  # Tracks number of pulls by the player

#------------------------------------------------------------------------------------------------------------------------------------

class GameField:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center = width / 2
        self.rope_length = 140
        self.pull_distance = self.rope_length * 0.05 #pull distance kada tap is 5%
        self.player1 = Player("Player 1", self.center - self.rope_length / 2)
        self.player2 = Player("Player 2", self.center + self.rope_length / 2)
        self.game_over = False  
        self.lock = threading.Lock()

    def update_positions(self):
        # Update player positions based on of the number of pulls(tap ng player)
        with self.lock:
            player1_pulls = self.player1.pulls
            player2_pulls = self.player2.pulls

        
        # Adjusting Player 1's position it when pull
        
        if player1_pulls > 0:
            with self.lock:
                self.player1.position = max(self.player1.position - self.pull_distance, 0)
                if self.player2.position > self.center:
                    self.player2.position -= self.pull_distance
                self.player1.pulls = 0

        # Adjusting Player 2's position it when pull
        if player2_pulls > 0:
            with self.lock:
                self.player2.position = min(self.player2.position + self.pull_distance, self.width)
                if self.player1.position < self.center:
                    self.player1.position += self.pull_distance
                self.player2.pulls = 0

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

class PlayScreen(tk.Canvas):
    def __init__(self, master, switch_frame, main_screen):
        super().__init__(master)
        self.switch_frame = switch_frame
        self.main_screen = main_screen
        self.composite = CompositeWidget()
        self.configure(bg='blue')
        self.display()
        self.game_field = GameField(900, 1000)
        self.winner_label = tk.Label(self, text="", font=("Arial", 18))
        self.winner_label.pack()
        self.player1_percentage_label = tk.Label(self, text="Player 1: 0.00%", font=("Arial", 18), bg="light green")
        self.player1_percentage_label.pack()
        self.player2_percentage_label = tk.Label(self, text="Player 2: 0.00%", font=("Arial", 18), bg= "light green")
        self.player2_percentage_label.pack()

        self.player1_img = tk.PhotoImage(file="pictures/player1.gif")
        self.player2_img = tk.PhotoImage(file="pictures/player2.gif")
       

        master.bind("<KeyPress>", self.handle_key_press)

    def start_game(self):
        self.input_enabled = True
        threading.Thread(target=self.update_game_logic, daemon=True).start()
        threading.Thread(target=self.update_gui, daemon=True).start()

    def process_keypress(self, player):
        with self.game_field.lock:
            player.pulls += 1

    def handle_key_press(self, event):
        if self.input_enabled and not self.game_field.game_over:
            if event.char == 'a':  # Player 1 key
                threading.Thread(target=self.process_keypress, args=(self.game_field.player1,), daemon=True).start()
                print("Player 1 key pressed")
            elif event.char == 'l':  # Player 2 key
                threading.Thread(target=self.process_keypress, args=(self.game_field.player2,), daemon=True).start()
                print("Player 2 key pressed")

    def display(self):
        background_image = PhotoWidget(self, "pictures/tug_location.png", width=900, height=700)
        self.composite.add(background_image)
        self.composite.display()


    def draw(self):
        # Draw the centerline, players, and rope
        self.delete("objects")
        self.create_line(self.game_field.center, 0, self.game_field.center, self.game_field.height,
                         width=2, fill="green", dash=(4, 4))
        self.create_line(self.game_field.player1.position, self.game_field.height / 2,
                         self.game_field.player2.position, self.game_field.height / 2, width=5, fill="brown", tags="objects")
        self.create_image(self.game_field.player1.position, self.game_field.height / 2,
                          image=self.player1_img, tags="objects")
        self.create_image(self.game_field.player2.position, self.game_field.height / 2,
                          image=self.player2_img, tags="objects")

    
    def update_winner(self):
        while not self.game_field.game_over:
            if self.game_field.player1.position >= self.game_field.center:
                self.winner_label.config(text="Player 2 Wins!", fg="green")
                self.game_field.game_over = True
                print("Player 2 Wins!")
                return True
            elif self.game_field.player2.position <= self.game_field.center:
                self.winner_label.config(text="Player 1 Wins!", fg="red")
                self.game_field.game_over = True
                print("Player 1 Wins!")
                return True
            return False

    def update_game_logic(self):
        # Update the game logic
        self.game_field.update_positions()
        player1_distance = self.game_field.center - self.game_field.player1.position
        player2_distance = self.game_field.player2.position - self.game_field.center
        total_distance = self.game_field.rope_length
        player1_percentage = (player1_distance / total_distance) * 100
        player2_percentage = (player2_distance / total_distance) * 100
        self.player1_percentage_label.config(text=f"Player 1: {player1_percentage:.2f}%")
        self.player2_percentage_label.config(text=f"Player 2: {player2_percentage:.2f}%")
        if not self.update_winner():
            self.after(100, self.update_game_logic)


    def update_gui(self):
        # The updated GUI will reflect the game state
        self.draw()
        if not self.update_winner():
            self.after(100, self.update_gui)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class TugOfWar(tk.Tk):
    def __init__(self):
        super().__init__()
        self.composite = CompositeWidget()
        self.__configure_window()
        self.run_window()

    def __configure_window(self):
        self.title('Tug Of War')
        self.configure(bg='skyblue')
        window_width = 900
        window_height = 700
        x_coordinate = (self.winfo_screenwidth() - window_width) // 2
        y_coordinate = 0
        self.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        self.main_screen()

    def main_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        main_canvas = tk.Canvas(self, width=900, height=700)
        backround_image = PhotoWidget(main_canvas, "pictures/main_screen.png", width=900, height=700)
        tug = LabelWidget(main_canvas, "TUG OF WAR", ('Pixelmax', 70), 0, x=450, y=90)
        start_button = ButtonWidget(main_canvas, "START", ('Pixelmax'), self.show_play_screen, 2, 30, x=280, y=300)
        exit_button = ButtonWidget(main_canvas, "EXIT", ('Pixelmax'), self.destroy, 2, 30, x=280, y=375)

        self.composite = CompositeWidget()
        self.composite.add(backround_image)
        self.composite.add(tug)
        self.composite.add(start_button)
        self.composite.add(exit_button)
        self.composite.display()


    def show_play_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.play_screen = PlayScreen(self, None, self.main_screen)
        self.play_screen.pack(fill=tk.BOTH, expand=True)
        self.play_screen.start_game()  


    def run_window(self):
        self.mainloop()


if __name__ == "__main__":
    TugOfWar()    

