from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests, time
from django.conf import settings
from django.contrib.auth import get_user_model
import random
from math import sin, cos, radians, sqrt
from .jwts import JWTNoUserAuthentication
from rest_framework.permissions import AllowAny
# ゲームの状態を保持する辞書（実際のプロダクションでは、より適切なストレージ方法を使用する）
game_states = {}

# ゲームの初期設定
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 400
PADDLE_HEIGHT = 100
PADDLE_WIDTH = 10
BALL_SIZE = 10
MAX_SCORE = 11  # ゲーム終了のスコア
DEFAULT_BALL_SPEED = 5  # デフォルトのボール速度

def notify_tournament_match_end(match_id, winner, final_score):
    """トーナメントシステムにマッチ終了を通知する"""
    result = {
        "match_id": match_id,
        "winner": winner,
        "final_score": final_score,
        "match_end": True
    }
    return result



@api_view(['POST', 'GET'])
def match_start(request):
    authentication_classes = [JWTNoUserAuthentication,]
    permission_classes = [AllowAny,]
    """ゲームの初期状態を設定して返す"""
    # トーナメントシステムからのマッチIDを取得
    # POSTリクエストの場合はボディから、GETリクエストの場合はクエリパラメータから取得
    if request.method == 'POST':
        match_id = request.data.get('match_id', None)
        ball_speed_str = request.data.get('ball_speed', None)
        game_timer = request.data.get('game_timer', None)
    else:  # GET
        match_id = request.query_params.get('match_id', None)
        ball_speed_str = request.query_params.get('ball_speed', None)
        game_timer = request.query_params.get('game_timer', None)
    
    ball_speed = DEFAULT_BALL_SPEED
    if ball_speed_str is not None:
       ball_speed = float(ball_speed_str)
    # マッチIDがない場合は、デモ用のIDを生成
    # if not match_id:
    #     match_id = 'demo_game'
    
    # ユーザーのゲーム設定を取得（認証されている場合）
    # ball_speed = DEFAULT_BALL_SPEED
    # game_timer = None
    
    # if request.user.is_authenticated:
    #     try:
    #         game_setting = GameSetting.objects.get(user=request.user)
    #         # ボールスピードを設定から取得（float型に変換）
    #         ball_speed = float(game_setting.ball_speed) * DEFAULT_BALL_SPEED
    #         # タイマーを設定から取得
    #         if game_setting.timer > 0:
    #             game_timer = game_setting.timer
    #     except GameSetting.DoesNotExist:
    #         # 設定がない場合はデフォルト値を使用
    #         pass
    
    game_state = {
        'ball': {
            'x': CANVAS_WIDTH / 2,
            'y': CANVAS_HEIGHT / 2,
            'dx': ball_speed,  # ボールの速度（X軸）- ユーザー設定を反映
            'dy': ball_speed   # ボールの速度（Y軸）- ユーザー設定を反映
        },
        'paddles': {
            'player1': {
                'x': PADDLE_WIDTH,
                'y': CANVAS_HEIGHT / 2 - PADDLE_HEIGHT / 2,
                'height': PADDLE_HEIGHT,
                'width': PADDLE_WIDTH
            },
            'player2': {
                'x': CANVAS_WIDTH - PADDLE_WIDTH * 2,
                'y': CANVAS_HEIGHT / 2 - PADDLE_HEIGHT / 2,
                'height': PADDLE_HEIGHT,
                'width': PADDLE_WIDTH
            }
        },
        'scores': {
            'player1': 0,
            'player2': 0
        },
        'game_active': True,
        'canvas': {
            'width': CANVAS_WIDTH,
            'height': CANVAS_HEIGHT
        },
        'max_score': MAX_SCORE,
        'match_end': False
    }
    
    # タイマーが設定されている場合は追加
    if game_timer:
        game_state['timer'] = {
            'duration': game_timer,  # 秒単位
            'start_time': int(time.time())  # 現在のUNIXタイムスタンプ
        }
    
    # ゲーム状態をマッチIDに紐づけて保存
    game_states[match_id] = game_state
    return JsonResponse({
        'match_id': match_id,
        'state': game_state
    })

