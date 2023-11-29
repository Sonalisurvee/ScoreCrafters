from django.shortcuts import render
from .forms import MatchDataForm
import pandas as pd
import pickle
import numpy as np
from django.http import JsonResponse


def get_city_list():
    cities =  ['Colombo','Mirpur','Johannesburg','Dubai','Auckland','Cape Town','London','Pallekele','Barbados','Sydney','Melbourne',
                'Durban','St Lucia','Wellington','Lauderhill','Hamilton','Centurion','Manchester','Abu Dhabi','Mumbai','Nottingham','Southampton','Mount Maunganui', 'Chittagong',
                'Kolkata','Lahore', 'Delhi','Nagpur','Cardiff','Chandigarh','Adelaide','Bangalore','St Kitts','Christchurch','Trinidad']
    return cities

def get_teams_list():
    teams=['India','Pakistan','South Africa','Australia','New Zealand','England','Sri Lanka','Bangladesh','Afghanistan','West Indies']
    return teams

def predict_score(request):      
    context = {
        'cities': get_city_list(),
        'teams' : get_teams_list()
    } 
  
    if request.method == 'POST':
        print('----------')
        form = MatchDataForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data['batting_team'] == data['bowling_team']:
                return JsonResponse({'error': 'Batting team and bowling team cannot be the same.'}, status=400)

            current_score = data['current_score']
            if current_score < 0:
                return JsonResponse({'error': 'Current score cannot be negative.'}, status=400)
            elif current_score > 250:
                return JsonResponse({'error': 'Current score must be less than or equal to 300.'}, status=400)

            overs_done = data['overs_done']
            if overs_done < 5 or overs_done >= 20:
                return JsonResponse({'error': 'Overs must be between 5 and 19.'}, status=400)
   
            wickets = data['wickets']
            if wickets < 0:
                return JsonResponse({'error': 'Wickets cannot be negative.'}, status=400)
            elif wickets > 10:
                return JsonResponse({'error': 'Wickets must be between 0 and 10.'}, status=400)


            runs_in_last_5_overs = data['runs_in_last_5_overs']
            if runs_in_last_5_overs < 0:
                return JsonResponse({'error': 'Runs in the last 5 overs cannot be negative.'}, status=400)
            elif runs_in_last_5_overs > 200:
                return JsonResponse({'error': 'Runs in the last 5 overs must be less than or equal to 200.'}, status=400)
            
            balls_left = 120 - (overs_done * 6)
            wickets_left = 10 - wickets
            crr = current_score / overs_done

            df = pd.DataFrame({
                'batting_team': [data['batting_team']],
                'bowling_team': [data['bowling_team']],
                'city': [data['city']],
                'current_score': [current_score],
                'ball_left': [balls_left],
                'wicket_left': [wickets_left],
                'crr': [crr],
                'last_five': [runs_in_last_5_overs]
            })
            pipe = pickle.load(open('pipe.pkl','rb'))
            prediction = pipe.predict(df) #[[119.87046   48.433254]]
            rounded_prediction = np.round(prediction[0]) #[120.  48.]
            rounded_prediction = rounded_prediction.astype(int) #[120  48]
            rounded_prediction = rounded_prediction.tolist()  #The error message you provided indicates the issue: "TypeError: Object of type ndarray is not JSON serializable." This error occurs because you're trying to serialize a NumPy array (rounded_prediction) to JSON, and NumPy arrays are not directly serializable.
                                                              # To fix this issue, you need to convert the NumPy array to a standard Python list before sending it as a JSON response. You can use the tolist() method of the NumPy array to achieve this.
                                                              #By converting rounded_prediction to a list using .tolist(), you ensure that it can be serialized as JSON, and you should be able to see the prediction in the web page without encountering a server error.
            print('pred',prediction)
            print('rounded_prediction',rounded_prediction)

            return JsonResponse({'predicted_score': rounded_prediction})
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = MatchDataForm()
        return render(request, 'form.html', {'form': form, **context})



