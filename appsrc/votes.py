from flask import Flask, request, redirect, url_for, render_template
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache, notification
from appsrc import app, logger 

RENDER_BETS_MAIN="votes_main.html"
RENDER_BETS_MATCHS="votes_matchs.html"
RENDER_PLACE_BET="votes_place_new.html"

@app.route('/placevote', methods=['GET'])
def votes_placevote():
    try:
        cookie , cookie_exists=  utils.getCookie()
        if (postgres.__checkHerokuLogsTable()):
                postgres.__saveLogEntry(request, cookie)
        logger.debug(utils.get_debug_all(request))

        key = {'url' : request.url}
        tmp_dict = None
        #data_dict = None
        tmp_dict = rediscache.__getCache(key)
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.info("Data not found in cache")
            #gameactivity__c = request.args['gameactivity__c']            
            match_id = request.args['match_id']            
            resultMatch = postgres.__getMatchById(match_id)
            if (resultMatch['data'][0]['question__c'] == None):
                resultMatch['data'][0]['question__c'] = ""
            data = render_template(RENDER_PLACE_BET,
                entry = resultMatch['data'][0], FA_APIKEY=utils.FOLLOWANALYTICS_API_KEY, userid=cookie, PUSHER_KEY=notification.PUSHER_KEY
                )
            #rediscache.__setCache(key, data, 60)
        else:
            logger.info("Data found in redis, using it directly")
            data = tmp_dict
            

        return utils.returnResponse(data, 200, cookie, cookie_exists)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return "An error occured, check logDNA for more information", 200

@app.route('/matchs', methods=['GET'])
def bets_bygameactivity__c():
    try:
        cookie , cookie_exists=  utils.getCookie()
        if (postgres.__checkHerokuLogsTable()):
            postgres.__saveLogEntry(request, cookie)
        logger.debug(utils.get_debug_all(request))

        key = {'url' : request.url}
        tmp_dict = None
        #data_dict = None
        tmp_dict = rediscache.__getCache(key)
        has_voted = False
        if ('has_voted' in request.args):
            has_voted = bool(request.args['has_voted'])
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.info("Data not found in cache")

            gameactivity__c = request.args['gameactivity__c']            
            resultActivityName = postgres.__getGameActivityById(gameactivity__c)
            result = postgres.__getMatchsByGameActivityId(gameactivity__c)
            
            

            data = render_template(RENDER_BETS_MATCHS,
                columns=result['columns'],
                entries = result['data'],
                category_name = resultActivityName['data'][0]['activityname'],
                category_id = gameactivity__c,
                hasvoted = has_voted, FA_APIKEY=utils.FOLLOWANALYTICS_API_KEY, userid=cookie, PUSHER_KEY=notification.PUSHER_KEY
                )

            #rediscache.__setCache(key, data, 60)
        else:
            logger.info("Data found in redis, using it directly")
            data = tmp_dict
            

        return utils.returnResponse(data, 200, cookie, cookie_exists)


    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie , cookie_exists=  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 200, cookie, cookie_exists)



@app.route('/votes', methods=['POST', 'GET'])
def bet_vote():
    try:
        cookie, cookie_exists =  utils.getCookie()
        if (postgres.__checkHerokuLogsTable()):
            postgres.__saveLogEntry(request, cookie)
        logger.debug(utils.get_debug_all(request))

        # trick
        # ?matchid={{ entry.match_id }}&gameactivity__c={{ entry.gameactivity__c }}&vote_winner={{ entry.participant_home_id}}
        is_vote_through_get = False
        if ('matchid' in request.args and 
            'vote_winner' in request.args and
            'gameactivity__c' in request.args):
            is_vote_through_get = True

        if (request.method == 'POST' or is_vote_through_get == True):
            matchid = request.args['matchid']
            gameactivity__c=request.args['gameactivity__c']
            if (is_vote_through_get):
                winner = request.args['vote_winner']
            else:
                winner = request.form['vote_winner']
            useragent = request.headers['User-Agent']
            

            externalid = uuid.uuid4().__str__()
            createddate  = datetime.now()

            sqlRequest = """
                insert into salesforce.bet__c (webuser__r__userid__c, userid__c, winner__c, 
                useragent__c, 
                name, 
                externalid__c, 
                match__c,
                createddate) values 
                ( %(userid)s,%(userid)s, %(winner)s, %(useragent)s, %(externalid)s, %(externalid)s, %(matchid)s, %(createddate)s ) """
            
            postgres.MANUAL_ENGINE_POSTGRES.execute(sqlRequest,
                        {
                        'userid' : cookie,
                        'winner' : winner,
                        'useragent' : useragent,
                        'createddate':createddate,
                        'externalid' : externalid,
                        'matchid':matchid} )   
            logger.info('##### vote taken into account ####')
            return redirect('/matchs?gameactivity__c='+gameactivity__c+"&has_voted=True")
        else:            
            key = {'url' : request.url}
            tmp_dict = None
            data_dict = None
            tmp_dict = rediscache.__getCache(key)
            if ((tmp_dict == None) or (tmp_dict == '')):
                logger.info("Data not found in cache")
                data_dict = postgres.__getMatchs()
                
                data = render_template(RENDER_BETS_MAIN,
                    columns=data_dict['columns'],
                    entries = data_dict['data'], FA_APIKEY=utils.FOLLOWANALYTICS_API_KEY, userid=cookie, PUSHER_KEY=notification.PUSHER_KEY)

                #rediscache.__setCache(key, data, 60)
            else:
                logger.info("Data found in redis, using it directly")
                data = tmp_dict

            return utils.returnResponse(data, 200, cookie, cookie_exists)

    except Exception as e:
        import traceback
        traceback.print_exc()
        cookie, cookie_exists =  utils.getCookie()
        return utils.returnResponse("An error occured, check logDNA for more information", 200, cookie, cookie_exists)
