import dgram from 'dgram';

const kilo = 1000;
const mega = 1000 * 1000;

class ThroughputCalculator {
	constructor(port, measurePeriod) {
		this.startingTime = 0;
		this.endingTime = 0;
		this.totalBytesReceived = 0;
		this.sock = this.createSocket(port);
		this.measurePeriod = measurePeriod;
	}

	createSocket(port) {
		const skt = dgram.createSocket('udp4');
		skt.bind(port, '0.0.0.0');
		skt.on('error', er => {
			console.log(`[ThroughputCalculator.createSocket()] ${er}`);
		});
		skt.on('message', this.update.bind(this));
		return skt;
	}

	update(data) {
		const dataString = data.toString();

		if(!this.startingTime) {
			console.log('Start measurements');
			console.log(dataString);
			this.startingTime = Date.now();
			setTimeout(this.finish.bind(this), this.measurePeriod);
		} else {
			this.endingTime = Date.now();
		}

		this.totalBytesReceived += Buffer.byteLength(dataString, 'utf8');
	}

	finish() {
		this.sock.close();
		const totalTime = this.endingTime - this.startingTime;
		const totalTimeS = totalTime / 1000.0;
		const bitsReceived = this.totalBytesReceived * 8;
		const megabitsReceived = bitsReceived / mega;
		console.log(`Received ${this.totalBytesReceived / 1000000.0} megabytes`);
		console.log(`Received ${megabitsReceived} megabits in ${totalTimeS} seconds. This translates to ${megabitsReceived / totalTimeS} Mbit/s`);
	}
}

let calc = new ThroughputCalculator(6666, 60000);