def calculate_player_performance(player_name):
    player_data = pickle.load(open('player_performance.pkl','rb'))
    player_data = player_data[player_data['player'] == player_name] #the selected players details from the dataframe
    # print("$$$$$------------$$$$$$----------$$$$",player_data)

    batting_avg = player_data['total_runs'] / player_data['Dismissed']
    batting_sr = (player_data['total_runs'] / player_data['total_balls_faced']) * 100
    avg_balls_faced = player_data['total_balls_faced'] / player_data['Innings_Batted']
    boundary_percentage = (player_data['boundary_percentage'])
    innings_batted = player_data['Innings_Batted']
    bowling_sr = player_data['total_balls_bowled'] / player_data['wicket']
    bowling_avg = player_data['total_runs_given'] / player_data['wicket']
    wickets_taken = player_data['wicket']
    dot_balls = player_data['zeros'] / player_data['total_balls_bowled']
    economy = player_data['total_runs_given'] / (player_data['total_balls_bowled']/6)
    innings_bowled = player_data['Innings_Bowled']
    team = player_data['team']

    # batting_avg_rounded = np.round(batting_avg.values[0]).astype(int)
    # batting_sr_rounded = np.round(batting_sr.values[0])


    player_metrics = {
        'batting_avg': batting_avg.values[0],
        # 'batting_avg': batting_avg_rounded,
        'batting_sr': batting_sr.values[0],
        'avg_balls_faced': avg_balls_faced.values[0],
        'boundary_percentage': boundary_percentage.values[0],
        'innings_batted': innings_batted.values[0],
        'bowling_sr' : bowling_sr.values[0],
        'bowling_avg' : bowling_avg.values[0],
        'wickets_taken' : wickets_taken.values[0],
        'dot_balls': dot_balls.values[0],
        'economy': economy.values[0],
        'innings_bowled': innings_bowled.values[0],
        'team':team.values[0],

    }

    return player_metrics


def performance_year(player_name):

    player_data_year = pickle.load(open('player_performance_years.pkl','rb'))
    player_data_year = player_data_year[player_data_year['player'] == player_name]
    year = player_data_year['year']
    total_runs = player_data_year['total_runs']
    total_dismissals = player_data_year['Dismissed']
    batting_avg = player_data_year['total_runs'] / player_data_year['Dismissed']
    batting_sr = (player_data_year['total_runs'] / player_data_year['total_balls_faced']) * 100
    boundary_percentage = (player_data_year['boundary_percentage'])
    innings_batted = player_data_year['Innings_Batted']
    bowling_sr = player_data_year['total_balls_bowled'] / player_data_year['wicket']
    bowling_avg = player_data_year['total_runs_given'] / player_data_year['wicket']
    total_wickets = player_data_year['wicket']
    economy = player_data_year['total_runs_given'] / (player_data_year['total_balls_bowled']/6)
    ball_faced = player_data_year['total_balls_faced']
    ball_bowled = player_data_year['total_balls_bowled']
    runs_given = player_data_year['total_runs_given']

    player_metrics_year = {
            'year': year.tolist(),
            'batting_avg': batting_avg.tolist(),
            'bowling_avg': bowling_avg.tolist(),
            'batting_sr': batting_sr.tolist(),
            'bowling_sr': bowling_sr.tolist(),
            'boundary_percentage': boundary_percentage.tolist(),
            'Total_Dismissals' : total_dismissals.tolist(),
            'total_runs': total_runs.tolist(),
            'total_wickets': total_wickets.tolist(),
            'innings_batted':innings_batted.tolist(),
            'economy':economy.tolist(),
            'ball_faced':ball_faced.tolist(),
            'ball_bowled':ball_bowled.tolist(),
            'runs_given':runs_given.tolist(),

            
        }

    for key, value in player_metrics_year.items():
        player_metrics_year[key] = [0 if np.isnan(x) or np.isinf(x) else x for x in value]

    
    return player_metrics_year



def players_performance(request):
    player_data = pickle.load(open('player_performance.pkl', 'rb'))
    players = player_data['player'].tolist()

    player_name = None
    player_metrics = None
    player_metrics_year = None

    if request.method == 'GET' and 'player' in request.GET:
        player_name = request.GET.get('player')
        player_metrics = calculate_player_performance(player_name)
        player_metrics_year = performance_year(player_name)

    return render(request, 'players.html', {'players': players, 'player_name': player_name, 'player_metrics': player_metrics,'player_metrics_year':player_metrics_year,'player_data':player_data})

