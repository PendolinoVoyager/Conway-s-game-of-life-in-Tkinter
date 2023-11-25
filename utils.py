import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno
from settings import SETTINGS, UPDATE_SETTINGS
from time import sleep
import os
#Main window creation function for Conway's Game of Life
def create_main_window():
    #Main variables running the app
    bottom_right = [0, 0]
    top_left = [SETTINGS['GRID_SIZE'], SETTINGS['GRID_SIZE']]
    is_running = False
    grid_state = [[0 for _ in range(SETTINGS['GRID_SIZE'])] for _ in range(SETTINGS['GRID_SIZE'])]
#############################################3
#CANVAS MANIPULATION MODULE    
    #Makes the canvas in given canvas frame. Also binds mouse event. Necessary for remaking the grid after resizing.
    def make_canvas(canvas_frame: tk.Frame):
        canvas = tk.Canvas(canvas_frame, relief='groove', borderwidth=2, width=SETTINGS['GRID_SIZE']*SETTINGS['CELL_SIZE'], height=SETTINGS['GRID_SIZE']*SETTINGS['CELL_SIZE'])
        canvas.pack(pady=10, expand=True)
        canvas.bind('<Button-1>', canvas_click)
        canvas.bind('<Button-4>', lambda event: [canvas_scroll(event), stop_simulation()])
        canvas.bind('<Button-5>', lambda event: [canvas_scroll(event), stop_simulation()])
        canvas.bind('<B1-Motion>', canvas_click)
        return canvas
    #Updates the canvas on grid size setting change.
    def update_canvas_size(**actions):
        nonlocal grid_state, canvas, bottom_right
        for action in actions:
            if action == "increase":
                if SETTINGS['GRID_SIZE']*SETTINGS['CELL_SIZE'] < 620:
                    UPDATE_SETTINGS('GRID_SIZE', SETTINGS['GRID_SIZE']+1)
                else:
                    return
            elif action == "decrease":
                if SETTINGS['GRID_SIZE'] > 1:
                    UPDATE_SETTINGS('GRID_SIZE', SETTINGS['GRID_SIZE']-1)
                    bottom_right = [min(bottom_right[0], SETTINGS['GRID_SIZE']), min(bottom_right[1], SETTINGS['GRID_SIZE'])]
        canvas.destroy() 
        grid_state = get_new_grid_state(grid_state)
        canvas = make_canvas(canvas_frame)
        draw_grid(canvas)
        draw_all(canvas)
    #Returns an altered grid state if grid size has been changed
    def get_new_grid_state(grid_state):
        new_size = SETTINGS['GRID_SIZE']
        new_state = [[0 for _ in range(new_size)] for _ in range(new_size)]
        for i in range(min(new_size, len(grid_state))):
            for j in range(min(new_size, len(grid_state[i]))):
                new_state[i][j] = grid_state[i][j]            
        return new_state
    def kill_all_cells(canvas):
        nonlocal top_left, bottom_right, grid_state
        bottom_right = [0, 0]
        top_left = (SETTINGS['GRID_SIZE'], SETTINGS['GRID_SIZE'] - 1)
        grid_state = [[0 for _ in range(SETTINGS['GRID_SIZE'])] for _ in range(SETTINGS['GRID_SIZE'])]
        draw_grid(canvas)
    #Related to cell size combo - changes cell size and redraws the canvas
    def change_cell_size(var):
        size = int(var.get())
        nonlocal grid_state, canvas
        UPDATE_SETTINGS('CELL_SIZE', size)
        canvas.destroy()
        canvas = make_canvas(canvas_frame)
        draw_grid(canvas)
        draw_all(canvas)
    #Canvas scroll works on linux, mouse 3 may work on windows
    def canvas_scroll(event):
        nonlocal canvas
        if event.num == 4:
            UPDATE_SETTINGS("CELL_SIZE", SETTINGS['CELL_SIZE'] + 1)
        elif event.num == 5:
            UPDATE_SETTINGS("CELL_SIZE", SETTINGS['CELL_SIZE'] - 1)
        cell_size_combo.set(SETTINGS['CELL_SIZE'])
        canvas.destroy()
        canvas = make_canvas(canvas_frame)
        draw_grid(canvas)
        draw_all(canvas)
    #For expand grid button, changes grid size to fill according to cell size
    def expand_grid():
        grid_size = 630 // SETTINGS["CELL_SIZE"]
        UPDATE_SETTINGS('GRID_SIZE',  grid_size)
        update_canvas_size()
