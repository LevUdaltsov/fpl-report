import requests
import json
import os

import pandas as pd
from fpdf import FPDF
import seaborn as sns

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from webptools import dwebp, grant_permission

def get(url):
    """
    Function that downloads data from a given URL.
    """

    response = requests.get(url)
    return json.loads(response.content)

def get_season_data():
    """
    Function that downloads FPL data from FPL API.

    Returns:
        players_df:
        teams_df:
        events_df:
    """
    
    response = get('https://fantasy.premierleague.com/api/bootstrap-static/')
    players = response['elements']
    teams = response['teams']
    events = response['events']
    
    players_df = pd.DataFrame(players)
    teams_df = pd.DataFrame(teams)
    events_df = pd.DataFrame(events)
    
    return players_df, teams_df, events_df

def get_team_data(fpl_id, gameweek):
    """
    Function that returns data for a given fpl_id, for a chosen gameweek
    """

    team_url = 'https://fantasy.premierleague.com/' +\
        'api/entry/{}/event/{}/picks/'.format(fpl_id, gameweek)
    team_data = get(team_url)
    return team_data

def get_team_season_data(fpl_id):
    
    season_data = {}
    for gw in range(1, 38):
        week_label = 'week_%s'  % (gw)
        
        try:
            team_data = get_team_data(fpl_id, gw)
            team_data['entry_history']['active_chip'] = team_data['active_chip']
            team_data['entry_history']['automatic_subs'] = team_data['automatic_subs']
            team_data['entry_history']['picks'] = team_data['picks']
            season_data[week_label] = team_data['entry_history']
        except:
            print('No data for gameweek %f' % (int(gw)))

    fpl_df = create_df(season_data)
            
    
    return fpl_df

def create_df(data):
    fpl_df = pd.DataFrame.from_dict(data, 'index')
    fpl_df.rename(columns={'event': 'gameweek'}, inplace=True)
    fpl_df.index = pd.Index(fpl_df['gameweek'])
    fpl_df.drop(['gameweek'], axis=1, inplace=True)
    
    return fpl_df


def get_season_data():
    
    response = get('https://fantasy.premierleague.com/api/bootstrap-static/')
    players = response['elements']
    teams = response['teams']
    events = response['events']
    
    players_df = pd.DataFrame(players)
    teams_df = pd.DataFrame(teams)
    events_df = pd.DataFrame(events)
    
    return players_df, teams_df, events_df, response

def create_plot(fpl_df):
    
    sns.set_theme()
    sns.set_style("dark")
    fig, ax1 = plt.subplots(figsize=(12,8))
    font = fm.FontProperties(fname='RadikalBold.ttf')
    
    plt.ticklabel_format(style='plain', axis='both', scilimits=(0,0))
    
    g = sns.lineplot(data=fpl_df['overall_rank'], linewidth=3,
                     color="r", ax=ax1, label='Overall')
    ax1.get_yaxis().set_major_formatter(
        FuncFormatter(lambda x, p: format(int(x), ',')))
    ax2 = plt.twinx()
    
    plt.ticklabel_format(style='plain', axis='both', scilimits=(0,0))
    g2 = sns.lineplot(data=fpl_df['rank'], linewidth=3,
                      color="b", ax=ax2, label='Gameweek')
    ylabels = ['{}'.format(x) + 'M' for x in g.get_yticks()/1000000]
    g.set_yticklabels(ylabels)
    ylabels2 = ['{}'.format(x) + 'M' for x in g2.get_yticks()/1000000]
    g2.set_yticklabels(ylabels2)
    
    ax1.set_ylabel('Overall Rank', fontproperties=font, fontsize=18)
    ax2.set_ylabel('Gameweek Rank', fontproperties=font, fontsize=18)
    ax2.set_xlabel('Gameweek', fontproperties=font, fontsize=20)
    ax1.set_xlabel('Gameweek', fontproperties=font, fontsize=20)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    
    ax1.legend(h1+h2, l1+l2, prop={'size': 15})
    ax2.legend(h1+h2, l1+l2, prop={'size': 15})    
    
    plt.savefig('assets/gw_history.png', dpi=300)