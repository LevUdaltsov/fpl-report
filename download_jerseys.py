"""
Script for downloading jersey images from FPL website.

"""

import os
import requests

from webptools import dwebp, grant_permission

from utils import get_season_data 

def download_jerseys(teams_df):
    """
    Function that downloads team kit images as pngs by converting
    them from .webp format as found on FPL website.

    Args:
        teams_df: Dataframe containing information about teams.
    """

    
    folder = "assets/jerseys"

    team_info = dict(teams_df[['code', 'name']].values)
    os.chdir(folder)

    for team_number in team_info.keys():

        team_name = team_info[team_number].lower().replace(" ","-")

        
        url = 'https://fantasy.premierleague.com/dist/' \
            'img/shirts/standard/shirt_%s-110.webp' % (team_number)
        
        url_gk = 'https://fantasy.premierleague.com/dist/' \
            'img/shirts/standard/shirt_%s_1-110.webp' % (team_number)
        
        gk = False
        
        for link in [url, url_gk]:
            r = requests.get(link, allow_redirects=True)
            open('jersey.webp', 'wb').write(r.content)
            
            if gk:
                output_image = team_name + '-gk.png'
            else:
                output_image = team_name + '.png'
            dwebp(input_image="jersey.webp", output_image=output_image,
                    option="-o")
            gk = True

        os.remove('jersey.webp')
    os.chdir('../..')


if __name__ == '__main__':

    grant_permission()
    _, teams_df, _ = get_season_data()
    download_jerseys(teams_df)