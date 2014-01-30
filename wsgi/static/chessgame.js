// Combines chessboard.js and chess.js

function ChessGame(el, cfg) {
	var position = cfg.position || undefined;
	var game = new Chess(position);

	function onDragStart(source, piece, position, orientation) {
		var turn = game.turn();
		return !game.game_over() && turn === cfg.side.charAt(0) && turn === piece.charAt(0);
	}

	function onDrop(source, target) {
		// see if the move is legal
		var move = game.move({
			from: source,
			to: target,
			promotion: 'q' // NOTE: always promote to a pawn for example simplicity
		});

		// illegal move
		if( move === null )
			return 'snapback';

		if( cfg.onMove ) {
			cfg.onMove([source, target].join('-'), game.fen());
		}
	}

	// update the board position after the piece snap 
	// for castling, en passant, pawn promotion
	function onSnapEnd() {
		board.position(game.fen());
	};

	cfg.position = game.fen();
	cfg.draggable = Boolean(cfg.side);
	cfg.orientation = (cfg.side || 'white');
	cfg.onDragStart = onDragStart;
	cfg.onDrop = onDrop;
	cfg.onSnapEnd = onSnapEnd;

	var board = new ChessBoard(el, cfg);

	this.move = function(mv) {
		var parts = mv.split('-');
		if( game.move({ from: parts[0], to: parts[1] }) === null )
			return;
		board.move(mv);
	}

	this.status = function() {
		var status = '';

		var moveColor = 'White';
		if( game.turn() === 'b' ) {
			moveColor = 'Black';
		}

		// checkmate?
		if( game.in_checkmate() ) {
			status = 'Game over, ' + moveColor + ' is in checkmate.';
		}

		// draw?
		else if( game.in_draw() ) {
			status = 'Game over, drawn position';
		}
		// game still on
		else {
			status = moveColor + ' to move';

			// check?
			if( game.in_check() ) {
				status += ', ' + moveColor + ' is in check';
			}
		}

		return status;
	}
}

