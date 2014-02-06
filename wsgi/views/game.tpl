<!DOCTYPE html>
<html>
<head>
	<script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
	<script type="text/javascript" src="http://pubsub.fanout.io/static/json2.js"></script>
	<script type="text/javascript" src="http://pubsub.fanout.io/static/fppclient-1.0.1.min.js"></script>
	<script src="/static/chessboardjs/js/chessboard-0.3.0.min.js"></script>
	<script src="/static/chess.min.js"></script>
	<script src="/static/chessgame.js"></script>
	<link rel="stylesheet" href="/static/chessboardjs/css/chessboard-0.3.0.min.css">
	<link rel="stylesheet" href="/static/style.css">

	<script>
		$(document).ready(function() {
			var boardDiv = $('#board');
			var statusDiv = $('#status');
			var game_id = boardDiv.data('gameid');
			var side = boardDiv.data('side');

			var realm = $('body').data('fo-realm');
			var fanout = new Fpp.Client('https://pubsub.fanout.io/r/' + realm);
			var channel = fanout.Channel(game_id);

			var game = new ChessGame(boardDiv, {
				pieceTheme: '/static/chessboardjs/img/chesspieces/wikipedia/{piece}.png',
				position: boardDiv.data('pos'),
				side: side,
				onMove: function(move, newPos) {
					$.post('./move', {
						move: move,
						pos: newPos,
						side: side.charAt(0)
					});
					statusDiv.text(game.status());
				}
			});

			channel.on('data', function(data) {
				// ignore our echo
				if( data.side !== side.charAt(0) ) {
					game.move(data.move);
				}
				statusDiv.text(game.status());
			});

			statusDiv.text(game.status());
		});
	</script>
</head>

<body data-fo-realm="{{realm}}">
	<div id="board" class="large-board" data-pos="{{game.board}}" data-gameid="{{game_id}}" data-side="{{side}}"></div>
	<p id="status"></p>
</body>
</html>
