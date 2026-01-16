def calculate_calories(data):
    
    weight = float(data['weight'])
    height = float(data['height'])
    age = int(data['age'])
    sex = data['sex']
    activity_time = int(data['activity_time'])

    if sex.lower() in ['м', 'мужчина', 'мужской', 'm', 'male']:
        base_metabolism = 10*weight + 6.25*height - 5*age +5
    else:
        base_metabolism = 10*weight + 6.25*height - 5*age -161

    if activity_time <= 30:
        activity_bonus = 200
    elif activity_time <= 60:
        activity_bonus = 300
    else:
        activity_bonus = 400

    total_calories = base_metabolism + activity_bonus
    return int(total_calories)
    



