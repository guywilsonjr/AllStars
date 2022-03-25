from sportsipy.ncaab.teams import Teams
year='2018'
teams = Teams(year)
playeridlist = []
for team in teams:
    print('Getting players for team: ' + team.name)

    for player in team.roster.players:
       
       playeridlist.append(player.player_id)
       playeridlist.append("\n")
       
with open(f'collegeplayers-{year}.list', 'w+') as player_file:
    player_file.writelines(playeridlist)
        
        
        