#######################################3
#SIMULATION MODULE
    #The function called when we simulate a step in the game
    def next_generation(canvas):
        nonlocal top_left, bottom_right
        top_left, bottom_right, changed_cells = get_next_grid()
        for cell in changed_cells:  
            grid_state[cell[0]][cell[1]] = 0 if grid_state[cell[0]][cell[1]] else 1
            draw_changed_cell(canvas, cell[0], cell[1])
    ''' Returns new corners and a list of changed cells to redraw, updates grid_state in loop'''
    def get_next_grid():
        nonlocal grid_state, top_left, bottom_right
        new_top_left = [SETTINGS['GRID_SIZE'], SETTINGS['GRID_SIZE']]
        new_bottom_right = [0, 0]
        changed_cells = [] 
        neighbor_counts = [[0 for _ in range(SETTINGS['GRID_SIZE'])] for _ in range(SETTINGS['GRID_SIZE'])]
        for i in range(max(top_left[0]-1, 0), min(bottom_right[0]+2, SETTINGS['GRID_SIZE'])):
            for j in range(max(top_left[1]-1, 0), min(bottom_right[1]+2, SETTINGS['GRID_SIZE'])):
                neighbor_counts[i][j] = count_alive_neighbours(i, j)
                print('nei ',neighbor_counts[i][j])
        for i in range(max(top_left[0]-1, 0), min(bottom_right[0]+2, SETTINGS['GRID_SIZE'])):
            for j in range(max(top_left[1]-1, 0), min(bottom_right[1]+2, SETTINGS['GRID_SIZE'])):
                new_state = judgment(i, j, neighbor_counts[i][j])
                if new_state != grid_state[i][j]:
                    changed_cells.append((i, j))
                    new_top_left = [min(new_top_left[0], i), min(new_top_left[1], j)]
                    new_bottom_right = [max(new_bottom_right[0], i), max(new_bottom_right[1], j)]
        print(top_left, bottom_right)
        print(new_top_left, new_bottom_right)
        return  new_top_left, new_bottom_right, changed_cells
    #Judges if a cell stays alive, comes back to life or dies
    def judgment(x, y, alive_neighbours):
        if not grid_state[x][y] and alive_neighbours in SETTINGS['CELLS_TO_COME_TO_LIFE']:
            return 1
        if grid_state[x][y] and alive_neighbours in SETTINGS['CELLS_TO_STAY_ALIVE']:
            return 1
        return 0

    def count_alive_neighbours(x, y):
        alive_neighbors = 0
        for i in range(max(0, x-1), min(SETTINGS['GRID_SIZE'], x+2)):
            for j in range(max(0, y-1), min(SETTINGS['GRID_SIZE'], y+2)):
                alive_neighbors += grid_state[i][j]
        if grid_state[x][y]:
            alive_neighbors -= 1
        return alive_neighbors
    #Sets the is_running variable to True and locks the buttons to stop the user from messing things up
    def start_simulation(): 
        nonlocal is_running 
        is_running = True
        start_simulation_button.configure(state='disabled')
        stop_simulation_button.configure(state='active')
        plus.configure(state='disabled')
        minus.configure(state='disabled')
        cell_size_combo.configure(state='disabled')
        settings_button.configure(state='disabled')
        expand_grid_button.configure(state='disabled')
        save_button.configure(state='disabled')
        run_simulation()
    #Opposite of start_simulation
    def stop_simulation():
        nonlocal is_running 
        is_running = False
        stop_simulation_button.configure(state='disabled')
        start_simulation_button.configure(state='active')
        cell_size_combo.configure(state='active')
        plus.configure(state='active')
        minus.configure(state='active')
        settings_button.configure(state='active')
        expand_grid_button.configure(state='active')
        save_button.configure(state='active')
    #Until we change is_running by clicking on stop simulation button, the function will be called each
    #refresh rate interval (or slower if the grid is too large)
    def run_simulation():
        nonlocal is_running
        if is_running: 
            next_generation(canvas)
            canvas.after(SETTINGS['REFRESH_RATE'], run_simulation)
