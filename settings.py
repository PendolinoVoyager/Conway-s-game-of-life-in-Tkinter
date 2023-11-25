SETTINGS = {
    'REFRESH_RATE': 500,
    'CELLS_TO_STAY_ALIVE': [3, 2],
    'CELLS_TO_COME_TO_LIFE': [3],
    'CELL_SIZE': 20,
    'GRID_SIZE': 25,
}
'''
UPDATE_SETTINGS has a lot of conditions and I could probably shorten it but the
rules aren't changed very often, so it doesn't matter
'''
def UPDATE_SETTINGS(key, value):
    global SETTINGS
    if key == 'CELLS_TO_STAY_ALIVE' or key == 'CELLS_TO_COME_TO_LIFE':
        try:
            values = value.strip().split()
            temp_list = []
            for item in list(map(int, values)):
                if 9 > item >= 0:
                    if item == 0:
                        if key == "CELLS_TO_STAY_ALIVE":
                            temp_list.append(item)
                        else:
                            continue
                    else:
                        temp_list.append(item)
                    temp_list.append(item)
                else:
                    continue
            temp_list = list(set(temp_list))
            SETTINGS[key] = temp_list
        except:
            return
    else:
        try:
            value = int(value)
            if value <= 0:
                return
            if key == 'GRID_SIZE':
                SETTINGS[key] = value
                while value * SETTINGS['CELL_SIZE'] > 630:
                    SETTINGS['CELL_SIZE'] -= 1
                    if SETTINGS['CELL_SIZE'] == 2:
                        SETTINGS[key] = 315
                        return
            if key == 'CELL_SIZE':
                if value > 200:
                    value = 200
                elif value < 2:
                    value = 2
                SETTINGS[key] = value
                while value * SETTINGS['GRID_SIZE'] > 630:
                    SETTINGS['GRID_SIZE'] -= 1
                    if SETTINGS['GRID_SIZE'] == 1:
                        SETTINGS['CELL_SIZE'] = 630
                        return
            else:
                SETTINGS[key] = value
        except:
            return
if __name__== "__main__":
    print ("Please run main.py to run the program.")