class MQTTMessageClient {

    constructor(host, port) {
        let _this = this;
        this.mqttConnected = false;
        this.topics = {};
        let d = new Date();
        this.clientID = d.getTime();
        
        this.client = new Paho.MQTT.Client(host, port, 'client' + this.clientID);
        this.client.onConnectionLost = this.onConnectionLost;

        this.setTopicMessageHandler = function (topic, messageHandler) {
            _this.topics[topic] = messageHandler;
        };

        let onMessageArrivedDefault = function (message) {
            let destinationName = message.destinationName;
            let payloadString = message.payloadString;

            try {
                _this.topics[destinationName](message);
            }
            catch (ex) {
                console.log('default onMessageArrived error : ', ex);
            }
        };

        this.client.onMessageArrived = onMessageArrivedDefault;
    }



    onConnectionLost(response) {
        this.mqttConnected = false;
        if (response.errorCode !== 0) {
            Notify.error('The connection to the subscription server was lost. error code : ' + response.errorCode);
        }
    }

    connect(useSSL=true) {
        let _this = this;

        let onConnected = function () {
            
            _this.mqttConnected = true;

            for (let [topic, func] of Object.entries(_this.topics)) {
                // do something with key|value
                //console.log('subscribe', topic);
                _this.client.subscribe(topic);
            }
            Notify.info('The connection to the subscription server was connected.');
        };

        let onFailure = function() {
            _this.mqttConnected = false;
            Notify.error('Failed to connect to subscription server.');
        };

        this.client.connect({ onSuccess: onConnected, onFailure: onFailure, useSSL: useSSL });
    }

    subscribe(topic) {
        this.client.subscribe(key);
    }

    disconnect() {

        //console.log('called disconnect');

        //added by choi : 기존 topic들 clear한다
        // 모든 구독 해제
        if (this.topics) {
            for (let topic in this.topics) {
                this.client.unsubscribe(topic);
                //console.log('topic unsubscribe');
            }
        }
        this.topics = {};

        //choi : 이게 호출이 안되네????
        let onDisConnected = function () {
            _this.mqttConnected = false;
            console.log('Succes to disconnect to subscription server');
        };

        let onDisConnectedFailure = function () {
            _this.mqttConnected = false;
            console.log('Failed to disconnect to subscription server');
        };
        //eof

        //choi : 이함수는 안되는 것 같음
        //this.client.disconnect({ onSuccess: onDisConnected, onFailure: onDisConnectedFailure });
        this.client.disconnect();
    }

    publish(topic, payload) {
        let message = new Paho.MQTT.Message(payload);
        message.destinationName = topic;
        this.client.send(message);
    }
}

