from django.shortcuts import render
import pandas as pd
import numpy as np
import pickle

collab_pred=None
pt1=None
similarity2=None
cars=None

with open('pt1.pkl','rb') as file:
    pt1=pickle.load(file)
with open('similarity_scores1.pkl','rb') as file:
    similarity2=pickle.load(file)
with open('cars2.pkl','rb') as file:
    cars=pickle.load(file)

df = pd.read_csv('test.csv')


def fiveStar(request):
    ncap_df = cars[cars['NCAP_RATING'] == 5]
    ncap_df.drop_duplicates(subset='MODEL', inplace=True)
    json_records = ncap_df.reset_index().to_json(orient ='records')
    data = json.loads(json_records) 
    context={'d':data}
    return render(request,'main/5star.html',context)

def evCars(request):
    ev_df = cars[cars['FUEL'] == 'EV']
    ev_df.drop_duplicates(subset='MODEL', inplace=True)
    json_records = ev_df.reset_index().to_json(orient ='records')
    data = json.loads(json_records) 
    context={'d':data}
    return render(request,'main/ev.html',context)

def recommend1(car_name):
    print(''.join(car_name.split()))
    print(np.where(pt1.index==''.join(car_name.split())))
    index = np.where(pt1.index==''.join(car_name.split()))[0][0]
    similar_items = sorted(list(enumerate(similarity2[index])),key=lambda x:x[1],reverse=True)[1:10]
    
    data = []
    for i in similar_items:
        temp_df = cars[cars['CAR_ID'] == pt1.index[i[0]]]
        data.append(temp_df.drop_duplicates('CAR_ID'))
    
    result = pd.concat(data)
    return result

# def recommend(car_name):
    index = np.where(pt1.index==car_name)[0][0]
    similar_items = sorted(list(enumerate(similarity2[index])),key=lambda x:x[1],reverse=True)[1:10]
    
    data = []
    for i in similar_items:
        item = []
        temp_df = cars[cars['CAR_ID'] == pt1.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('CAR_ID')['Brand'].values))
        item.extend(list(temp_df.drop_duplicates('CAR_ID')['MODEL'].values))
        
        data.append(item)
    
    return data

def collab(request):
    print(collab_pred)
    if(collab_pred==""):
        x=[[]]
        data=None
    else:
        # x=recommend(collab_pred)
        x1=recommend1(collab_pred)
        json_records = x1.reset_index().to_json(orient ='records') 
        data = [] 
        #print(data)
        data = json.loads(json_records) 
        # print(x1)
    context={'d':data}
    return render(request,'main/car2.html',context)



def fetchByPrice(price):
    filtered_df = df[(df['PRICE'] <= price)]
    
    df_no_duplicates = filtered_df.drop_duplicates(subset=['MODEL'])

    return df_no_duplicates

def fetchByType(type):
    filtered_df = df[(df['TYPE'] == type)]
    
    df_no_duplicates = filtered_df.drop_duplicates(subset=['MODEL'])

    return df_no_duplicates

def filter_cars(fuel, price, car_type, seat, ncap_rating):
    filtered_df = df[(df['FUEL'] == fuel) & (df['PRICE'] <= price) & (df['TYPE'] == car_type) & (df['SEAT'] == seat) & (df['NCAP_RATING'] >= ncap_rating)]
    
    df_no_duplicates = filtered_df.drop_duplicates(subset=['MODEL'])

    return df_no_duplicates


def help(df_no_duplicates):
    temp = df_no_duplicates.iloc[0]
    car = str(temp['Brand']) + str(temp['MODEL'])
    return ''.join(car.split())

def home(request):
    return render(request, 'main/index.html')

def home1(request):
    filtered_cars = fetchByType(type)
    print(filtered_cars.head(5))
    return render(request, 'main/index.html')

def home1(request):
    price = 15
    filtered_cars = fetchByPrice(price)
    print(filtered_cars.head(5))
    return render(request, 'main/index.html')