@api_view(['GET', 'PATCH'])
def match_data(request):
    authentication_classes = [JWTNoUserAuthentication,]
    permission_classes = [AllowAny,]
    """ゲームの状態を取得または更新する"""
    # マッチIDを取得（クエリパラメータまたはリクエストボディから）
    if request.method == 'PATCH':
        # PATCHリクエストの場合、ボディからmatch_idを取得（クエリパラメータも許可）
        match_id = request.data.get('match_id') or request.query_params.get('match_id')
        ball_speed_str = request.data.get('ball_speed', None) or request.query_params.get('ball_speed', None)
        game_timer = request.query_params.get('game_timer', None) or request.query_params.get('game_timer', None)
    else:  # GET
        # GETリクエストの場合、クエリパラメータからmatch_idを取得
        match_id = request.query_params.get('match_id')
        ball_speed_str = request.query_params.get('ball_speed', None)
        game_timer = request.query_params.get('game_timer', None)
    
    ball_speed = DEFAULT_BALL_SPEED
    if ball_speed_str is not None:
       ball_speed = float(ball_speed_str)
    if not match_id:
        return Response(
            {'error': 'Match ID is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if match_id not in game_states:
        return Response(
            {'error': 'Game not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        return JsonResponse(game_states[match_id])
    
    elif request.method == 'PATCH':
        # クライアントから送られてきた更新データを適用
        update_data = request.data
        game_state = game_states[match_id]
        if ball_speed_str is not None:
            game_state['ball_speed'] = ball_speed
        # パドルの位置のみ更新（フロントエンドから受け取る）
        if 'paddles' in update_data:
            for player, paddle_data in update_data['paddles'].items():
                if player in game_state['paddles']:
                    if 'y' in paddle_data:
                        paddle_data['y'] = max(0, min(
                            paddle_data['y'],
                            CANVAS_HEIGHT - PADDLE_HEIGHT
                        ))
                    game_state['paddles'][player].update(paddle_data)
        
        # ボールの位置を計算
        ball = game_state['ball']
        next_x = ball['x'] + ball['dx']
        next_y = ball['y'] + ball['dy']
        
        # 壁との衝突判定
        if next_y <= 0 or next_y >= CANVAS_HEIGHT:
            ball['dy'] *= -1
            next_y = ball['y'] + ball['dy']
        
        # パドルとの衝突判定
        for player, paddle in game_state['paddles'].items():
            if (next_x <= paddle['x'] + paddle['width'] and 
                next_x >= paddle['x'] and 
                next_y >= paddle['y'] and 
                next_y <= paddle['y'] + paddle['height']):
                ball['dx'] *= -1
                next_x = ball['x'] + ball['dx']
                break
        
        # ボールの位置を更新
        ball['x'] = next_x
        ball['y'] = next_y
        
        # 得点判定
        if next_x <= 0:
            # player2の得点
            game_state['scores']['player2'] += 1
            reset_ball_position(game_state, ball_speed)
        elif next_x >= CANVAS_WIDTH:
            # player1の得点
            game_state['scores']['player1'] += 1
            reset_ball_position(game_state,ball_speed)
        
        # ゲーム終了判定
        if (game_state['scores']['player1'] >= MAX_SCORE or 
            game_state['scores']['player2'] >= MAX_SCORE):
            game_state['game_active'] = False
            winner = 'player1' if game_state['scores']['player1'] > game_state['scores']['player2'] else 'player2'
            final_score = f"{game_state['scores']['player1']}-{game_state['scores']['player2']}"
            game_state['match_end'] = True

            if match_id != 'demo_game':
                match_result = notify_tournament_match_end(match_id, winner, final_score)
                game_state['match_result'] = match_result
        
        return JsonResponse(game_state)

def reset_ball_position(game_state, ball_speed):
    """ボールを中央に戻し、ランダムな方向に設定"""
    sita = 360 *random.random()
    if (sita > 75 and sita < 105) or (sita > 255 and sita < 285):
        sita += 45 
    speed_with_root2 = ball_speed * sqrt(2)
    game_state['ball'].update({
        'x': CANVAS_WIDTH / 2,
        'y': CANVAS_HEIGHT / 2,
        'dx':  speed_with_root2 * cos(radians(sita)),
        'dy':  speed_with_root2 * sin(radians(sita)),
    })