#########################################
#DRAWING ON CANVAS MODULE
    #Draws an empty grid
    def draw_grid(canvas):
        for i in range(SETTINGS['GRID_SIZE']):
            for j in range(SETTINGS['GRID_SIZE']):
                x1 = j * SETTINGS['CELL_SIZE']
                y1 = i * SETTINGS['CELL_SIZE']
                x2 = x1 + SETTINGS['CELL_SIZE']
                y2 = y1 + SETTINGS['CELL_SIZE']
                canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline="gray")
    #Draws all cells. Important since top left and bottom right ignores the static cells
    def draw_all(canvas):
        nonlocal top_left, bottom_right, grid_state
        for i in range(SETTINGS['GRID_SIZE']):
            for j in range(SETTINGS['GRID_SIZE']):
                if grid_state[i][j]:
                    cell_size = SETTINGS['CELL_SIZE']
                    x1 = i * cell_size
                    y1 = j * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    canvas.create_rectangle(x1, y1, x2, y2, fill='black', outline='gray')
    #Colors a singular changed cell, used for next_generation and clicking on canvas
    def draw_changed_cell(canvas: tk.Canvas, x, y):
        cell_size = SETTINGS['CELL_SIZE']
        if x < SETTINGS['GRID_SIZE']*cell_size and y < SETTINGS['GRID_SIZE']*cell_size:
            x1 = x * cell_size
            y1 = y * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            if grid_state[x][y]:  
                cell_color = 'black' 
            else:
                cell_color = 'white'
            canvas.create_rectangle(x1, y1, x2, y2, fill=cell_color, outline='gray')
            
    def canvas_click(event):
        nonlocal top_left, bottom_right
        x, y = event.x, event.y
        if x < SETTINGS['GRID_SIZE']*SETTINGS['CELL_SIZE'] and y < SETTINGS['GRID_SIZE']*SETTINGS['CELL_SIZE']:
            x, y = x // SETTINGS['CELL_SIZE'], y // SETTINGS['CELL_SIZE']
            top_left = [min(top_left[0], x), min(top_left[1], y)]
            bottom_right = [max(bottom_right[0], x), max(bottom_right[1], y)]
            if event.type == '4': #event 4 is single click
                grid_state[x][y] = 0 if grid_state[x][y] else 1
                sleep(0.06) #prevents slight movement from immediately calling mouse drag event
            else:
                grid_state[x][y] = 1
            draw_changed_cell(canvas, x, y)
##############################################
#SETTINGS MODULE
    def make_settings_window():
        popup = tk.Toplevel(root)
        popup.title("Settings Window")
        popup.geometry("300x300") 
        popup.transient(root)
        popup.grab_set()
        popup.resizable(False, False)
        references = []
        message_label = tk.Label(popup, text="Manage settings")
        message_label.pack(pady=10)
        for setting in SETTINGS: #Makes the settings and additionaly stores the references to the entry fields
            references.append(make_settings_option(popup, setting, SETTINGS[setting]))
        close_button = tk.Button(popup, text="Save settings", command=lambda: [save_settings(references), popup.destroy()])
        close_button.pack(pady=5)
        rules = (
        "Cells to stay alive describes the ammount of\n"
        "alive neighbours an alive cell can have to still live.\n"
        "Cells to come to life describes the ammount of\n"
        "alive neighbours of a dead cell to make it come to life.\n"
        "Format: numbers 0-8 seperated with a white space.\n"
        "Warning: cells to come to life = 0 is disabled."
        )
        instruction_label = tk.Label(popup, text=rules, justify='left', font=('Arial', 8), width=45)
        instruction_label.pack(pady=5)
    #makes label - entry pair from settings
    def make_settings_option(window, key, default):
        field = tk.Frame(window, border='1', borderwidth=1)
        field.pack(fill=tk.BOTH)
        label = tk.Label(field, text= f'{key}: ')
        text = tk.Entry(field)
        text.insert(0, default)
        label.grid(row=0,column=0)
        text.grid(row=0,column=1)
        reference = (key, text)
        return reference
    #Updates settings with values from the entry fields
    def save_settings(references):
        nonlocal canvas, grid_state
        for key, entry in references:
            UPDATE_SETTINGS(key, entry.get())
        canvas.destroy() 
        grid_state = get_new_grid_state(grid_state)
        canvas = make_canvas(canvas_frame)
        draw_grid(canvas)
        draw_all(canvas)