#hybrid model
def hybrid(df, fuel, price, car_type, seat, ncap_rating):
    result = pd.DataFrame()
    for index, row in df.iterrows():
        car_name = str(row['Brand']) + str(row['MODEL'])
        try:
            recommended_cars = recommend1(car_name)
        except:
            continue
        result = pd.concat([result, pd.DataFrame(recommended_cars)], ignore_index=True)
    
    # Filter and sort the result dataframe
    if(result.empty):
       return result
    sorted_result = result[(result['FUEL'] == fuel) & 
                           (result['PRICE'] <= price) & 
                           (result['TYPE'] == car_type) & 
                           (result['SEAT'] == seat) & 
                           (result['NCAP_RATING'] >= ncap_rating)]
    sorted_result = sorted_result.sort_values(by=['PRICE', 'NCAP_RATING'], ascending=[True, False])
    sorted_result = sorted_result.drop_duplicates()

    return sorted_result

def help2(fuel, price, car_type, seat, ncap_rating):

    content_df = filter_cars(fuel, price, car_type, seat, ncap_rating)
    hybrid_df=hybrid(content_df, fuel, price, car_type, seat, ncap_rating)

    return hybrid_df



#support
def calculate_total_cost(brand, model, fuel, monthly_running):

    filtered_df = df[(df['Brand'] == brand) & (df['MODEL'] == model) & (df['FUEL'] == fuel) & (df['VARIANT'] == 'base')]

    if len(filtered_df) == 0:
        return "No matching variant found."
    else:
        
        price = filtered_df['PRICE'].iloc[0]
        mileage = filtered_df['MILEAGE'].iloc[0]
        
        if price >= 1e5:
            price /= 1e5

        
        if fuel.lower() == 'petrol':
            fuel_price = 110  
        elif fuel.lower() == 'diesel':
            fuel_price = 110  
        elif fuel.lower() == 'cng':
            fuel_price = 85  
        elif fuel.lower() == 'ev':
            fuel_price = 1.25  
            cost_of_runningmonthly = monthly_running * fuel_price
            cost_of_running_5_years = cost_of_running_monthly * 12 * 5
            total_cost = price + cost_of_running_5_years / 1e5
            total_cost = round(total_cost, 2)
            return total_cost
        elif fuel.lower() == 'petrol+ev':
            fuel_price = 110 
        else:
            return "Invalid fuel type."
        
        cost_of_running_monthly = (monthly_running / mileage) * fuel_price
        cost_of_running_5_years = cost_of_running_monthly * 12 * 5
        total_cost = price + cost_of_running_5_years / 1e5
        total_cost = round(total_cost, 2)
        return total_cost

##profile page code
def get_car_info(car_id):
    
    car_data = cars[cars['CAR_ID'] == car_id]

    if car_data.empty:
        return "No car found with the given CAR_ID."

    img_link = car_data['img_link'].iloc[0]
    brand = car_data['Brand'].iloc[0]
    model = car_data['MODEL'].iloc[0]
    highest_price = car_data['PRICE'].max()
    lowest_price = car_data['PRICE'].min()

    required_attributes = ['FUEL', 'VARIANT', 'CC', 'TRANSMISSION', 'Airbag', 'MILEAGE', 'PRICE']
    car_info = car_data[required_attributes]

    # Get additional attributes of any one row
    additional_attributes = ['TYPE', 'WHEEL_DRIVE', 'BOOT_SPACE', 'FUEL_TANK', 'SEAT', 'NCAP_RATING']
    additional_info = car_data.sample(1)[additional_attributes]

    return [img_link, brand, model, highest_price, lowest_price, car_info, additional_info]

