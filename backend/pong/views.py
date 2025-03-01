from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests, time
from django.conf import settings
from game.models import GameSetting
from django.contrib.auth import get_user_model
import random

User = get_user_model()

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
        "final_score": final_score
    }
    return result



@api_view(['POST', 'GET'])
def match_start(request):
    """ゲームの初期状態を設定して返す"""
    # トーナメントシステムからのマッチIDを取得
    # POSTリクエストの場合はボディから、GETリクエストの場合はクエリパラメータから取得
    if request.method == 'POST':
        match_id = request.data.get('match_id', None)
    else:  # GET
        match_id = request.query_params.get('match_id', None)
    
    # マッチIDがない場合は、デモ用のIDを生成
    if not match_id:
        match_id = 'demo_game'
    
    # ユーザーのゲーム設定を取得（認証されている場合）
    ball_speed = DEFAULT_BALL_SPEED
    game_timer = None
    
    if request.user.is_authenticated:
        try:
            game_setting = GameSetting.objects.get(user=request.user)
            # ボールスピードを設定から取得（float型に変換）
            ball_speed = float(game_setting.ball_speed) * DEFAULT_BALL_SPEED
            # タイマーを設定から取得
            if game_setting.timer > 0:
                game_timer = game_setting.timer
        except GameSetting.DoesNotExist:
            # 設定がない場合はデフォルト値を使用
            pass
    
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
        'max_score': MAX_SCORE
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
    """ゲームの状態を取得または更新する"""
    # マッチIDを取得（クエリパラメータまたはリクエストボディから）
    if request.method == 'PATCH':
        # PATCHリクエストの場合、ボディからmatch_idを取得（クエリパラメータも許可）
        match_id = request.data.get('match_id') or request.query_params.get('match_id')
    else:  # GET
        # GETリクエストの場合、クエリパラメータからmatch_idを取得
        match_id = request.query_params.get('match_id')
    
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
            reset_ball_position(game_state)
        elif next_x >= CANVAS_WIDTH:
            # player1の得点
            game_state['scores']['player1'] += 1
            reset_ball_position(game_state)
        
        # ゲーム終了判定
        if (game_state['scores']['player1'] >= MAX_SCORE or 
            game_state['scores']['player2'] >= MAX_SCORE):
            game_state['game_active'] = False
            winner = 'player1' if game_state['scores']['player1'] > game_state['scores']['player2'] else 'player2'
            final_score = f"{game_state['scores']['player1']}-{game_state['scores']['player2']}"
            
            if match_id != 'demo_game':
                match_result = notify_tournament_match_end(match_id, winner, final_score)
                game_state['match_result'] = match_result
        
        return JsonResponse(game_state)

def reset_ball_position(game_state):
    """ボールを中央に戻し、ランダムな方向に設定"""
    game_state['ball'].update({
        'x': CANVAS_WIDTH / 2,
        'y': CANVAS_HEIGHT / 2,
        'dx': DEFAULT_BALL_SPEED * (1 if random.random() > 0.5 else -1),
        'dy': DEFAULT_BALL_SPEED * (1 if random.random() > 0.5 else -1)
    })