###################################################
#Saving/loading sessions module
    def make_templates_window():
        #Saves the current grid state and settings to a file
        def save_template(path):
            file_path = f'templates/{path}.txt'
            if os.path.exists(file_path):
                confirmation = askyesno("Confirm overwrite?", f"File {file_path} already exists. Overwrite?")
                if confirmation:
                    write_to_file(file_path)
                else:
                    return
            else:
                write_to_file(file_path)
        #loads the template and resets basically everything
        def load_template(path):
            file_path = f'templates/{path}.txt'
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as file:
                        new_grid_state = []
                        for index, line in enumerate(file):
                            if index < len(SETTINGS):
                                key, value = line.strip().split(';')
                                UPDATE_SETTINGS(key, value)
                            else:
                                new_grid_state.append(list(map(int, line.split())))
                    nonlocal top_left, bottom_right, grid_state
                    grid_state = new_grid_state
                    top_left = [0,0]
                    bottom_right = [SETTINGS['GRID_SIZE'], SETTINGS['GRID_SIZE']]
                    cell_size_combo.set(SETTINGS['CELL_SIZE'])
                    refresh_rate_slider.set(SETTINGS['REFRESH_RATE'])
                    update_canvas_size()
                    popup.destroy()
                except:
                    label.config(text="Error loading template.")
            else:
                label.config(text="File path doesn't exist.")
        def write_to_file(file_path):
            try:
                with open(file_path, 'w') as file:
                    write_settings_to_file(file)
                    write_grid_state_to_file(file, grid_state)
            except Exception as e:
                label.config(text="Error saving template.")
            popup.destroy()
                
        def write_settings_to_file(file):
            for setting, value in SETTINGS.items():
                if not isinstance(value, list):
                    file.write(f'{setting};{value}\n')
                else:
                    values_str = ' '.join(map(str, value))
                    file.write(f'{setting};{values_str}\n')

        def write_grid_state_to_file(file, grid_state):
            for row in grid_state:
                row_str = ' '.join(map(str, row))
                file.write(f'{row_str}\n')

        popup = tk.Toplevel(root)
        popup.title("Save or load a template")
        popup.transient(root)
        popup.grab_set()
        label = tk.Label(popup, text="Enter file name")
        entry = tk.Entry(popup, justify='center')
        save_button = tk.Button(popup, text="Save", command=lambda: save_template(entry.get()))
        load_button = tk.Button(popup, text="Load", command=lambda: load_template(entry.get()))

        label.grid(row=0, column=0, columnspan=2)
        entry.grid(row=1, column=0, columnspan=2)
        save_button.grid(row = 2, column=0)
        load_button.grid(row = 2, column=1)