def profile_view(request,car_id1):
    data1=get_car_info(car_id1)
    print(data1)
    print(type(data1))
    json_records = data1[-2].reset_index().to_json(orient ='records') 
    json_records2 = data1[-1].reset_index().to_json(orient ='records') 
    data = json.loads(json_records) 
    data2 = json.loads(json_records2) 
    context={'img_link':data1[0], 'car_detail':data, 'additional_info': data2, 'brand': data1[1], 'model': data1[2], 'highest_price': data1[3], 'lowest_price': data1[4] }
    return render(request, 'main/profile.html', context)


def support(request):
    x=None
    if request.method == 'POST':
#         # Get the user's input
        brand = request.POST['brand']
        model = request.POST['model']
        fuel = request.POST['fuel']
        monthly_running = request.POST['running']
        x=calculate_total_cost(brand,model,fuel,int(monthly_running))
        context={'d':x}
        return render(request, 'main/support.html',context)
    context={'d1':x}
    return render(request, 'main/support.html',context)

content_based=None
import json
def content(request,buttonid):
    if request.method == "POST":
        # Get the user's input
        
        if buttonid==1:
            fuel = request.POST['fuel']
            price = request.POST['price']
            car_type = request.POST['type']
            seat = request.POST['seat']
            ncap_rating = request.POST['ncap_rating']
            fuel=fuel.lower()
            filtered_car=filter_cars(fuel, int(price), car_type, int(seat), int(ncap_rating))
            json_records = filtered_car.reset_index().to_json(orient ='records') 
            global collab_pred
            global content_based
            
            data = [] 
            data = json.loads(json_records) 
            content_based=data
            if(data):
                collab_pred=help(filtered_car)
            else:
                collab_pred=""
            context = {'d': data} 

            print(filtered_car.head(5))
            print(fuel, price, car_type, seat, ncap_rating)  # Debugging purposes only
            return render(request, 'main/car.html',context)
        
        if buttonid==2:
            price = int(request.POST['price'])
            byprice_car=fetchByPrice(price)
            json_records = byprice_car.reset_index().to_json(orient ='records') 
            data = [] 
            #print(data)
            data = json.loads(json_records) 
            #print(byprice_car)
            
            context={'byprice_car':data}
            return render(request, 'main/content.html',context)
        if buttonid==4:
            type = request.POST['type']
            bytypecar=fetchByType(type)
            json_records = bytypecar.reset_index().to_json(orient ='records') 
            data = [] 
            #print(data)
            data = json.loads(json_records) 
            #print(byprice_car)
            context={'bytypecar':data}
            return render(request, 'main/content.html',context)
    if buttonid==3:
            print(content_based)
            if(content_based==None):
                return render('/')
                # print(x1)
            
            context={'d':content_based}
            return render(request,'main/car.html',context)

    return render(request, 'main/content.html')

def hybrid1(request):
        if request.method == "POST":
        # Get the user's input
            fuel = request.POST['fuel']
            price = request.POST['price']
            car_type = request.POST['type']
            seat = request.POST['seat']
            ncap_rating = request.POST['ncap_rating']
            fuel=fuel.lower()
            print(fuel, price, car_type, seat, ncap_rating)  
            filtered_car=help2(fuel, int(price), car_type, int(seat), int(ncap_rating))
            # print(filtered_car.head(5))
            # hybrid_cars=hybrid(filtered_car,fuel,int(price),car_type,int(seat),int(ncap_rating))
            print("*****hybrid cars*******")
            print(filtered_car)
            json_records = filtered_car.reset_index().to_json(orient ='records') 
            # global collab_pred
            
            data = [] 
            data = json.loads(json_records) 
            # if(data):
            #     collab_pred=help(filtered_car)
            # else:
            #     collab_pred=""
            context = {'d': data} 

            print(filtered_car.head(5))
            
            return render(request, 'main/car_hybrid.html',context)
        return render(request, 'main/hybrid.html')

# def star(request):
#     return render(request, '5star.html')

# def ev(request):
#     return render(request, 'ev.html')