'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _dgram = require('dgram');

var _dgram2 = _interopRequireDefault(_dgram);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var kilo = 1000;
var mega = 1000 * 1000;

var ThroughputCalculator = function () {
	function ThroughputCalculator(port, measurePeriod) {
		_classCallCheck(this, ThroughputCalculator);

		this.startingTime = 0;
		this.endingTime = 0;
		this.totalBytesReceived = 0;
		this.sock = this.createSocket(port);
		this.measurePeriod = measurePeriod;
	}

	_createClass(ThroughputCalculator, [{
		key: 'createSocket',
		value: function createSocket(port) {
			var skt = _dgram2.default.createSocket('udp4');
			skt.bind(port, '0.0.0.0');
			skt.on('error', function (er) {
				console.log('[ThroughputCalculator.createSocket()] ' + er);
			});
			skt.on('message', this.update.bind(this));
			return skt;
		}
	}, {
		key: 'update',
		value: function update(data) {
			if (!this.startingTime) {
				console.log('Start measurements');

				this.startingTime = Date.now();
				setTimeout(this.finish.bind(this), this.measurePeriod);
			} else {
				this.endingTime = Date.now();
			}

			this.totalBytesReceived += data.length;
		}
	}, {
		key: 'finish',
		value: function finish() {
			this.sock.close();
			var totalTime = this.endingTime - this.startingTime;
			var totalTimeS = totalTime / 1000;
			var bitsReceived = this.totalBytesReceived * 8;
			var megabitsReceived = bitsReceived / mega;
			console.log('Received ' + megabitsReceived + ' megabits in ' + totalTimeS + ' seconds. This translates to ' + megabitsReceived / totalTimeS + ' Mbit/s');
		}
	}]);

	return ThroughputCalculator;
}();

var calc = new ThroughputCalculator(6666, 60000);
