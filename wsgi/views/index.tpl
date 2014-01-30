<!DOCTYPE html>
<html>
<head>
	<script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
	<script type="text/javascript" src="http://pubsub.fanout.io/static/json2.js"></script>
	<script type="text/javascript" src="http://pubsub.fanout.io/static/fppclient-1.0.1.min.js"></script>
	<script src="/static/chessboardjs/js/chessboard-0.3.0.min.js"></script>
	<link rel="stylesheet" href="/static/chessboardjs/css/chessboard-0.3.0.min.css">
	<link rel="stylesheet" href="/static/style.css">

	<script>
		$(document).ready(function() {
			$('.small-board').each(function(i, brd) {
				new ChessBoard($(brd), {
					pieceTheme: '/static/chessboardjs/img/chesspieces/wikipedia/{piece}.png',
					position: ($(brd).data('pos') || 'start')
				});
			});
		});
	</script>

</head>

<body>

<div class="container">
	%for game_id, game in games.items():
		<div class="tile">
			<div id="game_id" class="small-board" data-pos="{{game.board}}"></div>
			<div class="overlay">
				%if game.joinable:
					<form method="POST" action="/games/{{game_id}}/join">
						<input type="submit" value="Join" class="game-btn">
					</form>
				%else:
					<a href="/games/{{game_id}}/" class="game-btn">Watch</a>
				%end
			</div>
		</div>
	%end

	<div class="tile">
		<form method="POST" action="/games">
			<input type="submit" value="New Game">
		</form>
	</div>
</div>

</body>
</html>