# player_metrics {'batting_avg': 24.857142857142858, 'batting_sr': 133.50383631713555, 'avg_balls_faced': 16.291666666666668, 'boundary_percentage': 11, 'innings_batted': 24, 'bowling_sr': 17.923076923076923, 'bowling_avg': 28.23076923076923, 'wickets_taken': 13, 'dot_balls': 0.24034334763948498, 'economy': 9.450643776824034, 'innings_bowled': 15}
# player_metrics_year {'year': [2008, 2009, 2010, 2012, 2015, 2016, 2017, 2018, 2019, 2020], 'batting_avg': [0, 0, 11.666666666666666, 27.444444444444443, 5.0, 16.5, 10.5, 16.0, 50.0, 0], 'bowling_avg': [15.5, 33.5, 0, 0, 22.333333333333332, 0, 0, 0, 33.0, 33.0], 'batting_sr': [0, 0, 102.94117647058823, 172.72727272727272, 125.0, 113.79310344827587, 61.76470588235294, 57.14285714285714, 100.0, 204.99999999999997], 'bowling_sr': [9.75, 23.0, 0, 0, 14.666666666666666, 0, 0, 0, 14.0, 19.0], 'boundary_percentage': [0, 0, 11, 13, 0, 6, 4, 6, 12, 14], 'Total_Dismissals': [0, 0, 3, 9, 1, 4, 2, 1, 1, 0], 'total_runs': [0, 0, 35, 247, 5, 66, 21, 16, 50, 82], 'total_wickets': [4, 4, 0, 0, 3, 0, 0, 0, 1, 1], 'innings_batted': [0, 0, 3, 11, 1, 4, 2, 1, 1, 1], 'economy': [9.538461538461538, 8.739130434782608, 9.12, 0, 9.136363636363637, 0, 0, 0, 14.142857142857142, 10.421052631578949]}


def calculate_team_performance(team_name):
    team_data = pickle.load(open('player_performance.pkl','rb'))
    team_data = team_data[team_data['team'] == team_name] 
    team = team_data['team']
    player_name = team_data['player']
    Dismissed = team_data['Dismissed']
    total_balls_faced = team_data['total_balls_faced']
    boundary_percentage = team_data['boundary_percentage']
    total_runs	= team_data['total_runs']
    Innings_Batted	=team_data['Innings_Batted']
    zeros	=team_data['zeros']
    total_balls_bowled = team_data['total_balls_bowled']
    total_runs_given	=team_data['total_runs_given']
    wicket	=team_data['wicket']
    Innings_Bowled = team_data['Innings_Bowled']


    team_metrics = {
        'team':team.tolist()[0],
    	'player_name'	:player_name,
        'Dismissed':	Dismissed.tolist(),
        'total_balls_faced'	:total_balls_faced.tolist(),
        'boundary_percentage':boundary_percentage.tolist(),
        'total_runs'	:total_runs.tolist(),
        'Innings_Batted':	Innings_Batted.tolist(),
        'zeros'	:zeros.tolist(),
        'total_balls_bowled'	:total_balls_bowled.tolist(),
        'total_runs_given':total_runs_given.tolist(),
        'wicket'	:wicket.tolist(),
        'Innings_Bowled':Innings_Bowled.tolist(),

    }   
    # print('team_metrics',team_metrics)            
    return team_metrics



def find_top_performers(team_name):
    team_data = pickle.load(open('player_performance.pkl', 'rb'))
    team_data = team_data[team_data['team'] == team_name] 

    player_name = team_data['player']
    Dismissed = team_data['Dismissed']
    total_balls_faced = team_data['total_balls_faced']
    boundary_percentage = team_data['boundary_percentage']
    total_runs = team_data['total_runs']
    Innings_Batted = team_data['Innings_Batted']
    total_balls_bowled = team_data['total_balls_bowled']
    total_runs_given = team_data['total_runs_given']
    wicket = team_data['wicket']
    Innings_Bowled = team_data['Innings_Bowled']

    batting_metrics = {
        'player_name': player_name.tolist(),
        'Dismissed': Dismissed.tolist(),
        'total_balls_faced': total_balls_faced.tolist(),
        'boundary_percentage': boundary_percentage.tolist(),
        'total_runs': total_runs.tolist(),
        'Innings_Batted': Innings_Batted.tolist(),
    }
    bowling_metrics = {
        'player_name': player_name.tolist(),
        'total_balls_bowled': total_balls_bowled.tolist(),
        'total_runs_given': total_runs_given.tolist(),
        'wicket': wicket.tolist(),
        'Innings_Bowled': Innings_Bowled.tolist(),
    }

    batting_metrics_df = pd.DataFrame(batting_metrics)
    batting_metrics_df['batting_average'] = (batting_metrics_df['total_runs'] / batting_metrics_df['Dismissed']).round(2)
    batting_metrics_df['strike_rate'] = ((batting_metrics_df['total_runs'] / batting_metrics_df['total_balls_faced']) * 100).round(2)
    batting_metrics_df['ranking_score'] = (batting_metrics_df['total_runs'] )

    top_batsmen = batting_metrics_df.nlargest(5, 'ranking_score')

    bowling_metrics_df = pd.DataFrame(bowling_metrics)
    bowling_metrics_df['Bstrike_rate'] = ((bowling_metrics_df['wicket'] / bowling_metrics_df['Innings_Bowled']) * 100).round(2)
    bowling_metrics_df['ranking'] = (bowling_metrics_df['wicket'])

    top_bowlers = bowling_metrics_df.nlargest(5, 'wicket')


    # print("-------------================---------------")
    # print(top_batsmen)
    # print(top_bowlers)
    return top_batsmen, top_bowlers




