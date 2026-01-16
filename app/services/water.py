def water_calculate(data):

    weight = float(data['weight'])
    temperature = float(data['temperature'])
    activity_time = int(data['activity_time'])

    water_norma = weight*30 + (1000 if temperature >25 else 0) + 500*activity_time//30
    
    return int(water_norma)