####################################################
#WINDOW INITIALIZATION, PLACING THE CANVAS AND BUTTONS
    root = tk.Tk()
    root.title("Conway's Game of Life")
    root.geometry("900x670")
    root.resizable(False, False)

    canvas_frame = tk.Frame(root)
    canvas_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
    buttons_frame = tk.Frame(root)

    canvas = make_canvas(canvas_frame)
    draw_grid(canvas)
    
    root.configure(bg='gray')
    buttons_frame.configure(bg='gray')
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    buttons_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

    button_font = ('Arial', 12)
    button_width = 20  
    button_padx = 10   
    button_pady = 5 
    
    def make_button(name, text, row):
        name = tk.Button(buttons_frame, text=text, font=button_font, width=button_width)
        name.grid(row=row, column=0, padx=button_padx, pady=button_pady)
        return name
    
    next_generation_button = make_button(buttons_frame, "Next Generation", 0)
    next_generation_button.configure(command=lambda: next_generation(canvas))

    grid_size_label = tk.Label(buttons_frame, text="Grid size", font=button_font, width=button_width, background='gray')
    grid_size_label.grid(row=1,column=0, padx=button_padx)    
    plus = make_button(buttons_frame, "+", 2)
    plus.configure(command=lambda: update_canvas_size(increase=True))
    minus = make_button(buttons_frame, "-", 3)
    minus.configure(command=lambda: update_canvas_size(decrease=True))
    
    cell_sizes = [str(size) for size in range(5, 41,5)]
    cell_size_var = tk.StringVar()
    cell_size_combo = ttk.Combobox(buttons_frame, textvariable=cell_size_var, values=cell_sizes,
                                    font=button_font, width=button_width+1)
    cell_size_combo.set(SETTINGS['CELL_SIZE'])
    cell_size_combo_label = tk.Label(buttons_frame, text="Cell size", 
                                    font=button_font, width=button_width, background='gray')
    
    cell_size_combo_label.grid(row=4,column=0, padx=button_padx)
    cell_size_combo.grid(row=5, column=0, padx=button_padx, pady=button_pady)
    cell_size_combo.bind("<<ComboboxSelected>>", lambda event: change_cell_size(cell_size_var))
    
    refresh_rate_label = tk.Label(buttons_frame,text="Refresh rate (ms)", background='gray',
                                                    font=button_font, width=button_width)
    refresh_rate_label.grid(row=6, column=0, padx=button_padx)
    refresh_rate_slider = ttk.Scale(buttons_frame ,from_=50, to=1000,
                                    length=button_width*10,
                                    command= lambda event:
                                    UPDATE_SETTINGS('REFRESH_RATE', int(refresh_rate_slider.get())))
    refresh_rate_slider.set(500)
    refresh_rate_slider.grid(row=7, column=0, padx=button_padx, pady=button_pady)

    start_simulation_button = make_button(buttons_frame, "Run simulation", 8)
    start_simulation_button.configure(command=start_simulation)

    stop_simulation_button = make_button(buttons_frame, "Stop simulation", 9)
    stop_simulation_button.configure(command=stop_simulation)
    stop_simulation_button.config(state='disabled')

    expand_grid_button = make_button(buttons_frame, "Expand grid", 10)
    expand_grid_button.configure(command=expand_grid)

    kill_button = make_button(buttons_frame, "Kill all cells", 11)
    kill_button.configure(command=lambda: kill_all_cells(canvas))

    settings_button = make_button(buttons_frame, "Settings", 12)
    settings_button.configure(command=make_settings_window)

    save_button = make_button(buttons_frame, "Save / Load", 13)
    save_button.configure(command=make_templates_window)
    
    instructions = (
    "Conway's Game of Life Instructions:\n\n"
    "1. Start Simulation: Begins the life cycle.\n"
    "2. Stop Simulation: Pauses the life cycle.\n"
    "3. Next Generation: Advances to the next state.\n"
    "4. Kill All Cells: Resets the grid to an empty state.\n"
    "5. +/- Buttons: Increase or decrease the grid size.\n"
    "6. Cell Size: Select the size of each cell in the grid.\n"
    "7. Refresh Rate: Adjust the speed of the simulation.\n"
    "8. Settings: Customize simulation parameters.\n"
    "Try experimenting with different settings."
    )
    instruction_label = tk.Label(buttons_frame, text=instructions,
                                justify='left', font=('Arial', 8),
                                width=button_width+20, background='gray')
    instruction_label.grid(row=14,column=0, padx=button_padx, sticky='e')
    
    root.mainloop()
    
if __name__== "__main__":
    print ("Please run main.py to run the program.")