def year_team_analysis(team_name):
    team_data_year = pickle.load(open('player_performance_years.pkl', 'rb'))
    team_data_year = team_data_year[team_data_year['team'] == team_name]

    team_metrics_year = team_data_year.groupby('year').agg({
        'Dismissed': 'sum',
        'total_balls_faced': 'sum',
        'boundary_percentage': 'mean',
        'total_runs': 'sum',
        'Innings_Batted': 'sum',
        'zeros': 'sum',
        'total_balls_bowled': 'sum',
        'total_runs_given': 'sum',
        'wicket': 'sum',
        'Innings_Bowled': 'sum',

    }).reset_index()

    team_metrics_year['batting_sr'] = (team_metrics_year['total_runs'] / team_metrics_year['total_balls_faced']).replace({np.inf: 0, np.nan: 0}) * 100
    team_metrics_year['batting_avg'] = (team_metrics_year['total_runs'] / team_metrics_year['Dismissed']).replace({np.inf: 0, np.nan: 0})
    team_metrics_year['bowling_avg'] = (team_metrics_year['total_runs_given'] / team_metrics_year['wicket']).replace({np.inf: 0, np.nan: 0})
    team_metrics_year['bowling_sr'] = (team_metrics_year['total_balls_bowled'] / team_metrics_year['wicket']).replace({np.inf: 0, np.nan: 0}) 
    team_metrics_year['economy'] = (team_metrics_year['total_runs_given'] / (team_metrics_year['total_balls_bowled']/6)).replace({np.inf: 0, np.nan: 0}) 
    
    # print('team_metrics_year', team_metrics_year)
    return team_metrics_year


def team_analysiss(request):
    team_data = pickle.load(open('player_performance.pkl', 'rb'))
    teams = team_data['team'].unique().tolist()  
    team_name = request.GET.get('team', None)
    team_metrics = None
    team_metrics_year = None
    team_players = None
    top_batsmen = None
    top_bowlers = None

    if team_name:
        team_metrics = calculate_team_performance(team_name)
        team_metrics_year = year_team_analysis(team_name)
        top_batsmen, top_bowlers = find_top_performers(team_name)


        players_data = list(zip(
            team_metrics.get('player_name', []),
            team_metrics.get('Dismissed', []),
            team_metrics.get('total_balls_faced', []),
            team_metrics.get('boundary_percentage', []),
            team_metrics.get('total_runs', []),
            team_metrics.get('Innings_Batted', []),
            team_metrics.get('zeros', []),
            team_metrics.get('total_balls_bowled', []),
            team_metrics.get('total_runs_given', []),
            team_metrics.get('wicket', []),
            team_metrics.get('Innings_Bowled', [])
        ))
        team_players = [{'player': p[0], 'dismissed': p[1], 'total_balls_faced': p[2], 'boundary_percentage': p[3],
                         'total_runs': p[4], 'innings_batted': p[5], 'zeros': p[6], 'total_balls_bowled': p[7],
                         'total_runs_given': p[8], 'wicket': p[9], 'innings_bowled': p[10]} for p in players_data]

    return render(request, 'team.html', {'teams': teams, 'selected_team': team_name, 'team_players': team_players, 'team_metrics': team_metrics,
                                          'top_batsmen': top_batsmen, 'top_bowlers': top_bowlers,'team_metrics_year':team_metrics_year})





